# input one file to compute scores 
import json
import sacrebleu
from comet import download_model, load_from_checkpoint
import argparse
import pprint

# load model
model_path = download_model("Unbabel/wmt22-comet-da")
model = load_from_checkpoint(model_path)

def comet22(src, ref, pred):
    data = [{"src": src, "mt": pred, "ref": ref} for src, ref, pred in zip(src, ref, pred)]
    scores = model.predict(data, batch_size=4, gpus=1)
    return scores

def main(args):

    with open(args.input1, "r") as file1:
        data1 = json.load(file1)

        diffs = {}

        srcs1 = [doc1["source"] for doc1 in data1]
        refs1 = [doc1["target"].strip() for doc1 in data1]
        preds1 = [doc1["logit_0"] for doc1 in data1]

        comets = comet22(srcs1, refs1, preds1)["scores"]

        refs2 = [[doc1["target"].strip()] for doc1 in data1]
        preds2 = [doc1["logit_0"] for doc1 in data1]

        bleus = sacrebleu.corpus_bleu(preds2, refs2).score

        chrfs = sacrebleu.corpus_chrf(preds2, refs2).score

        splut = args.input1.replace("_outputs.json", "_results.json")

        with open(splut, "w") as output_file:
            
            task = args.input1.split(".")[0].split("=")[1]
            results_dict = {task: {"bleu": bleus, "chrf": chrfs,"comet": comets}}
            pprint.pprint(results_dict)
            json.dump(results_dict, output_file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input1", required=True, type=str, help='input baseline file')
    main(parser.parse_args())
