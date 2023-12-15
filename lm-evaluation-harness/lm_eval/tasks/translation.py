"""
NOTE: This file implements translation tasks using datasets from WMT conferences,
provided by sacrebleu. Traditionally they are evaluated with BLEU scores. TER
and CHRF are other options.

We defer citations and descriptions of the many translations tasks used
here to the SacreBLEU repo from which we've obtained the datasets:
https://github.com/mjpost/sacrebleu/blob/master/sacrebleu/dataset.py

Homepage: https://github.com/mjpost/sacrebleu/blob/master/sacrebleu/dataset.py
"""
import pycountry
from pprint import pprint
from sacrebleu import sacrebleu
from lm_eval import metrics
from lm_eval.utils import remove_excess
from lm_eval.base import Task, rf
from typing import List
import string
import torch

# EDITS
import os
import itertools
from lm_eval.topicmodel import TopicModel
from bertopic import BERTopic
import random
os.environ["SACREBLEU"] = "/scratch/saycock/data/"
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

TOPIC_MODEL = None
verbose = False
ALL_LANGS = False
DOMAIN_RANDOM = False
SENT_SIM = False
SEEN = False

try:
    import nagisa

    HAS_NAGISA = True
except ImportError:
    HAS_NAGISA = False

try:
    import jieba

    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False


_CITATION = """
@inproceedings{post-2018-call,
    title = "A Call for Clarity in Reporting {BLEU} Scores",
    author = "Post, Matt",
    booktitle = "Proceedings of the Third Conference on Machine Translation: Research Papers",
    month = oct,
    year = "2018",
    address = "Belgium, Brussels",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/W18-6319",
    pages = "186--191",
}
"""


sacrebleu_datasets = sacrebleu.DATASETS


def create_tasks_from_benchmarks(benchmark_dict):
    """Creates a dictionary of tasks from a dict
    :param benchmark_dict: { dataset: [lang_pair, ...], }
    :return: {task_name: task}
        e.g. {wmt14-fr-en: Task, wmt16-de-en: Task}
    """

    def version_of(dataset, language_pair):
        if language_pair[-2:] in ["zh", "ja"]:
            return 1  # changed to use jieba/nagisa
        return 0

    return {
        f"{dataset}-{language_pair}": create_translation_task(
            dataset, language_pair, version_of(dataset, language_pair)
        )
        for dataset, language_pairs in benchmark_dict.items()
        for language_pair in language_pairs
    }


########################################
# Language Specifics
########################################


def zh_split(zh_text: List[str]) -> List[str]:
    """Chinese splitting"""
    if not HAS_JIEBA:
        raise ImportError(
            "Chinese text splitting requires the `jieba` package. "
            "Please install it with:\npip install jieba"
        )

    return [" ".join(jieba.cut(txt.strip())) for txt in zh_text]


def ja_split(ja_text: List[str]) -> List[str]:
    """Japanese splitting"""
    if not HAS_NAGISA:
        raise ImportError(
            "Japanese text splitting requires the `nagisa` package. "
            "Please install it with:\npip install nagisa"
        )

    return [" ".join(nagisa.tagging(txt.strip()).words) for txt in ja_text]


NO_SPACE_LANG = {"zh": zh_split, "ja": ja_split}

########################################
# Tasks
########################################


def create_translation_task(dataset, language_pair, version=0):
    class TranslationTask(GeneralTranslationTask):
        VERSION = version

        def __init__(self):
            super().__init__(dataset, language_pair)

    return TranslationTask


