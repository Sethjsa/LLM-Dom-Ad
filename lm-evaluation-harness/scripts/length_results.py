#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17.12.21 09:54
# @Author  : Wen Lai
# @Site    : 
# @File    : remove_punctuation.py
# @Usage information: 

# Copyright (c) 2021-present, CIS, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


"""
Give no of correct language for a test document output
Also look at languages of fewshot prompts - split on ":" or "{target-lang}"

"""
import argparse
import os
from langcodes import standardize_tag
import fasttext
from huggingface_hub import hf_hub_download
from tqdm import tqdm
from pprint import pprint
import json
from glob import glob

model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
model = fasttext.load_model(model_path)

modifiers = [
    "xglm-base-trim",
    "xglm-label-trim",
    "xglm-keywords10-seen500-trim",
    "xglm-topic3shot-seen500-trim",

    "xglm-rand-label-trim",
    "verbose-base-trim",

    "xglm-keywords30-seen500-trim",
    "xglm-rand-keywords10-seen500-trim",
    "xglm-rand-keywords10-seen-all-trim",

    "xglm-rand-topic3shot-seen500-trim",
    "xglm-rand-3shot-seen-all-trim",
    
    "xglm-bm25-3shot-seen-all-trim",
    "xglm-sentsim-3shot-seen-all-trim",

    "xglm-topic1shot-seen500-trim",
    "xglm-topic5shot-seen500-trim",

    "xglm-topic3shot-seen200-trim",
    "xglm-topic3shot-seen1000-trim",

    "xglm-bm25-3shot-langs-trim",
    "xglm-sentsim-3shot-langs-trim",

    "xglm-topic3shot-lang500-trim",
    "xglm-topic3shot-domain200-trim",

    "xglm-domain3shot-all-trim",
    "xglm-truerand-3shot-langs-trim"
    ]

mods2 = [modifier.replace('-trim', '') for modifier in modifiers]

modifiers = modifiers + mods2


def main(args):
    # domain_list = ["OpenSubtitles"]
    # pre_list = ["en-fr", "de-en", "cs-en", "en-fi"]
    ### domain_list
    domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'TED2020', 'CCAligned', 'OpenSubtitles']
    # domain_list = ['EMEA', 'JRC-Acquis', 'KDE4', 'QED', 'TED2020', 'CCAligned', 'OpenSubtitles']
    # domain_list = ["EMEA"]
    # lang_pairs = ["en-fr"]
    ### pre_list
    lang_pairs = ["en-cs", "en-de", "en-fi", "en-fr", "en-lt", "en-ro", "en-ta","cs-en", "fr-en", "lt-en", "ro-en"]
    # lang_pairs = ["cs-en", "fr-en", "lt-en", "ro-en"]


    # print('Processing file {}'.format(args.input))

    for modifier in modifiers:
        for lang_pair in lang_pairs:
            for domain in domain_list:
                base_path = "/scratch/saycock/topic/lm-evaluation-harness/outputs/"
                base_path += f"task={domain}-{lang_pair}."
                # base_path += f"modifier={args.modifier}."
                base_path += f"modifier={modifier}."
                base_path += "*outputs.json"

                files = sorted(glob(base_path))

                langs = lang_pair.split("-")
                langs = [standardize_tag(lang) for lang in langs]

                # for filename in glob(base_path):
                try:
                    if len(files) > 1:
                        filename = files[-1]
                    else:
                        filename = files[0]

                    with open(filename, "r") as json_file:
                        # splut = filename.split(".")
                        # splut[1] = splut[1] + "-trim"
                        # splut = ".".join(splut)
                        # print(splut)
                        data = json.load(json_file)

                    with open(filename, "w") as output_file:
                                
                        # data = json.load(json_file)

                        for example in data:
                            example["length"] = len(example["logit_0"].split())

                        json.dump(data, output_file, indent=4, ensure_ascii=False)
                    
                    results = filename.replace("_outputs.json", "_results.json")

                    with open(results, "r") as file1:
                        data1 = json.load(file1)
                        total = 0
                        for doc1 in data:
                            total += doc1["length"]
                        av_len = total / len(data)

                    with open(results, "w") as results_file:
                        task = results.split(".")[0].split("=")[1]
                        print(f"{task}-{modifier}")
                        # print(av_len)
                        try:
                            data1[task]["av_len"] = av_len
                            json.dump(data1, results_file, indent=4, ensure_ascii=False)
                            # print(results_file)
                        except KeyError:
                            pass
            
                except (FileNotFoundError, TypeError, IndexError, json.decoder.JSONDecodeError, ZeroDivisionError):
                        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--modifier", required=False, type=str, help='input path (merge_file)')
    parser.add_argument("--output", required=False, type=str, help='output path')
    parser.add_argument('--encoding', required=False, default='utf-8', help='character encoding for input/output')
    main(parser.parse_args())