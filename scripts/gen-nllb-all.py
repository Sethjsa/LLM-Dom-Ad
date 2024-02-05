from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm
import torch

def generate_translations():
    # Initialize the model and tokenizer
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-1.3B", token=True)
    model = model.to('cuda')
    

    domain_list = ['EMEA', 'Tanzil', 'JRC-Acquis', 'KDE4', 'QED', 'CCAligned', 'TED2020', 'OpenSubtitles']
    pair_list = ['en-fi', 'en-fr', 'de-en', 'en-lt', 'en-ta', 'en-ro', 'cs-en']
    from_en_list = ['fi', 'fr', 'de', 'lt', 'ta', 'ro', 'cs']
    to_en_list = ["cs", "fr", "lt", "ro"]

    for domain in domain_list:
        for lang_pair in pair_list:

            # Split the language pair into source and target languages
            src_lang, tgt_lang = lang_pair.split('-')

            if src_lang == "de" or src_lang == "cs":
                src_lang, tgt_lang = tgt_lang, src_lang
                
            direction = f"{src_lang}-{tgt_lang}"

            print(f"Generating translations for {domain} in {direction}...")

            # Read the source sentences
            try:


                with open(f"/home/saycock/LLM-Dom-Ad/{domain}/{domain}.{lang_pair}.test.{src_lang}", "r") as f:
                    sents = [line.strip() for line in f.readlines()]

                # Save the source sentences
                with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.src", "w") as f:
                    f.write("\n".join(sents))

                # Tokenize the sentences
                tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B", token=True, src_lang="eng_Latn")
                # inputs = tokenizer(sents, return_tensors="pt", padding=True, truncation=True)

                if tgt_lang == "en":
                    outlangcode = "eng_Latn"
                if tgt_lang == "de":
                    outlangcode = "deu_Latn"
                if tgt_lang == "fr":
                    outlangcode = "fra_Latn"
                if tgt_lang == "fi":
                    outlangcode = "fin_Latn"
                if tgt_lang == "lt":
                    outlangcode = "lit_Latn"
                if tgt_lang == "ta":
                    outlangcode = "tam_Taml"
                if tgt_lang == "ro":
                    outlangcode = "ron_Latn"
                if tgt_lang == "cs":
                    outlangcode = "ces_Latn"

                batch_size = 8

                output_result = []

                for idx in tqdm(range(0, len(sents), batch_size)):
                    start_idx = idx
                    end_idx = idx + batch_size
                    inputs = tokenizer(sents[start_idx: end_idx], padding=True, truncation=True, max_length=175, return_tensors="pt").to('cuda')

                    with torch.no_grad():
                        translated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id[f"{outlangcode}"], 
                                        max_length=128, num_beams=5, num_return_sequences=1, early_stopping=True)

                    output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
                    output_result.extend(output)

                # Generate translations
                # outputs = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"])

                # Decode the translations
                # translations = [tokenizer.batch_decode(output, skip_special_tokens=True) for output in outputs]

                # Save the translations
                with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.eval", "w") as f:
                    f.write("\n".join(output_result))



                # ORIGINAL
                # tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B", token=True, src_lang="eng_Latn")
                # inputs = tokenizer(sents, return_tensors="pt", padding=True, truncation=True)

                # # Generate translations
                # outputs = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id[f"{output}"])

                # # Decode the translations
                # translations = [tokenizer.batch_decode(output, skip_special_tokens=True) for output in outputs]

                # # Save the translations
                # with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.eval", "w") as f:
                #     f.write("\n".join(translations))

                # Read the reference target sentences
                with open(f"/home/saycock/LLM-Dom-Ad/{domain}/{domain}.{lang_pair}.test.{tgt_lang}", "r") as f:
                    refs = [line.strip() for line in f.readlines()]

                # Save the reference target sentences
                with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.ref", "w") as f:
                    f.write("\n".join(refs))


                with open(f"/home/saycock/LLM-Dom-Ad/{domain}/{domain}.{lang_pair}.test.{src_lang}", "r") as f:
                    sents = [line.strip() for line in f.readlines()]

                # Save the source sentences
                with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.src", "w") as f:
                    f.write("\n".join(sents))
                
            except FileNotFoundError:
                pass


            ###########################################################
            ###########################################################


            # FROM ENGLISH 
            if tgt_lang in to_en_list:
                src_lang, tgt_lang = tgt_lang, src_lang
                direction = f"{src_lang}-{tgt_lang}"
                print(f"Generating translations for {domain} in {direction}...")

                try:
                    with open(f"/home/saycock/LLM-Dom-Ad/{domain}/{domain}.{lang_pair}.test.{src_lang}", "r") as f:
                        sents = [line.strip() for line in f.readlines()]

                    # Save the source sentences
                    with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.src", "w") as f:
                        f.write("\n".join(sents))


                    # Tokenize the sentences
                    

                    if src_lang == "en":
                        outlangcode = "eng_Latn"
                    if src_lang == "de":
                        outlangcode = "deu_Latn"
                    if src_lang == "fr":
                        outlangcode = "fra_Latn"
                    if src_lang == "fi":
                        outlangcode = "fin_Latn"
                    if src_lang == "lt":
                        outpoutlangcodeut = "lit_Latn"
                    if src_lang == "ta":
                        outlangcode = "tam_Taml"
                    if src_lang == "ro":
                        outlangcode = "ron_Latn"
                    if src_lang == "cs":
                        outlangcode = "ces_Latn"

                    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B", token=True, src_lang=outlangcode)
                    # inputs = tokenizer(sents, return_tensors="pt", padding=True, truncation=True)
                    
                    output_result = []

                    for idx in tqdm(range(0, len(sents), batch_size)):
                        start_idx = idx
                        end_idx = idx + batch_size
                        inputs = tokenizer(sents[start_idx: end_idx], padding=True, truncation=True, max_length=175, return_tensors="pt").to('cuda')

                        with torch.no_grad():
                            translated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"], 
                                            max_length=128, num_beams=5, num_return_sequences=1, early_stopping=True)

                        output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
                        output_result.extend(output)

                    # Generate translations
                    # outputs = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"])

                    # Decode the translations
                    # translations = [tokenizer.batch_decode(output, skip_special_tokens=True) for output in outputs]

                    # Save the translations
                    with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.eval", "w") as f:
                        f.write("\n".join(output_result))

                    # Read the reference target sentences
                    with open(f"/home/saycock/LLM-Dom-Ad/{domain}/{domain}.{lang_pair}.test.{tgt_lang}", "r") as f:
                        refs = [line.strip() for line in f.readlines()]

                    # Save the reference target sentences
                    with open(f"/home/saycock/LLM-Dom-Ad/tests/{domain}-{lang_pair}.ref", "w") as f:
                        f.write("\n".join(refs))
                except FileNotFoundError:
                    pass


# Call the function with your domain list and language
generate_translations()