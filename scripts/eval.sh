#!/bin/bash

domain_list=('EMEA' 'Tanzil' 'JRC-Acquis' 'KDE4' 'QED' 'TED2020' 'OpenSubtitles')
pair_list=('en-fi' 'en-fr' 'de-en' 'en-lt' 'en-ta' 'en-ro' 'cs-en')
model="nllb-200-1.3B"
addition=""
test="test"

for domain in "${domain_list[@]}"; do
    for lang_pair in "${pair_list[@]}"; do

        # Define the file paths
        hyps="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.eval"
        refs="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.ref"
        srcs="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.src"

        # Run the sacrebleu command
        cat $hyps | sacrebleu $refs -m bleu chrf > "/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.sacrebleu"

        # Run the comet-score command
        comet-score -s $srcs -r $refs -c $hyps --quiet --only_system --model Unbabel/wmt22-comet-da -o "/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.comet"
    done
done

# import subprocess

# domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'CCAligned', 'TED2020', 'OpenSubtitles']
# pair_list = ['en-fi', 'en-fr', 'de-en', 'en-lt', 'en-ta', 'en-ro', 'cs-en']


# def evaluate_translations(domain_list, pair_list, model, addition, test):
#     for domain in domain_list:
#         for lang_pair in pair_list:
#             # Define the file paths
#             hyps = f"{domain}-{lang_pair}.eval"
#             refs = f"{domain}-{lang_pair}.ref"
#             srcs = f"{domain}-{lang_pair}.src"

#             # Run the sacrebleu command
#             sacrebleu_command = f"cat {hyps} | sacrebleu {refs} -m bleu chrf > tests/hyps-{model}{addition}-{test}-{lang_pair}.sacrebleu"
#             subprocess.run(sacrebleu_command, shell=True)

#             # Run the comet-score command
#             comet_command = f"comet-score -s {srcs} -r {refs} -c {hyps} --quiet --only_system --model Unbabel/wmt22-comet-da -o tests/hyps-{model}{addition}-{test}-{lang_pair}.comet"
#             subprocess.run(comet_command, shell=True)

# # Call the function with your parameters
# evaluate_translations(domain_list, pair_list, "nllb-200-3.3B", "", "test")