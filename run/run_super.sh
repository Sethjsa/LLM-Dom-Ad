#!/usr/bin/bash

# langs=("en-cs" "en-de" "en-fi" "en-fr" "en-lt" "en-ro" "en-ta" "cs-en" "fr-en" "lt-en" "ro-en")
# 
langs=("cs" "de" "fi" "fr" "lt" "ro" "ta")
# langs=("cs")
# domains=("EMEA" "JRC-Acquis" "KDE4" "OpenSubtitles" "QED" "Tanzil" "TED2020")
# domains=("JRC-Acquis")

langs2=("cs" "fr" "lt" "ro")
langs2=("cs" "fr" "ro")
domains2=("EMEA" "JRC-Acquis" "KDE4" "OpenSubtitles" "QED" "Tanzil" "TED2020")
domains2=("Tanzil")


name=$1

for lang in "${langs[@]}"; do
    for domain in "${domains[@]}"; do
    file="run_${domain}_llama13.sh"
    echo $file
    echo "$domain <> en--$lang"
    # sbatch $file "en" "$lang" 3 "xglm-topic3shot-seen200" "--rep_topics" "emea_kde_jrc_subs-enpairs-200t-10w-base"
    # sbatch $file "en" "$lang" 1 "xglm-keywords10-seen500" "--topic_keywords" "seen500"
    # sbatch $file "en" "$lang" 1 "xglm-rand-keywords10-seen500" "--topic_keywords --randoms" "seen500"
    # sbatch $file "en" "$lang" 3 "xglm-keywords30-seen500" "--topic_keywords" "seen500"
    # sbatch $file "en" "$lang" 1 "xglm-rand-keywords10-seen-all" "--topic_keywords --true_random --seen --all_langs" ""
    # sbatch $file "en" "$lang" 3 "xglm-topic3shot-seen500-nostop" "--rep_topics" "seen500-2"
    # sbatch $file "en" "$lang" 3 "xglm-rand-3shot-seen-all" "--rep_topics --seen --all_langs --true_random" ""
    # sbatch $file "en" "$lang" 3 "xglm-bm25-3shot-seen-all" "--bm25 --seen --all_langs" ""
    # sbatch $file "en" "$lang" 3 "xglm-sentsim-3shot-seen-all" "--sent_sim --seen --all_langs" ""
    # sbatch $file "en" "$lang" 3 "xglm-sentsim-3shot-langs" "--sent_sim" ""
    # sbatch $file "en" "$lang" 3 "xglm-bm25-3shot-langs" "--bm25" ""
    # sbatch $file "en" "$lang" 1 "xglm-truerand-keywords10-all" "--topic_keywords --true_random --all_langs" ""
    # sbatch $file "en" "$lang" 3 "xglm-topic3shot-domain200" "--rep_topics" "$domain-enpairs-200t-10w"
    # sbatch $file "en" "$lang" 3 "xglm-topic3shot-domain500" "--rep_topics" "$domain-500"
    # sbatch $file "en" "$lang" 3 "xglm-topic3shot-lang500" "--rep_topics"  "en-$lang-500"
    # sbatch $file "en" "$lang" 1 "xglm-rand-domainkeywords10-all" "--domain_random --topic_keywords --all_langs" ""
    # sbatch $file "en" "$lang" 3 "xglm-rand-topic3shot-seen500" "--rep_topics --randoms" "seen500"
    # sbatch $file "en" "$lang" 3 "xglm-topic3shot-all2000" "--rep_topics" "all2000"
    # sbatch $file "en" "$lang" 3 "xglm-topic3shot-seen500" "--rep_topics" "seen500"
    # sbatch $file "en" "$lang" 5 "xglm-topic5shot-seen500" "--rep_topics" "seen500"
    # sbatch $file "en" "$lang" 1 "xglm-base" "" ""
    done
done

for lang in "${langs2[@]}"; do
    for domain in "${domains2[@]}"; do
    file="run_${domain}_llama13.sh"
    echo $file
    echo "$domain <> $lang--en"
    # sbatch $file "$lang" "en" 3 "xglm-topic3shot-seen1000" "--rep_topics" "seen1000"
    # sbatch $file "$lang" "en" 1 "xglm-rand-label" "--domain_label --randoms" ""
    # sbatch $file "$lang" "en" 1 "xglm-keywords10-seen500" "--topic_keywords" "seen500"
    # sbatch $file "$lang" "en" 1 "xglm-rand-keywords10-seen500" "--topic_keywords --randoms" "seen500"
    # sbatch $file "$lang" "en" 3 "xglm-keywords30-seen500" "--topic_keywords" "seen500"
    # sbatch $file "$lang" "en" 1 "xglm-rand-keywords10-seen-all" "--topic_keywords --true_random --seen --all_langs" ""
    # sbatch $file "$lang" "en" 3 "xglm-topic3shot-seen500-nostop" "--rep_topics" "seen500-2"
    # sbatch $file "$lang" "en" 3 "xglm-rand-3shot-seen-all" "--rep_topics --seen --all_langs --true_random" ""
    # sbatch $file "$lang" "en" 3 "xglm-bm25-3shot-seen-all" "--bm25 --seen --all_langs" ""
    # sbatch $file "$lang" "en" 3 "xglm-sentsim-3shot-seen-all" "--sent_sim --seen --all_langs" ""
    # sbatch $file "$lang" "en" 3 "xglm-sentsim-3shot-langs" "--sent_sim" ""
    # sbatch $file "$lang" "en" 1 "xglm-truerand-keywords10-all" "--topic_keywords --true_random --all_langs" ""
    # sbatch $file "$lang" "en" 3 "xglm-topic3shot-domain200" "--rep_topics"  "$domain-enpairs-200t-10w"
    # sbatch $file "$lang" "en" 3 "xglm-topic3shot-domain500" "--rep_topics" "$domain-500"
    # sbatch $file "$lang" "en" 3 "xglm-topic3shot-lang500" "--rep_topics"  "en-$lang-500"
    # sbatch $file "$lang" "en" 1 "xglm-rand-domainkeywords10-all" "--domain_random --topic_keywords --all_langs" ""
    # sbatch $file "$lang" "en" 3 "xglm-rand-topic3shot-seen500" "--rep_topics --randoms" "seen500"
    sbatch $file "$lang" "en" 3 "xglm-rand-topic3shot-seen200" "--rep_topics --randoms" "emea_kde_jrc_subs-enpairs-200t-10w-base"
    # sbatch $file "$lang" "en" 3 "xglm-topic3shot-all2000" "--rep_topics" "all2000"
    # sbatch $file "$lang" "en" 3 "xglm-topic3shot-seen500" "--rep_topics" "seen500"
    # sbatch $file "$lang" "en" 5 "xglm-topic5shot-seen500" "--rep_topics" "seen500"
    # sbatch $file "$lang" "en" 1 "xglm-base" "" ""
    # sbatch $file "$lang" "en" 1 "xglm-verbose" "--verbose" ""
    done
done



# "emea_kde_jrc_subs-enpairs-200t-10w-base"
# "alldomains-enpairs-500t-10w-base"
# "ccaligned-enpairs-100t-10w-base"
# "seen500"
# "all500"
# "alldomains-en-cs-200t-10w"