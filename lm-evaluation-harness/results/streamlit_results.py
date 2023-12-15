import streamlit as st
import pandas as pd
import os

# Function to load data from CSV files
def load_data(language, metric):
    file_name = f"/home/saycock/scratch/topic/lm-evaluation-harness/results/{language}_{metric}_results.csv"
    if os.path.isfile(file_name):
        data = pd.read_csv(file_name, sep="\t", header=None)
        data.columns = ["Modifier", "Language", "EMEA","JRC-Acquis","KDE4","OpenSubtitles","QED","Tanzil","TED2020","CCAligned"]
        return data
    return None

# Streamlit app
st.title("Results Table")

# Sidebar for user input
languages = ["en-cs", "en-de", "en-fi", "en-fr", "en-lt", "en-ro", "en-ta"]
metrics = ["bleu", "comet", "langids"]

selected_language = st.sidebar.selectbox("Select Language:", languages)
selected_metric = st.sidebar.radio("Select Metric:", metrics)

# Load and display data
data = load_data(selected_language, selected_metric)

if data is not None:
    st.write(f"Results for {selected_language} - {selected_metric.capitalize()}:")
    st.dataframe(data)
else:
    st.warning("Data not found for the selected language and metric.")
