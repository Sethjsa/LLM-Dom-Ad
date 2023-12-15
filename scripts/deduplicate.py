#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17.12.21 10:43
# @Author  : Wen Lai
# @Site    : 
# @File    : deduplicated.py
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
from tqdm import tqdm

def main(args):
    # ### domain_list
    # domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'CCAligned', 'TED2020', 'OpenSubtitles']
    # ### pre_list
    # pre_list = ['en-fi', 'en-fr', 'de-en', 'en-lt', 'en-ta', 'en-ro', 'cs-en']
    domain_list = ["CCAligned"]
    pre_list = ["en-fr", "de-en"]

    for dl in domain_list:
        if not os.path.exists(os.path.join(args.output, dl)):
            os.mkdir(os.path.join(args.output, dl))
        for pre_LL in pre_list:
            seen = set()
            dup_count = 0
            print('processing: ' + dl + '----' + pre_LL)
            lang_LL = pre_LL.split('-')

            src_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.' + lang_LL[0]), 'wt', encoding=args.encoding)
            tgt_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.' + lang_LL[1]), 'wt', encoding=args.encoding)

            try:
                with open(os.path.join(args.input, dl, dl + '.clean.' + pre_LL + '.' + lang_LL[0]), 'rt', encoding=args.encoding) as f_src:
                    with open(os.path.join(args.input, dl, dl + '.clean.' + pre_LL + '.' + lang_LL[1]), 'rt', encoding=args.encoding) as f_tgt:
                        for ori_1, ori_2 in tqdm(zip(f_src, f_tgt)):
                            if (ori_1.strip(), ori_2.strip()) not in seen:
                                src_out.write(ori_1.strip() + '\n')
                                tgt_out.write(ori_2.strip() + '\n')
                                seen.add((ori_1.strip(), ori_2.strip()))
                            else:
                                dup_count += 1
                        print(pre_LL + 'file number of duplication: ' + str(dup_count))
            except FileNotFoundError:
                print("file not found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="src file")
    parser.add_argument("--output", type=str, required=True, help="tgt file")
    parser.add_argument('--encoding', default='utf-8', help='character encoding for input/output')
    main(parser.parse_args())