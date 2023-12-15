import csv
import argparse
from glob import glob
import json


def main(args):

    langs = args.langs
    lang_pairs = ["en-cs", "en-de", "en-fi", "en-fr", "en-lt", "en-ro", "en-ta", "cs-en", "fr-en", "lt-en", "ro-en"]
    # lang_pairs = ["cs-en", "fr-en", "lt-en", "ro-en"]
    all_domains = ["EMEA","JRC-Acquis","KDE4","OpenSubtitles","QED","Tanzil","TED2020","CCAligned"]
        
    modifiers = [
        # "xglm-base",
        # "xglm-base-trim",

        # "verbose-base",
        # "verbose-base-trim",

        # "xglm-label",
        # "xglm-label-trim",

        # "xglm-rand-label",
        # "xglm-rand-label-trim",

        # "xglm-keywords10-seen200",
        # "xglm-keywords10-seen200-trim",
        
        # "xglm-rand-keywords10-seen200",
        # "xglm-rand-keywords10-seen200-trim",

        # "xglm-keywords10-all500",
        # "xglm-keywords10-all500-trim",

        # "xglm-keywords30-seen200",
        # "xglm-keywords30-seen200-trim",

        # "xglm-topic3shot-seen200",
        # "xglm-topic3shot-seen200-trim",

        # "xglm-topic3shot-all500",
        # "xglm-topic3shot-all500-trim",

        # "xglm-topic3shot-cc100",
        # "xglm-topic3shot-cc100-trim",

        # "xglm-topic1shot-seen200",
        # "xglm-topic1shot-seen200-trim",

        # "xglm-rand-topic3shot-seen200",
        # "xglm-rand-topic3shot-seen200-trim",

        # "xglm-rand-domain3shot-langs",
        # "xglm-rand-domain3shot-langs-trim",
        
        # "xglm-rand-domain3shot-all",
        # "xglm-rand-domain3shot-all-trim",

        # "xglm-truerand-3shot-langs",
        # "xglm-truerand-3shot-langs-trim",

        # "xglm-truerand-3shot-all",
        # "xglm-truerand-3shot-all-trim",

        # "xglm-topic5shot-seen200",
        # "xglm-topic5shot-seen200-trim",

        # "xglm-keywords10-cc100",
        # "xglm-keywords10-cc100-trim",

        # "xglm-keywords10-topic3shot-seen200",
        # "xglm-keywords10-topic3shot-seen200-trim",

        # "xglm-rand-domainkeywords10-langs",
        # "xglm-rand-domainkeywords10-langs-trim",

        # "xglm-rand-domainkeywords10-all",
        # "xglm-rand-domainkeywords10-all-trim",

        # "xglm-truerand-keywords10-langs",
        # "xglm-truerand-keywords10-langs-trim",

        # "xglm-truerand-keywords10-all",
        # "xglm-truerand-keywords10-all-trim",

        # "xglm-topic3shot-seen500",
        # "xglm-topic3shot-seen500-trim",

        # "xglm-topic3shot-seen1000",
        # "xglm-topic3shot-seen1000-trim",

        # "xglm-topic3shot-seen2000",
        # "xglm-topic3shot-seen2000-trim",

        # "xglm-topic3shot-all500",
        # "xglm-topic3shot-all500-trim",

        # "xglm-topic3shot-all1000",
        # "xglm-topic3shot-all1000-trim",
    
        # "xglm-topic3shot-all2000",
        # "xglm-topic3shot-all2000-trim",

        # "xglm-bm25-3shot-all",
        # "xglm-bm25-3shot-all-trim",

        # "xglm-bm25-3shot-langs",
        # "xglm-bm25-3shot-langs-trim",

        # "xglm-sentsim-3shot-langs",
        # "xglm-sentsim-3shot-langs-trim",

        # "xglm-sentsim-3shot-all",
        # "xglm-sentsim-3shot-all-trim",

        # "xglm-topic3shot-lang200",
        # "xglm-topic3shot-lang200-trim",

        # "xglm-topic3shot-lang500",
        # "xglm-topic3shot-lang500-trim",

        # "xglm-topic3shot-domain200",
        # "xglm-topic3shot-domain200-trim",

        # "xglm-bm25-3shot-seen-all",
        # "xglm-bm25-3shot-seen-all-trim",

        # "xglm-sentsim-3shot-seen-all",
        # "xglm-sentsim-3shot-seen-all-trim",

        # "xglm-label-keywords10-topic3shot-seen200",
        # "xglm-label-keywords10-topic3shot-seen200-trim",

        # "xglm-topn-topic3shot-seen500",
        # "xglm-topn-topic3shot-seen500-trim",

        # "xglm-rand-3shot-seen-all-trim",
        # "xglm-rand-keywords10-seen-all-trim",
        # "xglm-topic3shot-domain500",
        # "xglm-sentsim-3shot-seen-all"
        # "xglm-truerand-3shot-langs-trim"
        # "xglm-sentsim-3shot-seen-all"

        # "xglm-topic3shot-domain500"

        # "xglm-topic3shot-seen500-trim",
        # "xglm-topic3shot-domain500"
        # "xglm-rand-3shot-seen-all-trim"

        # "xglm-bm25-3shot-langs"

        # MASTER LIST

        # "xglm-base-trim",
        # "xglm-label-trim",
        # "xglm-keywords10-seen500-trim",
        # "xglm-topic3shot-seen500-trim",

        # "xglm-rand-label-trim",
        # "verbose-base-trim",

        # "xglm-keywords30-seen500-trim",
        # "xglm-rand-keywords10-seen500-trim",
        # "xglm-rand-keywords10-seen-all-trim",

        # "xglm-rand-topic3shot-seen500-trim",
        # "xglm-rand-3shot-seen-all-trim",
        
        # "xglm-bm25-3shot-seen-all-trim",
        # "xglm-sentsim-3shot-seen-all-trim",

        # "xglm-topic1shot-seen500-trim",
        # "xglm-topic5shot-seen500-trim",

        # "xglm-topic3shot-seen200-trim",
        # "xglm-topic3shot-seen1000-trim",
    
        # "xglm-bm25-3shot-langs-trim",
        # "xglm-sentsim-3shot-langs-trim",

        # "xglm-topic3shot-lang500-trim",
        # "xglm-topic3shot-domain200-trim",

        # "xglm-domain3shot-all-trim",
        # "xglm-truerand-3shot-langs-trim",

        "xglm-rand-topic3shot-seen200-trim"
        
        ]

    mods2 = [modifier.replace('-trim', '') for modifier in modifiers]

    modifiers = modifiers + mods2

    for modifier in modifiers:
        print(f"{modifier}:")

        domain_sum = {domain: 0 for domain in all_domains}
        domain_count = {domain: 0 for domain in all_domains}

        print("BLEU:")
        with open(f"/scratch/saycock/topic/lm-evaluation-harness/results/alldomains_{modifier}_bleu_results.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter="\t")
            first_row = ["lang-pair"]
            first_row.extend(all_domains)
            writer.writerow(first_row)
            print(first_row)
            for lang_pair in lang_pairs:
                row = [f"{lang_pair}"]
                for domain in all_domains:
                    base_path = "/home/saycock/scratch/topic/lm-evaluation-harness/outputs/"
                    base_path += f"task={domain}-{lang_pair}."
                    base_path += f"modifier={modifier}."
                    base_path += "*results.json"
                    found = 0
                    files = sorted(glob(base_path))
                    # print(files)
                    # for filename in glob(base_path):
                    try:
                        if len(files) > 1:
                            filename = files[-1]
                        else:
                            filename = files[0]
                        with open(filename, "r") as json_file:
                            data = json.load(json_file)
                            bleu = round(data[f"{domain}-{lang_pair}"]["bleu"], 1)
                            domain_sum[domain] += bleu
                            domain_count[domain] += 1
                            row.append(bleu)
                            found = 1
                    except (KeyError, IndexError, json.decoder.JSONDecodeError):
                        pass
                    if not found:
                        row.append("NA")
                writer.writerow(row)
                print(row)
            av_row = ["mean"]
            for domain in all_domains:
                av = "NA"
                if domain_count[domain] > 0:
                    av = round(domain_sum[domain] / domain_count[domain], 1)
                av_row.append(av)
            writer.writerow(av_row)
            print(av_row)
        
        print("COMET:")

        domain_sum = {domain: 0 for domain in all_domains}
        domain_count = {domain: 0 for domain in all_domains}
            
        with open(f"/scratch/saycock/topic/lm-evaluation-harness/results/alldomains_{modifier}_comet_results.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter="\t")
            first_row = ["lang-pair"]
            first_row.extend(all_domains)
            writer.writerow(first_row)
            print(first_row)
            for lang_pair in lang_pairs:
                row = [f"{lang_pair}"]
                for domain in all_domains:
                    base_path = "/home/saycock/scratch/topic/lm-evaluation-harness/outputs/"
                    base_path += f"task={domain}-{lang_pair}."
                    base_path += f"modifier={modifier}."
                    base_path += "*results.json"
                    found = 0
                    files = sorted(glob(base_path))
                    # for filename in glob(base_path)
                    try:
                        if len(files) > 1:
                            filename = files[-1]
                        else:
                            filename = files[0]
                        with open(filename, "r") as json_file:
                            data = json.load(json_file)
                            comet = round(data[f"{domain}-{lang_pair}"]["comet"] * 100, 1)
                            domain_sum[domain] += comet
                            domain_count[domain] += 1
                            row.append(comet)
                            found = 1
                    except (KeyError, IndexError, json.decoder.JSONDecodeError):
                        pass
                    if not found:
                        row.append("NA")
                            
                writer.writerow(row)
                print(row)
            av_row = ["mean"]
            for domain in all_domains:
                av = "NA"
                if domain_count[domain] > 0:
                    av = round((domain_sum[domain] / domain_count[domain]), 1)
                av_row.append(av)
            writer.writerow(av_row)
            print(av_row)

        domain_sum = {domain: 0 for domain in all_domains}
        domain_count = {domain: 0 for domain in all_domains}

        with open(f"/scratch/saycock/topic/lm-evaluation-harness/results/alldomains_{modifier}_langid_results.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter="\t")
            first_row = ["lang-pair"]
            first_row.extend(all_domains)
            writer.writerow(first_row)
            print(first_row)
            for lang_pair in lang_pairs:
                row = [f"{lang_pair}"]
                for domain in all_domains:
                    base_path = "/home/saycock/scratch/topic/lm-evaluation-harness/outputs/"
                    base_path += f"task={domain}-{lang_pair}."
                    base_path += f"modifier={modifier}."
                    base_path += "*results.json"
                    found = 0
                    files = sorted(glob(base_path))
                    # for filename in glob(base_path)
                    try:
                        if len(files) > 1:
                            filename = files[-1]
                        else:
                            filename = files[0]
                        with open(filename, "r") as json_file:
                            data = json.load(json_file)
                            comet = round((data[f"{domain}-{lang_pair}"]["langids"] / 500) * 100, 1)
                            domain_sum[domain] += comet
                            domain_count[domain] += 1
                            row.append(comet)
                            found = 1
                    except (KeyError, IndexError, json.decoder.JSONDecodeError):
                        pass
                    if not found:
                        row.append("NA")
                            
                writer.writerow(row)
                print(row)
            av_row = ["mean"]
            for domain in all_domains:
                av = "NA"
                if domain_count[domain] > 0:
                    av = round(domain_sum[domain] / domain_count[domain], 1)
                av_row.append(av)
            writer.writerow(av_row)
        
        domain_sum = {domain: 0 for domain in all_domains}
        domain_count = {domain: 0 for domain in all_domains}

        with open(f"/scratch/saycock/topic/lm-evaluation-harness/results/alldomains_{modifier}_length_results.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter="\t")
            first_row = ["lang-pair"]
            first_row.extend(all_domains)
            writer.writerow(first_row)
            print(first_row)
            for lang_pair in lang_pairs:
                row = [f"{lang_pair}"]
                for domain in all_domains:
                    base_path = "/home/saycock/scratch/topic/lm-evaluation-harness/outputs/"
                    base_path += f"task={domain}-{lang_pair}."
                    base_path += f"modifier={modifier}."
                    base_path += "*results.json"
                    found = 0
                    files = sorted(glob(base_path))
                    # for filename in glob(base_path)
                    try:
                        if len(files) > 1:
                            filename = files[-1]
                        else:
                            filename = files[0]
                        with open(filename, "r") as json_file:
                            data = json.load(json_file)
                            comet = round(data[f"{domain}-{lang_pair}"]["av_len"], 1)
                            domain_sum[domain] += comet
                            domain_count[domain] += 1
                            row.append(comet)
                            found = 1
                    except (KeyError, IndexError, json.decoder.JSONDecodeError):
                        pass
                    if not found:
                        row.append("NA")
                            
                writer.writerow(row)
                print(row)
            av_row = ["mean"]
            for domain in all_domains:
                av = "NA"
                if domain_count[domain] > 0:
                    av = round(domain_sum[domain] / domain_count[domain], 1)
                av_row.append(av)
            writer.writerow(av_row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", required=False, type=list, help='list of lang pairs')
    parser.add_argument("--domains", required=False, type=list, help='list of domains')
    parser.add_argument("--modifier", required=False, type=str, help='modifier')
    main(parser.parse_args())