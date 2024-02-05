langs=("cs-en" "de-en" "en-fi" "en-fr" "en-lt" "en-ro" "en-ta")
domains=("EMEA" "JRC-Acquis" "KDE4" "OpenSubtitles" "QED" "Tanzil" "TED2020")


for lang in "${langs[@]}"; do
    for domain in "${domains[@]}"; do
        sbatch run_nllb.sh $lang $domain
    done
done