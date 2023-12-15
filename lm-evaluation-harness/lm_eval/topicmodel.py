import itertools
import bertopic
import numpy as np
import pandas as pd
import advertools as ads
from cuml.manifold import UMAP
from cuml.cluster import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired
import langcodes
import stopwordsiso
import json
import random

class TopicModel():
    def __init__(self, **kwargs):

        self.docs = []
        self.src_data = None
        self.ref_data = None
        self.langs = None
        self.domains = None
        self.stop_langs = None
        self.use_stops = None
        self.stops = None
        self.test_docs = None
        self.path = None

        self.n_docs = None
        self.samples = None

        self.embedding_model = None
        self.umap_model = None
        self.hdbscan_model = None
        self.vectorizer_model = None
        self.ctfidf_model = None
        self.representation_model = None
        self.topic_model = None

        self.topics, self.probs = None, None
        self.topics_test, self.probs_test = None, None
        self.top_n_idx = None
        self.top_n_probs = None

        self.top_n_topics = None
        self.rep_docs = None

        self.kwargs = kwargs

    def load_model(self, path:str=None):
        full_path = "/scratch/saycock/topic/topicmodels/" + path
        self.path = full_path
        self.topic_model = bertopic.BERTopic.load(full_path)
        return self.topic_model

    def generate_model(self, langs:list, domains:list, nr_topics:int=100,
                       n_docs:int = 5, samples:int = 1000, src_data=None, ref_data=None,
                       use_stops=False, parallel=False, **kwargs):
        
        self.langs = langs
        self.stop_langs = [langcodes.Language.get(lang).display_name().lower()
                            for lang in self.langs]
        if use_stops:
            self.stops = self._generate_stops()

        # TO DO - combine source and ref sentences
        if parallel:
            self.docs.extend([f"{self.stop_langs[0]}: {src} = {self.stop_langs[1]}: {ref}" for src, ref in zip(src_data, ref_data)])
        else:
            self.docs.extend(src_data)
            self.docs.extend(ref_data)

        self.n_docs = n_docs
        self.samples = samples

        self.embedding_model = "paraphrase-multilingual-MiniLM-L12-v2"
        self.umap_model = UMAP(n_components=5, n_neighbors=40, metric="cosine", min_dist=0.0)
        self.hdbscan_model = HDBSCAN(min_samples=20, min_cluster_size=20, gen_min_span_tree=True, prediction_data=True)
        self.vectorizer_model = CountVectorizer(stop_words=self.stops, ngram_range=(1,3))
        self.ctfidf_model = ClassTfidfTransformer()
        self.representation_model = KeyBERTInspired()

        # get language codes - start from codes
        # lgs = [word[0:2] for word in self.langs]

        # for lang in langs:
        #     with open(f"{filepath}{lang}", "r", encoding='utf-8') as file:
        #         fdocs = list(file.readlines())
        #         self.docs.extend(fdocs)

        # init model
        self.topic_model = bertopic.BERTopic(
                        nr_topics=nr_topics,
                        low_memory=True,
                        verbose=False,
                        calculate_probabilities=True,
                        language="multilingual",
                        seed_topic_list=None,
                        top_n_words=10,
                        n_docs = self.n_docs,
                        samples = self.samples,
                        embedding_model=self.embedding_model,
                        umap_model=self.umap_model,
                        hdbscan_model=self.hdbscan_model,
                        vectorizer_model=self.vectorizer_model,
                        ctfidf_model=self.ctfidf_model,
                        representation_model=self.representation_model
                        **kwargs)

        self.topics, self.probs = self.topic_model.fit_transform(self.docs)

        return self.topic_model

    def closest_topics(self, sentences:str, top_n:int):

        top_n = -abs(top_n)

        if isinstance(sentences, list):
            pass
        else:
            sentences = [sentences]
        self.test_docs = sentences

        # predict topics for list of docs
        self.topics_test, self.probs_test = self.topic_model.transform(self.test_docs)
        # print(self.probs_test)

        # argsort returns indices to sort array
        self.top_n_idx = [np.flip(np.argsort(doc_probs).flatten()[top_n:]) for doc_probs in self.probs_test]

        self.top_n_probs = [np.flip(np.sort(doc_probs).flatten()[top_n:]).tolist() for doc_probs in self.probs_test]

        # TODO: add handling for KeyBERT, Llama2
        topic_dict = self.topic_model.get_topics()

        # topic_no-1 because of topic [-1] at index 0
        self.top_n_topics = [{topic_no:topic_dict[topic_no-1] for topic_no in doc} for doc in self.top_n_idx]

        #     second_idx = [np.flip(np.argsort(doc_probs).flatten()[top_n+1:]) for doc_probs in self.probs_test]
        #     print(second_idx)
        #     self.top_n_topics = [{topic_no:topic_dict[topic_no] for topic_no in doc} for doc in self.top_n_idx[1:]]

        # redefine top topic (sometimes prediction gives outlier topic -1)
        self.topics_test = [np.flip(np.argsort(doc_probs).flatten()[1:]) for doc_probs in self.probs_test]

        return self.top_n_topics, self.top_n_probs

    def representative_topics(self):

        # must have run closest topics?
        topic_nos = [self.top_n_idx[doc_no][0] for doc_no, doc in enumerate(self.test_docs)]
        self.rep_docs = self.topic_model.get_representative_docs()
        if not self.rep_docs:
            with open(f"{self.path}/rep_docs.json") as json_file:
                self.rep_docs = json.load(json_file)
        self.rep_docs = {int(k):v for k,v in self.rep_docs.items()}
        
        reps = [self.rep_docs[topic_no-1] for topic_no in topic_nos]

        return reps

    # def random_topics(self, topic_no):

    #     with open(f"{self.path}/rep_docs.json") as json_file:
    #         self.rep_docs = json.load(json_file)
    #     self.rep_docs = {int(k):v for k,v in self.rep_docs.items()}
        
    #     reps = [self.rep_docs[topic_no-1]]

    #     return reps

    def _generate_stops(self):
        if self.stop_langs:
            if "lt" in self.langs:
                stops = lt_stops[0:100]
            else:
                try:
                    stops = [ads.stopwords[lang] for lang in self.stop_langs]
                    stops = list(itertools.chain.from_iterable(stops))
                except KeyError:
                    stops = [stopwordsiso.stopwords(lang) for lang in self.langs]
                    stops = list(itertools.chain.from_iterable(stops))
        else:
            stops = None
        return stops

    def _format_data(self, data_dir):
        for lang in self.langs:
            with open(f"{data_dir}{lang}", "r", encoding='utf-8') as file:
                fdocs = list(file.readlines())
                self.docs.extend(fdocs)

    def _extract_keywords(self):

        pass

