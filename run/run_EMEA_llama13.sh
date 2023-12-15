#!/usr/bin/bash
#SBATCH --job-name=EMEA   # nom du job
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=4           # number of cores per task (with gpu_p2: 1/8 of the 8-GPUs node)
#SBATCH --ntasks=1             # Nombre total de processus MPI
#SBATCH --ntasks-per-node=1    # Nombre de processus MPI par noeud
#SBATCH --hint=multithread   # 1 processus MPI par coeur physique (pas d'hyperthreading)
#SBATCH --time=4:00:00        # Temps d’exécution maximum demande (HH:MM:SS)
#SBATCH --output=./runs/%x_%j.out  # Nom du fichier de sortie contenant l'ID et l'indice
#SBATCH --error=./runs/%x_%j.out   # Nom du fichier d'erreur (ici commun avec la sortie)


# go into the submission directory
cd /scratch/saycock/scripts/runs/
module purge

# Set your conda environment
source /home/$USER/.bashrc
# tensorflow environment shloud bre created previously
conda activate dada2


maindir=/scratch/saycock/topic/lm-evaluation-harness
outputdir=/scratch/saycock/topic/lm-evaluation-harness/outputs
[ -d $outputdir ] || mkdir $outputdir

modelname=llama-13b
modelpath=meta-llama/Llama-2-13b-hf
# modelpath=EleutherAI/pythia-160m
tokeniserpath=$modelpath

# choose a task and comment the other
dataset=EMEA
source=$1
target=$2
task="$dataset-$source-$target"

# choose q modifier/name
name=$4

# choose a fewshot number
fewshotnum=$3

# misc params
seed=1234
batchsize=8
timestamp=$(date +"%Y-%m-%dT%H_%M_%S")
output="task=$task.modifier=$name.seed=$seed.timestamp=$timestamp"

topic_flag=$5
echo $topic_flag

topic_model=$6

export CUDA_LAUNCH_BLOCKING=1
echo "Writing to: $output"
TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
TOKENIZERS_PARALLELISM=false \
python $maindir/main.py --model 'hf-causal-experimental' --model_args "use_accelerate=True,pretrained=$modelpath,tokenizer=$tokeniserpath" \
    --tasks=$task --num_fewshot=$fewshotnum --seed=$seed --write_out --output_base_path="$outputdir" --output_template="$output" \
    --no_cache --batch_size $batchsize --device cuda --bootstrap_iters=2 \
    $topic_flag --topic_model="$topic_model"