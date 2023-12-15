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
from string import punctuation
import os
from tqdm import tqdm

def len_no_punc(s, punc):
    return len([ch for ch in s if ch in punc])

def filter_overpunc(len_npunc, len_sen):
    return len_npunc < 0.5*len_sen

def main(args):
    ### domain_list
    domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'CCAligned', 'TED2020', 'OpenSubtitles']
    ### pre_list
    pre_list = ['en-fi', 'en-fr', 'de-en', 'en-lt', 'en-ta', 'en-ro', 'cs-en']
    punc = punctuation + "—|–"
    print('Processing file {}'.format(args.input))

    for dl in domain_list:
        print('process domain: ' + dl)
        if not os.path.exists(os.path.join(args.output, dl)):
            os.mkdir(os.path.join(args.output, dl))

        for pre_LL in pre_list:
            bad_count = 0
            lang_LL = pre_LL.split('-')
            src_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.' + lang_LL[0]), 'wt', encoding=args.encoding)
            tgt_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.' + lang_LL[1]), 'wt', encoding=args.encoding)

            try:
                with open(os.path.join(args.input, dl, dl + '.clean.' + pre_LL + '.' + lang_LL[0]), 'rt', encoding=args.encoding) as f_src:
                    with open(os.path.join(args.input, dl, dl + '.clean.' + pre_LL + '.' + lang_LL[1]), 'rt', encoding=args.encoding) as f_tgt:
                        for ori_1, ori_2 in tqdm(zip(f_src, f_tgt)):
                            src, tgt = ori_1.strip(), ori_2.strip()

                            nchar_npunc_src = len_no_punc(src, punc)
                            nchar_npunc_tgt = len_no_punc(tgt, punc)

                            if filter_overpunc(nchar_npunc_src, len(src)) and filter_overpunc(nchar_npunc_tgt, len(tgt)):
                                src_out.write(src.strip() + '\n')
                                tgt_out.write(tgt.strip() + '\n')
                            else:
                                bad_count += 1
                        print(pre_LL + 'file number of bad punc sents: ' + str(bad_count))
            except FileNotFoundError:
                print("file not found")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=str, help='input path (merge_file)')
    parser.add_argument("--output", required=True, type=str, help='output path')
    parser.add_argument('--encoding', default='utf-8', help='character encoding for input/output')
    main(parser.parse_args())