class GeneralTranslationTask(Task):
    VERSION = 0
    DATA_DIR = "/scratch/saycock/data/"
    TOPIC_DIR = "/scratch/saycock/topic/topicmodels/"

    # e.g. ("wmt14", "fr-en")
    def __init__(self, dataset, language_pair=None,):
        self.sacrebleu_dataset = dataset
        self.data_dir = self.DATA_DIR
        self.topic_dir = self.TOPIC_DIR
        self.sacrebleu_language_pair = language_pair
        self.src_file = self.ref_file = self.src_data = self.ref_data = None
        self.language_codes = self.sacrebleu_language_pair.split("-")
        self.train_src_file = self.train_trg_file = self.train_src_data = self.train_trg_data = None
        self.train_x_file = self.train_en_file = self.train_x_data = self.train_en_data = None

        # EDITS
        self.tm = None

        super().__init__()

    def download(self, data_dir=None, cache_dir=None, download_mode=None):
        # This caches in the users home dir automatically
        
        data_dir = self.data_dir

        reverse_list = self.sacrebleu_language_pair.split("-")
        reverse_pair = "-".join(reverse_list[::-1])

        if "wmt" in self.sacrebleu_dataset:
            self.src_file, self.ref_file = sacrebleu.download_test_set(
                self.sacrebleu_dataset, self.sacrebleu_language_pair
            )
        else:
            try:
                self.src_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + self.sacrebleu_language_pair + ".test." + self.language_codes[0]
                self.ref_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + self.sacrebleu_language_pair + ".test." + self.language_codes[1]

                self.src_data, self.ref_data = [
                    [line.rstrip() for line in sacrebleu.smart_open(file)]
                    for file in (self.src_file, self.ref_file)
                ]

            except FileNotFoundError:
                self.src_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + reverse_pair + ".test." + self.language_codes[0]
                self.ref_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + reverse_pair + ".test." + self.language_codes[1]       

                self.src_data, self.ref_data = [
                    [line.rstrip() for line in sacrebleu.smart_open(file)]
                    for file in (self.src_file, self.ref_file)
                ]

        # init topic model per dataset
        # TODO: optionally make topic model for all data
        # TODO: add option for topic model to combine source and ref sentences for in-context examples
        # self.tm = topic_model
        # _tm = self.tm.generate_model(langs=self.language_codes,
        #                             nr_topics=100,
        #                             n_docs=3,
        #                             samples=1000,
        #                             src_data = self.src_data,
        #                             ref_data = self.ref_data,
        #                             use_stops=False,
        #                             parallel=True)

        if TOPIC_MODEL:
            print(TOPIC_MODEL)
            # # wrapper class init
            self.tm = TopicModel()
            # # load in pretrained models
            self.tm.topic_model = BERTopic.load(self.topic_dir+TOPIC_MODEL)
            self.tm.path = self.topic_dir+TOPIC_MODEL


        domains = ["EMEA","JRC-Acquis","KDE4","OpenSubtitles","QED","Tanzil","TED2020","CCAligned"]
        langs = ["en", "fr", "lt", "fi", "ta", "ro", "cs", "de"]

        try:
            self.train_src_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + self.sacrebleu_language_pair + ".train." + self.language_codes[0]
            self.train_trg_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + self.sacrebleu_language_pair + ".train." + self.language_codes[1]

            self.train_src_data, self.train_trg_data = [
                [line.rstrip() for line in sacrebleu.smart_open(file)]
                for file in (self.train_src_file, self.train_trg_file)
            ]

        except FileNotFoundError:
            self.train_src_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + reverse_pair + ".train." + self.language_codes[0]
            self.train_trg_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + "." + reverse_pair + ".train." + self.language_codes[1]       

            self.train_src_data, self.train_trg_data = [
                [line.rstrip() for line in sacrebleu.smart_open(file)]
                for file in (self.train_src_file, self.train_trg_file)
                ]
            
        if SEEN:
            if ALL_LANGS:
                self.train_x_seen_file = data_dir + "seen-x.train.x"
                self.train_en_seen_file = data_dir + "seen-x.train.en"

                self.train_x_seen_data, self.train_en_seen_data = [
                    [line.rstrip() for line in sacrebleu.smart_open(file)]
                    for file in (self.train_x_seen_file, self.train_en_seen_file)
                ]
            else:
                if self.language_codes[0] == "en":
                    self.train_x_seen_file = data_dir + f"seen-{self.language_codes[1]}.train.{self.language_codes[1]}"
                    self.train_en_seen_file = data_dir + f"seen-{self.language_codes[1]}.train.en"
                else:
                    self.train_x_seen_file = data_dir + f"seen-{self.language_codes[0]}.train.{self.language_codes[0]}"
                    self.train_en_seen_file = data_dir + f"seen-{self.language_codes[0]}.train.en"

                self.train_x_seen_data, self.train_en_seen_data = [
                    [line.rstrip() for line in sacrebleu.smart_open(file)]
                    for file in (self.train_x_seen_file, self.train_en_seen_file)
                ]

        

        if DOMAIN_RANDOM:
            # one domain, all langs
            self.train_x_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + ".train.x"
            self.train_en_file = data_dir + self.sacrebleu_dataset + "/" + self.sacrebleu_dataset + ".train.en"

            self.train_x_data, self.train_en_data = [
                [line.rstrip() for line in sacrebleu.smart_open(file)]
                for file in (self.train_x_file, self.train_en_file)
            ]

        if not ALL_LANGS:
            # all domain, one lang pair
            if self.language_codes[0] == "en":
                self.alldom_x_file = data_dir + "all-" + self.language_codes[1] + ".train." + self.language_codes[1]
                self.alldom_en_file = data_dir + "all-" + self.language_codes[1] + ".train.en"
            if self.language_codes[1] == "en":
                self.alldom_x_file = data_dir + "all-" + self.language_codes[0] + ".train." + self.language_codes[0]
                self.alldom_en_file = data_dir + "all-" + self.language_codes[0] + ".train.en"
            
            self.alldom_train_x_data, self.alldom_train_en_data = [
                [line.rstrip() for line in sacrebleu.smart_open(file)]
                for file in (self.alldom_x_file, self.alldom_en_file)
            ]

        if ALL_LANGS and not SEEN:
            # all domains, all lang pairs (with en)
            self.all_x_file = data_dir + "all-x.train.x"
            self.all_en_file = data_dir + "all-en.train.en"

            self.all_x_data, self.all_en_data = [
                [line.rstrip() for line in sacrebleu.smart_open(file)]
                for file in (self.all_x_file, self.all_en_file)
            ]

        if SENT_SIM:
            if SEEN:
                if ALL_LANGS:
                    self.all_embeddings = model.encode(self.train_x_seen_data, convert_to_tensor=True)
                else:
                    self.lang_embeddings = model.encode(self.train_x_seen_data, convert_to_tensor=True)
            else:
                if ALL_LANGS:
                    self.all_embeddings = model.encode(self.all_x_data, convert_to_tensor=True)
                else:
                    self.lang_embeddings = model.encode(self.alldom_train_x_data, convert_to_tensor=True)

    def has_training_docs(self):
        """Whether the task has a training set"""
        # TODO In the future we could be more discerning. Some more recent tests have train and dev sets
        # TODO: Add training data functionality
        return False

    def has_validation_docs(self):
        """Whether the task has a validation set"""
        return False

    def has_test_docs(self):
        """Whether the task has a test set"""
        return True

    def test_docs(self):
        """
        :return: Iterable[obj]
            A iterable of any object, that doc_to_text can handle
        """
        return [
            {"src": src, "ref": ref} for src, ref in zip(self.src_data, self.ref_data)
        ]

    def doc_to_text(self, doc):
        language_codes = self.sacrebleu_language_pair.split("-")
        src_lang = code_to_language(language_codes[0])
        tar_lang = code_to_language(language_codes[1])

        # EDITS
        # Translate from {src_lang} to {tar_lang}.
        # {src_lang}: " + doc["src"] + f" = {tar_lang}:
        # Given the following source text in {src_lang}: \"{doc['src']}\", a good {tar_lang} translation is:
        text = f"{src_lang}: " + doc["src"] + f" = {tar_lang}:"
        if verbose:
            text = f"Given the following source text in {src_lang}: \"{doc['src']}\", a good {tar_lang} translation is:"
        return text

    def should_decontaminate(self):
        return True

    def doc_to_decontamination_query(self, doc):
        return doc["src"]

    def doc_to_target(self, doc):
        # This shows a single target, though there may be multiple targets in a lang test
        return " " + doc["ref"] if isinstance(doc["ref"], str) else doc["ref"][0]

    def construct_requests(self, doc, ctx):
        """Uses RequestFactory to construct Requests and returns an iterable of
        Requests which will be sent to the LM.

        :param doc:
            The document as returned from training_docs, validation_docs, or test_docs.
        :param ctx: str
            The context string, generated by fewshot_context. This includes the natural
            language description, as well as the few shot examples, and the question
            part of the document for `doc`.
        """
        return rf.greedy_until(ctx, {"until": ["\n"]})
        # return rf.greedy_until(ctx,  {"max_length": 64})
        # return rf.loglikelihood(ctx)

    def process_results(self, doc, results):
        # Add spaces between words for BLEU score calculation of target languages like Chinese
        tar_lang_code = self.sacrebleu_language_pair.split("-")[-1]
        if tar_lang_code in NO_SPACE_LANG:
            doc["ref"] = NO_SPACE_LANG[tar_lang_code]([doc["ref"]])[0]
            results = NO_SPACE_LANG[tar_lang_code](results)

        # These metrics are corpus-level not sentence level, so we'll hide the
        # results in this dict and compute the corpus score in the aggregate method
        # remove_excess goes here
        results = [res for res in results]

        ref_pred = (doc["ref"], results)
        src_ref_pred = (doc["src"], doc["ref"], results)

        return {
            "bleu": ref_pred,
            "chrf": ref_pred,
            # EDITS
            "comet": src_ref_pred
        }

    def aggregation(self):
        """
        :returns: {str: [float] -> float}
            A dictionary where keys are the names of submetrics and values are
            functions that aggregate a list of metrics
        """
        return {
            "bleu": metrics.bleu,
            "chrf": metrics.chrf,
            # EDITS
            "comet": metrics.comet22
        }

    def higher_is_better(self):
        """
        :returns: {str: bool}
            A dictionary where keys are the names of submetrics and values are
            whether a higher value of the submetric is 
        """
        return {
            "bleu": True,
            "chrf": True,
            # EDITS
            "comet": True
        }

    def __str__(self):
        language_codes = self.sacrebleu_language_pair.split("-")
        src_lang = code_to_language(language_codes[0])
        tar_lang = code_to_language(language_codes[1])
        return f"{self.sacrebleu_dataset.upper()} {src_lang} to {tar_lang} Task"

    def fewshot_context(
        self, doc, num_fewshot, provide_description=None, rnd=None, description=None,
        topic_keywords = False, rep_topics = False, no_topics=1, domain_label = False,
        randoms = False, domain_random = False, true_random = False, all_langs = False,
        bm25 = False, sent_sim = False, seen = False, top_n = False
    ):
        """Returns a fewshot context string that is made up of a prepended description
        (if provided), the `num_fewshot` number of examples, and an appended prompt example.

        :param doc: str
            The document as returned from training_docs, validation_docs, or test_docs.
        :param num_fewshot: int
            The number of fewshot examples to provide in the returned context string.
        :param provide_description: bool
            Not implemented, and this option is deprecated and will be removed in a future version in favor of a different description providing method
        :param rnd: random.Random
            The pseudo-random number generator used to randomly sample examples.
            WARNING: This is currently a required arg although it's optionalized with a default `None`.
        :param description: str
            The task's description that will be prepended to the fewshot examples.
        :returns: str
            The fewshot context.
        """
        assert (
            rnd is not None
        ), "A `random.Random` generator argument must be provided to `rnd`"
        assert not provide_description, (
            "The `provide_description` arg will be removed in future versions. To prepend "
            "a custom description to the context, supply the corresponding string via the "
            "`description` arg."
        )
        if provide_description is not None:
            # nudge people to not specify it at all
            print(
                "WARNING: provide_description is deprecated and will be removed in a future version in favor of description_dict"
            )

        description = description + "\n\n" if description else ""
        fewshotex = ""

        if domain_label:
            domain = self.sacrebleu_dataset
            domain_dict = {"EMEA": "EU biomedical texts",
                            "TED2020": "Public speaking transcripts",
                            "OpenSubtitles": "TV and movie subtitles",
                            "Tanzil": "Religious Quran text",
                            "QED": "Educational video transcripts",
                            "JRC-Acquis": "EU legislative texts",
                            "KDE4": "Software localization files",
                            "CCAligned": "General web text"}
            if randoms:
                key_list = list(domain_dict.keys())
                key_list.remove(domain)
                domain = random.choice(key_list)
            #  {domain}. Description: 
            fewshotex += f"Domain: {domain_dict[domain]}.\n"

        if num_fewshot == 0:
            pass
        else:
            # EDITS

            if topic_keywords:
                # best matching topics and probs for given sentence
                n = num_fewshot
                no_topics = num_fewshot
                if self.tm:
                    topics, probs = self.tm.closest_topics(doc["src"], n)
                    if no_topics == 1:
                        if randoms:
                            # topics_rand, probs_rand = self.tm.closest_topics(doc["src"], len(probs))
                            rand_topic = random.choice(range(len(self.tm.topics_test[0])))
                            # print(len(self.tm.topics_test), len(self.tm.topics_test[0]), len(topics[0]), len(topics))
                            # print(rand_topic)
                            # rand_topic = self.tm.topics_test[0][rand_topic]
                            keyword_text = ("Related keywords: " +
                                        ", ".join([keyword_tuple[0] for keyword_tuple in self.tm.topic_model.get_topics()[rand_topic]])  + ".\n"
                            )
                        
                            
                        else:
                            # TODO: add probability threshold - for sentence's topic probability, not word's prob of being in topic
                            top_topic = self.tm.topics_test[0][0]
                            keyword_text = ("Related keywords: " +
                                        ", ".join([keyword_tuple[0] for keyword_tuple in topics[0][top_topic] ])  + ".\n"
                            )
                            # if keyword_tuple[1] > 0.05
                    else:
                        assert n >= len(topics), "Requested more examples than available topics, please increase no. of closest topics"
                        top_topics = self.tm.topics_test[0][:n].tolist()

                        # get list of all keywords per n topics
                        all_keywords = [topics[0][no] for no in top_topics]
                        all_keywords = list(itertools.chain(*all_keywords))

                        # get list of probabilities per n topics
                        all_probs = [probs[0][c] for c, no in enumerate(top_topics)]

                        #TODO: DELETE THIS LINE AFTER KEY-3SHOT EXPERIMENTS!!
                        # top_topic = self.tm.topics_test[0][0]
                        # keyword_text = ("Related keywords: " +
                        #                 ", ".join([keyword_tuple[0] for keyword_tuple in topics[0][top_topic] ])  + ".\n"
                        #     )

                        # UNCOMMENT THIS FOR KEYWORDS30!!!
                        keyword_text = (f"Related keywords: " +
                                        ", ".join([keyword for (keyword, p) in all_keywords])  + ".\n"
                            )


                    fewshotex += keyword_text
            
            src_lang = code_to_language(self.language_codes[0])
            tar_lang = code_to_language(self.language_codes[1])
            
            if rep_topics:
                n = num_fewshot
                no_topics = num_fewshot
                if self.tm:
                    topics, probs = self.tm.closest_topics(doc["src"], n)
                    rep = self.tm.representative_topics()[0][:num_fewshot]
                    # list of sentences that represent topic
                    if randoms:
                        rand_topic = random.choice(range(len(self.tm.rep_docs))) - 1
                        # print(rand_topic)
                        # print(self.tm.rep_docs)
                        rep = self.tm.rep_docs[rand_topic][:num_fewshot]
                        # full_random = 0
                        # if full_random:
                        #     pass
                    if top_n:
                            top_topics = self.tm.topics_test[0][:n].tolist()
                            rep = [self.tm.rep_docs[x-1][0] for x in top_topics]
                            # print(top_topics, rep)

                    else:
                        rep = self.tm.representative_topics()[0][:num_fewshot]
                    # Representative sentences in the closest topic include:
                    if self.language_codes[1] == "en":
                        rep = [ " = ".join(r.split(" = ")[::-1]) for r in rep ]
                    
                    rep_text = (
                                "\n".join([r for r in rep]) + "\n"
                    )

                    fewshotex += rep_text
            
            if bm25:

                if seen:
                    range_value_pairs = {
                            (0, 19999): "Czech",
                            (20000, 39999): "German",
                            (40000, 59999): "Finnish",
                            (60000, 79999): "French",
                            (80000, 99000): "Lithuanian",
                            (100000, 119000): "Romanian",
                            (120000, 140000): "Tamil"
                        }

                else:
                    range_value_pairs = {
                            (0, 39999): "Czech",
                            (40000, 79999): "German",
                            (80000, 114999): "Finnish",
                            (115000, 154999): "French",
                            (155000, 189999): "Lithuanian",
                            (190000, 229999): "Romanian",
                            (230000, 259999): "Tamil"
                        }
                
                # ALL DOMAINS, ALL LANGS
                # self.all_x_data, self.all_en_data

                n = num_fewshot
                if all_langs:
                    # SEEN DOMAINS ONLY
                    if seen:
                        if self.language_codes[0] == "en":
                            srcdata = self.train_en_seen_data
                            trgdata = self.train_x_seen_data

                        if self.language_codes[1] == "en":
                            srcdata = self.train_x_seen_data
                            trgdata = self.train_en_seen_data
                    
                    # ALL DOMAINS
                    else:
                        if self.language_codes[0] == "en":
                            srcdata = self.all_en_data
                            trgdata = self.all_x_data

                        if self.language_codes[1] == "en":
                            srcdata = self.all_x_data
                            trgdata = self.all_en_data
                
                
                # ONE LANG
                else:
                    if seen:
                        if self.language_codes[0] == "en":
                            srcdata = self.train_en_seen_data
                            trgdata = self.train_x_seen_data

                        if self.language_codes[1] == "en":
                            srcdata = self.train_x_seen_data
                            trgdata = self.train_en_seen_data
                    else:
                        if self.language_codes[0] == "en":
                            srcdata = self.alldom_train_en_data
                            trgdata = self.alldom_train_x_data

                        if self.language_codes[1] == "en":
                            srcdata = self.alldom_train_x_data
                            trgdata = self.alldom_train_en_data

                # if all_langs:
                #     if self.language_codes[0] == "en":
                #         srcdata = self.all_en_data
                #         trgdata = self.all_x_data

                #     if self.language_codes[1] == "en":
                #         srcdata = self.all_x_data
                #         trgdata = self.all_en_data
                # # ONE LANG
                # else:
                #     if self.language_codes[0] == "en":
                #         srcdata = self.alldom_train_en_data
                #         trgdata = self.alldom_train_x_data

                #     if self.language_codes[1] == "en":
                #         srcdata = self.alldom_train_x_data
                #         trgdata = self.alldom_train_en_data

                tokenized_corpus = [sent.split() for sent in srcdata]
                bm = BM25Okapi(tokenized_corpus)

                query = doc["src"].split()
                results = bm.get_top_n(query, tokenized_corpus, n)

                detok_sents = [" ".join(d) for d in results]
                
                indices = [srcdata.index(x) for x in detok_sents]
                trg_sents = [trgdata[i] for i in indices]

                langs = []
                for index in indices:
                    for (start, end), lang in range_value_pairs.items():
                        if start <= index <= end:
                            langs.append(lang)
                            break
                if all_langs:
                    if self.language_codes[1] == "en":
                        examples = [f"{lang}: {detok_sents[c]} = English: {trg_sents[c]}" for c, lang in enumerate(langs)]
                    if self.language_codes[0] == "en":
                        examples = [f"English: {detok_sents[c]} = {lang}: {trg_sents[c]}" for c, lang in enumerate(langs)]
                else:
                    if self.language_codes[1] == "en":
                        examples = [f"{src_lang}: {detok_sents[c]} = English: {trg_sents[c]}" for c, i in enumerate(langs)]
                    if self.language_codes[0] == "en":
                        examples = [f"English: {detok_sents[c]} = {tar_lang}: {trg_sents[c]}" for c, i in enumerate(langs)]

                rep_text = (
                                "\n".join([r for r in examples]) + "\n"
                    )

                fewshotex += rep_text

            if sent_sim:
                
                if seen:
                    range_value_pairs = {
                            (0, 19999): "Czech",
                            (20000, 39999): "German",
                            (40000, 59999): "Finnish",
                            (60000, 79999): "French",
                            (80000, 99000): "Lithuanian",
                            (100000, 119000): "Romanian",
                            (120000, 140000): "Tamil"
                        }

                else:
                    range_value_pairs = {
                            (0, 39999): "Czech",
                            (40000, 79999): "German",
                            (80000, 114999): "Finnish",
                            (115000, 154999): "French",
                            (155000, 189999): "Lithuanian",
                            (190000, 229999): "Romanian",
                            (230000, 259999): "Tamil"
                        }
                
                # ALL DOMAINS, ALL LANGS
                # self.all_x_data, self.all_en_data

                n = num_fewshot
            
                if all_langs:
                    embeddings = self.all_embeddings

                    # SEEN DOMAINS ONLY
                    if seen:
                        if self.language_codes[0] == "en":
                            srcdata = self.train_en_seen_data
                            trgdata = self.train_x_seen_data

                        if self.language_codes[1] == "en":
                            srcdata = self.train_x_seen_data
                            trgdata = self.train_en_seen_data
                    
                    # ALL DOMAINS
                    else:
                        if self.language_codes[0] == "en":
                            srcdata = self.all_en_data
                            trgdata = self.all_x_data

                        if self.language_codes[1] == "en":
                            srcdata = self.all_x_data
                            trgdata = self.all_en_data
                
                
                # ONE LANG
                else:
                    embeddings = self.lang_embeddings
                    if seen:
                        if self.language_codes[0] == "en":
                            srcdata = self.train_en_seen_data
                            trgdata = self.train_x_seen_data

                        if self.language_codes[1] == "en":
                            srcdata = self.train_x_seen_data
                            trgdata = self.train_en_seen_data
                    else:
                        if self.language_codes[0] == "en":
                            srcdata = self.alldom_train_en_data
                            trgdata = self.alldom_train_x_data

                        if self.language_codes[1] == "en":
                            srcdata = self.alldom_train_x_data
                            trgdata = self.alldom_train_en_data

                
                test_embed = model.encode(doc["src"], convert_to_tensor=True)
                cosine_scores = util.cos_sim(test_embed, embeddings)
                scores_array = cosine_scores.cpu().numpy().flatten()
                top_indices = torch.topk(cosine_scores, n).indices
                # print(top_indices)
                # print(len(srcdata), len(self.all_en_data))
                top_sents = [srcdata[i] for i in top_indices[0]]

                # paraphrases = util.paraphrase_mining(model, srcdata)

                # query = doc["src"].split(" ")
                # results = bm.get_top_n(query, tokenized_corpus, n)

                # detok_sents = [" ".join(d) for d in results]
                
                # indices = [srcdata.index(x) for x in detok_sents]
                trg_sents = [trgdata[i] for i in top_indices[0]]

                langs = []
                for index in top_indices[0]:
                    for (start, end), lang in range_value_pairs.items():
                        if start <= index <= end:
                            langs.append(lang)
                            break
                if all_langs:
                    if self.language_codes[1] == "en":
                        examples = [f"{lang}: {top_sents[c]} = English: {trg_sents[c]}" for c, lang in enumerate(langs)]
                    if self.language_codes[0] == "en":
                        examples = [f"English: {top_sents[c]} = {lang}: {trg_sents[c]}" for c, lang in enumerate(langs)]
                else:
                    if self.language_codes[1] == "en":
                        examples = [f"{src_lang}: {top_sents[c]} = English: {trg_sents[c]}" for c, i in enumerate(langs)]
                    if self.language_codes[0] == "en":
                        examples = [f"English: {top_sents[c]} = {tar_lang}: {trg_sents[c]}" for c, i in enumerate(langs)]

                rep_text = (
                                "\n".join([r for r in examples]) + "\n"
                    )

                fewshotex += rep_text
                

            translator = str.maketrans('', '', string.punctuation)

            if num_fewshot and domain_random:

                range_value_pairs = {
                        (0, 4999): "Czech",
                        (5000, 9999): "German",
                        (10000, 14999): "Finnish",
                        (15000, 19999): "French",
                        (20000, 24999): "Lithuanian",
                        (25000, 29999): "Romanian",
                        (30000, 34999): "Tamil"
                    }

                if all_langs:
                    if self.language_codes[0] == "en":
                        self.train_src_data = self.train_en_data
                        self.train_trg_data = self.train_x_data
                    if self.language_codes[1] == "en":
                        self.train_src_data = self.train_x_data
                        self.train_trg_data = self.train_en_data
                    
                    
                    if rep_topics:
                    

                        indices = random.sample(range(len(self.train_src_data)), num_fewshot)

                        assigned_values = assign_values_to_indices(indices, range_value_pairs)

                        if self.language_codes[0] == "en":
                            selected = [f"{src_lang}: {self.train_src_data[i]} = {assigned_values[c]}: {self.train_trg_data[i]}" for c,i in enumerate(indices)]
                        if self.language_codes[1] == "en":
                            selected = [f"{assigned_values[c]}: {self.train_src_data[i]} = {tar_lang}: {self.train_trg_data[i]}" for c,i in enumerate(indices)]
                        text = ("\n".join([s for s in selected]) + "\n")
                        fewshotex += text
                
                    if topic_keywords:
                        src = [sentence.split() for sentence in self.train_src_data]
                        trg = [sentence.split() for sentence in self.train_trg_data]
                        flat_src = [word.translate(translator).lower() for sentence_words in src for word in sentence_words]
                        flat_trg = [word.translate(translator).lower() for sentence_words in trg for word in sentence_words]

                        selected_words = random.sample(flat_src, 5) + random.sample(flat_trg, 5)
                        random.shuffle(selected_words)
                        keyword_text = ("Related keywords: " +
                                    ", ".join([word for word in selected_words])  + ".\n"
                        )
                        fewshotex += keyword_text

                else:
                    assert len(self.train_src_data) == len(self.train_trg_data)
                    if rep_topics:
                        indices = random.sample(range(len(self.train_src_data)), num_fewshot)
                        selected = [f"{src_lang}: {self.train_src_data[i]} = {tar_lang}: {self.train_trg_data[i]}" for i in indices]
                        text = ("\n".join([s for s in selected]) + "\n")
                        fewshotex += text

                    if topic_keywords:
                        src = [sentence.split() for sentence in self.train_src_data]
                        trg = [sentence.split() for sentence in self.train_trg_data]
                        flat_src = [word.translate(translator).lower() for sentence_words in src for word in sentence_words]
                        flat_trg = [word.translate(translator).lower() for sentence_words in trg for word in sentence_words]

                        selected_words = random.sample(flat_src, 5) + random.sample(flat_trg, 5)
                        random.shuffle(selected_words)
                        keyword_text = ("Related keywords: " +
                                    ", ".join([word for word in selected_words])  + ".\n"
                        )
                        fewshotex += keyword_text

                
            if num_fewshot and true_random:

                # IMPLEMENT SEEN DOMAINS

                if all_langs:
                    
                    if seen:
                        range_value_pairs = {
                                (0, 19999): "Czech",
                                (20000, 39999): "German",
                                (40000, 59999): "Finnish",
                                (60000, 79999): "French",
                                (80000, 99000): "Lithuanian",
                                (100000, 119000): "Romanian",
                                (120000, 140000): "Tamil"
                            }
                    else:
                        range_value_pairs = {
                                (0, 39999): "Czech",
                                (40000, 79999): "German",
                                (80000, 114999): "Finnish",
                                (115000, 154999): "French",
                                (155000, 189999): "Lithuanian",
                                (190000, 229999): "Romanian",
                                (230000, 259999): "Tamil"
                            }
                    
                    if seen:
                        if self.language_codes[0] == "en":
                            self.train_src_data = self.train_en_seen_data
                            self.train_trg_data = self.train_x_seen_data

                        if self.language_codes[1] == "en":
                            self.train_src_data = self.train_x_seen_data
                            self.train_trg_data = self.train_en_seen_data
                    
                    # ALL DOMAINS
                    else:
                        if self.language_codes[0] == "en":
                            self.train_src_data = self.all_en_data
                            self.train_trg_data = self.all_x_data

                        if self.language_codes[1] == "en":
                            self.train_src_data = self.all_x_data
                            self.train_trg_data = self.all_en_data

                    # if self.language_codes[0] == "en":
                    #     self.train_src_data = self.all_en_data
                    #     self.train_trg_data = self.all_x_data
                    # if self.language_codes[1] == "en":
                    #     self.train_src_data = self.all_x_data
                    #     self.train_trg_data = self.all_en_data
                    
                    if rep_topics:

                        indices = random.sample(range(len(self.train_src_data)), num_fewshot)

                        assigned_values = assign_values_to_indices(indices, range_value_pairs)

                        if self.language_codes[0] == "en":
                            selected = [f"{src_lang}: {self.train_src_data[i]} = {assigned_values[c]}: {self.train_trg_data[i]}" for c,i in enumerate(indices)]
                        if self.language_codes[1] == "en":
                            selected = [f"{assigned_values[c]}: {self.train_src_data[i]} = {tar_lang}: {self.train_trg_data[i]}" for c,i in enumerate(indices)]
                        text = ("\n".join([s for s in selected]) + "\n")
                        fewshotex += text
                    
                    if topic_keywords:
                        src = [sentence.split() for sentence in self.train_src_data]
                        trg = [sentence.split() for sentence in self.train_trg_data]
                        flat_src = [word.translate(translator).lower() for sentence_words in src for word in sentence_words]
                        flat_trg = [word.translate(translator).lower() for sentence_words in trg for word in sentence_words]

                        selected_words = random.sample(flat_src, 5) + random.sample(flat_trg, 5)
                        random.shuffle(selected_words)
                        keyword_text = ("Related keywords: " +
                                    ", ".join([word for word in selected_words])  + ".\n"
                        )
                        fewshotex += keyword_text
                    
                else:
                    assert len(self.alldom_train_x_data) == len(self.alldom_train_en_data)
                    if self.language_codes[0] == "en":
                        self.train_src_data = self.alldom_train_en_data
                        self.train_trg_data = self.alldom_train_x_data
                    if self.language_codes[1] == "en":
                        self.train_src_data = self.alldom_train_x_data
                        self.train_trg_data = self.alldom_train_en_data

                    if rep_topics:
                        indices = random.sample(range(len(self.train_src_data)), num_fewshot)
                        selected = [f"{src_lang}: {self.train_src_data[i]} = {tar_lang}: {self.train_trg_data[i]}" for i in indices]
                        text = ("\n".join([s for s in selected]) + "\n")
                        fewshotex += text

                    if topic_keywords:
                        src = [sentence.split() for sentence in self.train_src_data]
                        trg = [sentence.split() for sentence in self.train_trg_data]
                        flat_src = [word.translate(translator).lower() for sentence_words in src for word in sentence_words]
                        flat_trg = [word.translate(translator).lower() for sentence_words in trg for word in sentence_words]

                        selected_words = random.sample(flat_src, 5) + random.sample(flat_trg, 5)
                        random.shuffle(selected_words)
                        keyword_text = ("Related keywords: " +
                                    ", ".join([word for word in selected_words])  + ".\n"
                        )
                        fewshotex += keyword_text


            # if num_fewshot and self.tm and not rep_topics and not topic_keywords:
            #     n = num_fewshot
            #     topics, probs = self.tm.closest_topics(doc["src"], n)
            #     # list of random parallel sentences
            #     unrel_top = random.sample(range(0,len(topics)), n)
                
            #     # select top sentence from random topic, for num_fewshot examples
            #     rep = [self.tm.representative_topics()[top][0] for top in unrel_top]
                
            #     rep_text = (
            #                 "\n".join([r for r in rep]) + "\n"
            #     )
                
                # no_topics = num_fewshot
                # topics, probs = self.tm.closest_topics(doc["src"], n)
                # # list of sentences that represent topic
                # rep = self.tm.representative_topics()[0]
                # # Representative sentences in the closest topic include:
                # rep_text = (
                #             "\n".join([r for r in rep])
                # )

                # fewshotex += rep_text



            # # for sets with no training docs, draw from other set *but ensure no overlap with current doc*
            # if self.has_training_docs():
            #     fewshotex = self.fewshot_examples(k=num_fewshot, rnd=rnd)
            # else:
            #     if self._fewshot_docs is None:
            #         self._fewshot_docs = list(
            #             self.validation_docs()
            #             if self.has_validation_docs()
            #             else self.test_docs()
            #         )

            #     fewshotex = rnd.sample(self._fewshot_docs, num_fewshot + 1)

            #     # get rid of the doc that's the one we're evaluating, if it's in the fewshot
            #     fewshotex = [x for x in fewshotex if x != doc][:num_fewshot]

        # labeled_examples = (
        #     "\n\n".join(
        #         [
        #             self.doc_to_text(doc) + self.doc_to_target(doc)
        #             for doc in fewshotex
        #         ]
        #     )
        #     + "\n\n"
        # )

        labeled_examples = fewshotex

        example = self.doc_to_text(doc)
        # print(example)

        return labeled_examples + example


########################################
# Util
########################################


def code_to_language(code):
    # key is alpha_2 or alpha_3 depending on the code length
    language_tuple = pycountry.languages.get(**{f"alpha_{len(code)}": code})
    return language_tuple.name


def assign_values_to_indices(indices, range_value_pairs):
    assigned_values = []
    for index in indices:
        assigned_value = None
        for (start, end), value in range_value_pairs.items():
            if start <= index <= end:
                assigned_value = value
                break
        assigned_values.append(assigned_value)
    return assigned_values