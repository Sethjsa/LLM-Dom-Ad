#!/bin/bash

#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
##SBATCH --nodelist=ilps-cn104
#SBATCH --exclude=ilps-cn108,ilps-cn113,ilps-cn104
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
##SBATCH --begin=now+1minute
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=s.aycock@uva.nl 

#SBATCH -o jobs/%x.%j.o
#SBATCH -e jobs/%x.%j.e

# activate conda environment
export PATH=/home/saycock/miniconda3/bin:$PATH
# source /home/saycock/miniconda3/etc/profile.d/conda.sh
# conda activate doma
source activate doma

# # set cuda paths - idk if this works or messes things up
export CUDA_HOME="/usr/local/cuda-10.2"
export PATH="${CUDA_HOME}/bin:${PATH}"
export LIBRARY_PATH="${CUDA_HOME}/lib64:${LIBRARY_PATH}"
export LD_LIBRARY_PATH="/home/saycock/cudalibs:/usr/lib64/nvidia:${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}"

lang_pair=$1
domain=$2

python /home/saycock/LLM-Dom-Ad/gen-nllb.py --lang_pair $lang_pair --domain $domain

if [ "$lang_pair" == "de-en" ]; then
    lang_pair="en-de"
fi

if [ "$lang_pair" == "cs-en" ]; then
    lang_pair="en-cs"
fi

hyps="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.eval"
refs="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.ref"
srcs="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.src"

echo $lang_pair

# Run the sacrebleu command
cat $hyps | sacrebleu $refs -m bleu > /home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.sacrebleu

# Run the comet-score command
comet-score -s $srcs -r $refs -t $hyps --quiet --only_system --model Unbabel/wmt22-comet-da > /home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.comet



# and into english
lang_codes=("cs" "fr" "lt" "ro")

# Get the source language from the language pair
src_lang=${lang_pair%-*}
tgt_lang=${lang_pair#*-}


if [[ " ${lang_codes[@]} " =~ " ${tgt_lang} " ]]; then
    # If it is, reverse the language pair
    lang_pair="${tgt_lang}-${src_lang}"
fi

echo $lang_pair
hyps="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.eval"
refs="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.ref"
srcs="/home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.src"

# Run the sacrebleu command
cat $hyps | sacrebleu $refs -m bleu > /home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.sacrebleu

# Run the comet-score command
comet-score -s $srcs -r $refs -t $hyps --quiet --only_system --model Unbabel/wmt22-comet-da > /home/saycock/LLM-Dom-Ad/tests/${domain}-${lang_pair}.comet

