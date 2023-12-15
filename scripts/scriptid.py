from stopes.pipelines.monolingual.utils.predict_script import find_lang_script
import importlib

lang="en"

with importlib.resources.path(
    "stopes.pipelines.monolingual", config.language_script_filename
) as path:
    lang_script = find_lang_script(lang, path)