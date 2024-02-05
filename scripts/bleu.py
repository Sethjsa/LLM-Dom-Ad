import json
import csv

# List of domains
domain_list = ['EMEA', 'JRC-Acquis', 'KDE4', 'OpenSubtitles', 'QED', 'Tanzil', 'TED2020']

# Language pair
lang_pairs = ['en-cs', 'en-de', 'en-fi', 'en-fr', 'en-lt', 'en-ro','en-ta', 'cs-en', 'fr-en', 'lt-en', 'ro-en']

# Initialize a dictionary to store the scores
scores = {lang_pair: {'lang-pair': lang_pair} for lang_pair in lang_pairs}

# Loop over each domain
for domain in domain_list:
    for lang_pair in lang_pairs:
        # Construct the file path
        file_path = f'/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.sacrebleu'
        try:
            # Try to open the JSON file for this domain-language pair
            with open(file_path, 'r') as f:
                # Load the JSON data
                data = json.load(f)
                # print(data)
                # Get the BLEU score and add it to the dictionary
                try:
                    scores[lang_pair][domain] = round(data['score'], 1)
                except TypeError:
                    scores[lang_pair][domain] = round(data[0]['score'], 1)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # If the file doesn't exist, set the score to "NA"
            scores[lang_pair][domain] = "NA"

# Convert the scores dictionary to a list of dictionaries
scores_list = list(scores.values())

# Write the scores to a CSV file
with open('bleu_scores.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['lang-pair'] + domain_list)
    writer.writeheader()
    writer.writerows(scores_list)




# COMET
# Initialize a dictionary to store the scores
comet_scores = {lang_pair: {'lang-pair': lang_pair} for lang_pair in lang_pairs}

# Loop over each domain
for domain in domain_list:
    for lang_pair in lang_pairs:
        # Construct the file path
        file_path = f'/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.comet'
        try:
            # Try to open the file for this domain-language pair
            with open(file_path, 'r') as f:
                # Read the first line
                line = f.readline()
                parts = line.split('score: ')
                # Split the line on 'score: '
                if len(parts) < 2:
                    # If not, set the score to "NA"
                    score = "NA"
                    comet_scores[lang_pair][domain] = score
                else:
                    # If it did, the second part is the score
                    score = float(parts[1])
                # Add the score to the dictionary
                    comet_scores[lang_pair][domain] = round(score * 100, 1)
        except FileNotFoundError:
            # If the file doesn't exist, set the score to "NA"
            comet_scores[lang_pair][domain] = "NA"

scores_list = list(comet_scores.values())

# Write the scores to a CSV file
with open('nllb_comet_scores.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['lang-pair'] + domain_list)
    writer.writeheader()
    writer.writerows(scores_list)

