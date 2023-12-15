# LLM-Dom-Ad

Here we release our data splits for domain adaptation experiments. 

We include a 'train' split of 5000 sentence pairs and a 'test' split of 500 pairs.

We cover 7 languages paired with English: Czech (cs), German (de), Finnish (fi), French (fr), Lithuanian (lt), Romanian (ro), and Tamil (ta). We also cover 7 domains: EMEA, JRC-Acquis, KDE4, OpenSubtitles, QED, Tanzil, and TED2020. 

All data was obtained from [OPUS](https://opus.nlpl.eu/).

If you use this data, please cite our paper: [link coming]

We also include our fork of the lm-evaluation-harness, which can be installed in the same way as the original, and for running inference see the example script in `./runs`. Our requirements.txt file is our complete conda environment so ignore if you already have cuda installed. We ran inference on 1xA100 80GB GPU, but it's possible to run LLaMa-2-13B on multiple smaller GPUs. We use the HuggingFace implementation of LLaMa-2-13B.
