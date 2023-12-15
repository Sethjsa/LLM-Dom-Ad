#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17.12.21 14:48
# @Author  : Wen Lai
# @Site    : 
# @File    : moses_len_filter.py
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
import subprocess

def main(args):
    ## domain_list
    domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'CCAligned', 'TED2020', 'OpenSubtitles']
    ## pre_list
    pre_list = ['en-fi', 'en-fr', 'de-en', 'en-lt', 'en-ta', 'en-ro', 'cs-en']


    for dl in domain_list:
        if not os.path.exists(os.path.join(args.output, dl)):
            os.mkdir(os.path.join(args.output, dl))
        for pre_LL in pre_list:
            print('processing: ' + dl + '.' + pre_LL)
            lang_LL = pre_LL.split('-')
            command = 'perl ' + args.moses \
                      + ' --ratio 3 ' \
                      + os.path.join(args.input, dl, dl + '.' + pre_LL) \
                      + ' ' + lang_LL[0] + ' ' + lang_LL[1] \
                      + ' ' + os.path.join(args.output, dl, dl + '.clean.' + pre_LL) + ' 1 175'
            subprocess.call(command, shell=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=str, help='input path')
    parser.add_argument("--output", required=True, type=str, help='output path')
    parser.add_argument("--moses", required=True, type=str, help='moses clean scripts')
    main(parser.parse_args())

# clean-corpus-n.perl corpus l1 l2 output minlen maxlen