# input files to compare
# measure difference in bleu, comet per sentence
# output list of docs with highest changes
# average change as well

# also look at length statistics per sentemce
# average change in length

import json
import sacrebleu
from collections import OrderedDict
from comet import download_model, load_from_checkpoint
import argparse
import sys
import pprint
# load model
model_path = download_model("Unbabel/wmt22-comet-da")
model = load_from_checkpoint(model_path)

def comet22(src, ref, pred):
    data = [{"src": src, "mt": pred, "ref": ref} for src, ref, pred in zip(src, ref, pred)]
    scores = model.predict(data, batch_size=4, gpus=1)
    return scores

def bleu(ref, pred):
    return sacrebleu.sentence_bleu(pred, [ref]).score

test = 2

def main(args):

    with open(args.input1) as file1, open(args.input2, "r") as file2:
        data1 = json.load(file1)
        data2 = json.load(file2)
        assert len(data1) == len(data2)
        diffs = {}

        srcs1 = [doc1["source"] for doc1 in data1]
        refs1 = [doc1["target"].strip() for doc1 in data1]
        preds1 = [doc1["logit_0"] for doc1 in data1]

        comets1 = comet22(srcs1, refs1, preds1)["scores"]

        srcs2 = [doc2["source"] for doc2 in data2]
        refs2 = [doc2["target"].strip() for doc2 in data2]
        preds2 = [doc2["logit_0"] for doc2 in data2]

        comets2 = comet22(srcs2, refs2, preds2)["scores"]
    
        av_len_diff = 0

        for c, (doc1, doc2) in enumerate(zip(data1, data2)):

            doc1["bleu_score"] = bleu(doc1["target"].strip(), doc1["logit_0"])
            # doc1["comet_score"] = comet22(doc1["source"], doc1["truth"].strip(), doc1["logit_0"])
            # doc1["comet_score"] = comet22(doc1["comet"].split(",)")[0], doc1["truth"].strip(), doc1["logit_0"])
        
            doc2["bleu_score"] = bleu(doc2["target"].strip(), doc2["logit_0"])
            # doc2["comet_score"] = comet22(doc2["comet"].split(",)")[0], doc2["truth"].strip(), doc2["logit_0"])

            doc2["comet_score"] = comets2[c]

            doc2["comet_diff"] = comets2[c] - comets1[c]
            doc2["bleu_diff"] = doc2["bleu_score"] - doc1["bleu_score"]

            doc1["len_pred"] = len(doc1["logit_0"].split())
            doc2["len_pred"] = len(doc2["logit_0"].split())
            doc2["len_diff"] = len(doc2["logit_0"].split()) - len(doc1["logit_0"].split())
            av_len_diff += doc2["len_diff"]

            diffs[doc1["doc_id"]] = {"source": doc1["source"], "target": doc1["target"].strip(), "bleu_diff": doc2["bleu_score"] - doc1["bleu_score"], "comet_diff": comets2[c] - comets1[c]}

        sorted_diffs = OrderedDict(sorted(diffs.items(), key=lambda t:t[1]["comet_diff"], reverse=False))
        pprint.pprint(sorted_diffs)

        av_len_diff = av_len_diff / c
        print(f"Average length diff (words): {av_len_diff}")


    with open(args.input2, "w") as fp:
        data2 = sorted(data2, key=lambda x: x["comet_diff"], reverse=True)
        pprint.pprint(data2)
        json.dump(data2, fp, indent=4, ensure_ascii=False)
   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input1", required=True, type=str, help='input baseline file')
    parser.add_argument("--input2", required=True, type=str, help='input comparison file')
    main(parser.parse_args())
