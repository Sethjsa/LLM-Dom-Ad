#!/usr/bin/bash

langs=("cs" "de" "fi" "fr" "lt" "ro" "ta")
domains=("EMEA" "JRC-Acquis" "KDE4" "OpenSubtitles" "QED" "Tanzil" "TED2020" "CCAligned")
modifiers=(
    "xglm-base"
    "xglm-base-trim"
    "verbose-base"
    "verbose-base-trim"
    "xglm-label"
    "xglm-label-trim"
    "xglm-rand-label"
    "xglm-rand-label-trim"
    "xglm-keywords10-seen200"
    "xglm-keywords10-seen200-trim"
    "xglm-rand-keywords10-seen200"
    "xglm-rand-keywords10-seen200-trim"
    "xglm-topic3shot-seen200"
    "xglm-topic3shot-seen200-trim"
    "xglm-topic3shot-all500"
    "xglm-topic3shot-all500-trim"
    "xglm-topic1shot-seen200"
    "xglm-topic1shot-seen200-trim"
    "xglm-rand-topic3shot-seen200"
    "xglm-rand-topic3shot-seen200-trim"
)

for modifier in "${modifiers[@]}"; do
    echo $modifier
    python -m gen_csv --modifier "$modifier"
    # python -m trim_excess --modifier "$modifier"
done

python language_table.py