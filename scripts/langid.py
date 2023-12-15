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
Example:

"""
import argparse
import os
from langcodes import standardize_tag
import fasttext
from huggingface_hub import hf_hub_download
from tqdm import tqdm

model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
model = fasttext.load_model(model_path)

def main(args):
    # domain_list = ["OpenSubtitles"]
    # pre_list = ["en-fr", "de-en", "cs-en", "en-fi"]
    ### domain_list
    domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'TED2020', 'CCAligned', 'OpenSubtitles']
    ### pre_list
    pre_list = ['en-fi', 'en-fr', 'de-en', 'en-lt', 'en-ta', 'en-ro', 'cs-en']

    print('Processing file {}'.format(args.input))

    for dl in domain_list:
        print('process domain: ' + dl)
        if not os.path.exists(os.path.join(args.output, dl)):
            os.mkdir(os.path.join(args.output, dl))

        for pre_LL in pre_list:
            wrong_count = 0
            lang_LL = pre_LL.split('-')
            src_out = open(os.path.join(args.output, dl, dl + '.clean.' + pre_LL + '.' + lang_LL[0]), 'wt', encoding=args.encoding)
            tgt_out = open(os.path.join(args.output, dl, dl + '.clean.' + pre_LL + '.' + lang_LL[1]), 'wt', encoding=args.encoding)
            try:
                with open(os.path.join(args.input, dl, dl + '.' + pre_LL + '.' + lang_LL[0]), 'rt', encoding=args.encoding) as f_src:
                    with open(os.path.join(args.input, dl, dl + '.' + pre_LL + '.' + lang_LL[1]), 'rt', encoding=args.encoding) as f_tgt:
                        for ori_1, ori_2 in tqdm(zip(f_src, f_tgt)):
                            src, tgt = ori_1.strip(), ori_2.strip()

                            # predict and extract language label
                            pred_0 = standardize_tag(model.predict(src)[0][0].split("__")[2], macro=True)
                            pred_1 = standardize_tag(model.predict(tgt)[0][0].split("__")[2], macro=True)

                            if lang_LL[0] == pred_0 and lang_LL[1] == pred_1:
                                src_out.write(src + '\n')
                                tgt_out.write(tgt + '\n')
                            else:
                                wrong_count += 1
                        print(pre_LL + 'file number of wrong lang_ids: ' + str(wrong_count))
            except FileNotFoundError:
                print("file not found")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=str, help='input path (merge_file)')
    parser.add_argument("--output", required=True, type=str, help='output path')
    parser.add_argument('--encoding', default='utf-8', help='character encoding for input/output')
    main(parser.parse_args())