lt_stops = ['ir', 'yra', 'su', 'iš', 'kad', 'kaip', 'savo', 'tai', 'ar', 'gali', 'nuo', 'apie', 'arba', 'bet', 'būti', 'taip', 'jūsų', 'jei', 'buvo', 'pat', 'mūsų', 'per', 'kai', 'jūs', 'mes', 'tik', 'turi', 'jums', 'jis', 'dėl', 'ne', 'iki', 'galite', 'daugiau', 'o', 'jie', 'po', 'kurie', 'bus', 'labai', 'už', 'be', 'prieš', 'jų', 'ant', 'kuris', 'pagal', 'bei', 'prie', 'nėra', 'ji', 'reikia', 'jo', 'tačiau', 'daug', 'nei', 'metu', 'kas', 'galima', 'm.', 'įmonės', 'jos', 'aš', 'todėl', 'nes', 'tiek', 'metų', 'šis', 'darbo', 'gauti', 'dar', 'to,', 'kuri', 'kodas', 'visi', 'naudoti', 'vienas', 'ką', 'kurios', 'būtų', 'jau', 'kitų', 'duomenų', 'tarp', 'net', 'tada', 'kokybės', 'turite', 'jį', 'nors', 'tai,', 'lietuvos', 'dabar', 'kur', 'mano', 'kurių', 'turėtų', 'naujas', 'ši', 'oro', 'kartu', 'čia', 'šiuo', 'šios', 'verslo', 'visų', 'tuo', 'visada', 'vaizdo', 'tam', 'viena', 'padaryti', 'to', 'visiškai', 'vandens', 'juos', 'naudojant', 'produktai', 'visą', 'leidžia', 'aukštos', 'vieną', 'nustatyti', 'šio', 'informacija', 'visos', 'dažnai', 'norite', 'europos', 'šių', 'interneto', 'visus', 'pavyzdžiui,', 'kaina', 'vis', 'informacijos', 'rasti', 'tiesiog', 'sukurti', 'sistemos', 'a', 'žaidimai', 'tikrai', 'įranga', 'laiko', 'įvairių', 'šią', 'siekiant', 'žaidimas', 'norėdami', 'el.', 'teisės', 'naudojamas', 'ypač', 'kurį', 'kinija', 'the', 'seksas', 'namų', 'automobilių', 'žaisti', 'kartą', 'maisto', 'd.', 'paprastai', 'pasirinkti', 'metai', 'informaciją', 'prekybos', 'paslaugų', 'gerai', 'prekės', 'kūno', 'veikia', 'suteikia', 'greitai', 'jeigu', 'peržiūros', 'live)', 'produktų', 'mums', 'kodėl', 'kuriuos', 'transporto', 'šie', 'gamybos', 'asmens', 'visas', 'plieno', 'du', 'žmonių', 'odos', 'esate', 'valdymo', 'atlikti', 'paslaugos', 'sistema', 'lengvai', 'atidaryta', 'kinijos']






