import argparse
import os
import random
from tqdm import tqdm

def main(args):
    ### domain_list
    # domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'CCAligned', 'TED2020', 'OpenSubtitles']
    # ### pre_list
    # pre_list = ['en-fi', 'en-fr', 'de-en', 'en-lt', 'en-ta', 'en-ro', 'cs-en']
    domain_list = ["OpenSubtitles"]
    pre_list = ['en-fi', 'en-fr', 'de-en', 'cs-en']    

    print('Processing file {}'.format(args.input))

    for dl in domain_list:
        print('processing domain: ' + dl)
        if not os.path.exists(os.path.join(args.output, dl)):
            os.mkdir(os.path.join(args.output, dl))


        for pre_LL in pre_list:

            print('processing: ' + dl + '----' + pre_LL)

            lang_LL = pre_LL.split('-')

            src_train_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.train.' + lang_LL[0]), 'wt', encoding=args.encoding)
            tgt_train_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.train.' + lang_LL[1]), 'wt', encoding=args.encoding)

            src_test_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.test.' + lang_LL[0]), 'wt', encoding=args.encoding)
            tgt_test_out = open(os.path.join(args.output, dl, dl + '.' + pre_LL + '.test.' + lang_LL[1]), 'wt', encoding=args.encoding)

            try:
                with open(os.path.join(args.input, dl, dl + '.' + pre_LL + '.' + lang_LL[0]), 'rt', encoding=args.encoding) as f_src:
                    with open(os.path.join(args.input, dl, dl + '.' + pre_LL + '.' + lang_LL[1]), 'rt', encoding=args.encoding) as f_tgt:
                        
                        bitext = list(zip(f_src, f_tgt))

                        if len(bitext) > 5500:
                            sets = random.sample(bitext, 5500)
                            random.shuffle(sets)
                            train = sets[0:5000]
                            test = sets[5000:5500]

                        elif len(bitext) < 5500 and len(bitext) > 1000:
                            sets = random.sample(bitext, len(bitext))
                            random.shuffle(sets)
                            train = sets[:-500]
                            test = sets[-500:]

                        for ori_1, ori_2 in train:
                            src, tgt = ori_1.strip(), ori_2.strip()
                            src_train_out.write(src + '\n')
                            tgt_train_out.write(tgt + '\n')
                        
                        for ori_1, ori_2 in test:
                            src, tgt = ori_1.strip(), ori_2.strip()
                            src_test_out.write(src + '\n')
                            tgt_test_out.write(tgt + '\n')

            except FileNotFoundError:
                print("dataset not found")
            except ValueError:
                print("not enough data")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=str, help='input path (merge_file)')
    parser.add_argument("--output", required=True, type=str, help='output path')
    parser.add_argument('--encoding', default='utf-8', help='character encoding for input/output')
    main(parser.parse_args())