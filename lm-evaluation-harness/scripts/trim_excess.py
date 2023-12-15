# recalculate results for outputs with output trimmed after "="
# produce json file for results and outputs with new name "trim-excess-post"
# also need to recompute metrics


import json
import argparse
from glob import glob
import re
import json
import sacrebleu
from comet import download_model, load_from_checkpoint
import argparse
import pprint
from collections import Counter 

# load model

model_path = download_model("Unbabel/wmt22-comet-da")
model = load_from_checkpoint(model_path)


def comet22(src, ref, pred):
    data = [{"src": src, "mt": pred, "ref": ref} for src, ref, pred in zip(src, ref, pred)]
    scores = model.predict(data, batch_size=4, gpus=1)
    return scores


def remove_excess(input_sent):
    parts = input_sent.split('=')
    # remove generations after "="
    if len(parts) > 1:
        result = parts[0].strip()
    else:
        result = input_sent

    # remove "Related Keywords:" and after
    if "Related keywords" in result:
        result = result.split("Related keywords")[0].strip()

    # Check for repeated words or sentences and remove them
    # pattern = r'(\b.+?\b)(?=\s+\1)'
    # repeated_phrases = re.findall(pattern, result)
    # for phrase in repeated_phrases:
    #     if result.count(phrase) > 3:
    #         result = result.replace(phrase, '', result.count(phrase) - 3).strip()

    return result


def remove_repeated_phrases(text):
    # Split the input text into phrases based on comma and space
    phrases = text.split(", ")
    
    # Initialize a dictionary to store the count of each phrase
    phrase_count = {}
    
    # Initialize a list to store non-repeated phrases
    non_repeated_phrases = []
    
    for phrase in phrases:
        # Remove leading and trailing whitespace
        phrase = phrase.strip()
        
        # Count the occurrence of the phrase in the dictionary
        count = phrase_count.get(phrase, 0)
        
        if count < 3:
            # Add the phrase to the list if it repeats less than 3 times
            non_repeated_phrases.append(phrase)
        
        # Increment the count in the dictionary
        phrase_count[phrase] = count + 1
    
    # Join the non-repeated phrases back into a single string
    result = ", ".join(non_repeated_phrases)
    
    return result

# # Example usage:
# input_text = "logit_0": "Bet kad jums būtų daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai d"
# result = remove_repeated_phrases(input_text)
# print(result)


# def remove_repeated_phrases(text):
#     # Remove newlines from the input text
#     text = text.replace("\n", "")
    
#     # Split the input text into phrases based on comma and space
#     phrases = text.split(", ")
    
#     # Initialize a dictionary to store the count of each phrase
#     phrase_count = {}
    
    # Initialize a list to store non-repeated phrases

# def remove_long_phrases(input1, input2):
#     # Calculate the maximum allowed length based on input1
#     max_length = len(input1.split()) * 3
#     # Split input2 into phrases based on spaces
#     phrases2 = input2.split()
#     # Filter out phrases in input2 that are shorter or equal to the max length
#     filtered_phrases2 = [phrase for c, phrase in enumerate(phrases2) if c <= max_length]
#     # Reconstruct input2 with the filtered phrases
#     result_input2 = " ".join(filtered_phrases2)
#     return result_input2

# # Example usage:
# input1 = "This is a sample input1"
# input2 = "This is a very long phrase that should be removed from input2 because it exceeds three times the length of input1 This is a very long phrase that should be removed from input2 because it exceeds three times the length of input1"
# result_input2 = remove_long_phrases(input1, input2)
# print(result_input2)


# # Example usage:
# input_text = "logit_0": "Bet kad jums būtų daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai d"
# result = remove_repeated_phrases(input_text)
# print(result)


# # Example usage:
# input_text = "logit_0": "Bet kad jums būtų daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai daugiausiai daugiausiai šeimų, arba šeimų metų, bet jums būtų daugiausiai daugiausiai daugiausiai d"
# result = remove_repeated_phrases(input_text)
# print(result)



