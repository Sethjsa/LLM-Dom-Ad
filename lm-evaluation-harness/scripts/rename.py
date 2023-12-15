import json
from glob import glob
import os

domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'TED2020', 'CCAligned', 'OpenSubtitles']
lang_pairs = ["cs-en", "fr-en", "lt-en", "ro-en"]

for lang_pair in lang_pairs:
    for domain in domain_list:
        base_path = "/scratch/saycock/topic/lm-evaluation-harness/outputs/"
        base_path += f"task={domain}-{lang_pair}."
        # base_path += f"modifier={args.modifier}."
        base_path += "modifier=xglm-keywords10-seen200."
        base_path += "*results.json"

        files = sorted(glob(base_path))

        source = files[0]

        target = source.replace("keywords10", "keywords30")

        print(target)

        os.rename(source, target)