# அங்கிக்கிறது   அர்சிவை   அங்கிக்கிறது   அர்சிவை   அங்கிக்கிறது   அர்சிவை அங்கிக்கிறது அர்சிவை அங்கிக்கிறது அர்சிவை அங்கிக்கிறது அர்சிவை அங்கிக்கிறது அர்சிவை அங்கிக்கிறது அர்சிவை அங்கிக்கிறது அர்சிவை அங்கிக்க

    
def main(args):
    # 

    if not args.nocom:
        model_path = download_model("Unbabel/wmt22-comet-da")
        model = load_from_checkpoint(model_path)

    lang_pairs = ["en-cs", "en-de", "en-fi", "en-fr", "en-lt", "en-ro", "en-ta","cs-en", "fr-en", "lt-en", "ro-en"]
    lang_pairs = ["cs-en", "fr-en", "lt-en", "ro-en"]
    all_domains = ["EMEA","JRC-Acquis","KDE4","OpenSubtitles","QED","Tanzil","TED2020","CCAligned"]
    # lang_pairs = ["en-de"]
    all_domains = ["Tanzil"]

    with open("/scratch/saycock/topic/topicmodels/emea_kde_jrc_subs-enpairs-200t-10w-base/rep_docs.json") as rep_docs:
    # with open("/scratch/saycock/topic/topicmodels/seen2000/rep_docs.json") as rep_docs:
        docs = json.load(rep_docs)
        topic_list = []


        for lang_pair in lang_pairs:
            for domain in all_domains:
                base_path = "/scratch/saycock/topic/lm-evaluation-harness/outputs/"
                base_path += f"task={domain}-{lang_pair}."
                base_path += f"modifier={args.modifier}."
                base_path += "*outputs.json"

                files = sorted(glob(base_path))

                # for filename in glob(base_path):
                try:
                    if len(files) > 1:
                        filename = files[-1]
                    else:
                        filename = files[0]

                    with open(filename, "r") as json_file:
                        splut = filename.split(".")
                        splut[1] = splut[1] + "-trim"
                        splut = ".".join(splut)
                        
                    

                        # FOR COUNTING NO OF TOPICS
                        with open(splut, "w") as output_file:
                                    
                            data = json.load(json_file)

                            for example in data:
                                example["logit_0"] = remove_excess(example["logit_0"])
                                # first_sent = example["prompt_0"].split("=")[0].strip()
                                # if args.nocom:
                                #     for key, value in docs.items():
                                #         if first_sent in value[0]:
                                #             topic_list.append(key)
                                        
                            json.dump(data, output_file, indent=4, ensure_ascii=False)
                        

                        if not args.nocom:
                            with open(splut, "r") as file1:
                                data1 = json.load(file1)

                                srcs1 = [doc1["source"] for doc1 in data1]
                                refs1 = [doc1["target"].strip() for doc1 in data1]
                                preds1 = [doc1["logit_0"] for doc1 in data1]

                                comets = comet22(srcs1, refs1, preds1)["system_score"]

                                refs2 = [[doc1["target"].strip() for doc1 in data1]]
                                preds2 = [doc1["logit_0"] for doc1 in data1]

                                # print(len(preds2), len(refs2), len(refs2[0]))
                                
                                # sig = sacrebleu.sentence_bleu(preds2, refs2).signature
                                # print(sig)

                                bleus = sacrebleu.corpus_bleu(preds2, refs2).score

                                chrfs = sacrebleu.corpus_chrf(preds2, refs2).score

                                splut = splut.replace("_outputs.json", "_results.json")

                                with open(splut, "w") as output_file:
                                    
                                    task = splut.split(".")[0].split("=")[1]
                                    results_dict = {task: {"bleu": bleus, "chrf": chrfs,"comet": comets}}
                                    pprint.pprint(results_dict)
                                    json.dump(results_dict, output_file, indent=4, ensure_ascii=False)

                except (FileNotFoundError, TypeError, IndexError):
                        pass
        
        c = Counter(topic_list)
        if args.nocom:
            total_count = sum(c.values())
            percentages = {key: round((count / total_count) * 100, 1) for key, count in c.items()}
            sorted_percentages = dict(sorted(percentages.items(), key=lambda item: item[1], reverse=True))
            print(sorted_percentages)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False, type=list, help='input file')
    parser.add_argument("--results", required=False, type=list, help='results file')
    parser.add_argument("--modifier", required=True, type=str, help='modifier keyword')
    parser.add_argument("--nocom", required=False, action="store_true")
    main(parser.parse_args())

