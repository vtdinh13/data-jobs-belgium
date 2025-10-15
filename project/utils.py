import pandas as pd
import numpy as np

import ast
from datetime import datetime, timedelta
import re
import json
import random
from cycler import cycler
from pathlib import Path

from PIL import Image
from wordcloud import WordCloud
import plotly.express as px
import matplotlib.pyplot as plt

from extract_top_skills import parse_json
from sentence_transformers import SentenceTransformer
from scipy.cluster.hierarchy import linkage, dendrogram


## Dates 

def normalize_json(df = pd.DataFrame):

    df['detected_extensions'] = df['detected_extensions'].apply(lambda x: ast.literal_eval(x) if isinstance(x,str) else x)

    mask = df['detected_extensions'].apply(lambda x:isinstance(x, dict))
    posted_at = pd.json_normalize(df.loc[mask, 'detected_extensions'])
    complete_df = pd.concat([df, posted_at], axis=1)
    complete_df.drop(columns='detected_extensions', inplace=True)
    return complete_df

def calculate_date(num_of_days_ago_text:str):
    date_extracted_data = datetime.today().date() - timedelta(days=2)

    if isinstance(num_of_days_ago_text,str):
        match = re.search(r'(\d+)', num_of_days_ago_text)
        if match:
            days = int(match.group(1))
            return datetime.today().date() - timedelta(days=days)
    return date_extracted_data


#### keep colors consistent

def rgb_to_hex(rgb_str):
    r, g, b = map(int, re.findall(r'\d+', rgb_str))
    return f'#{r:02x}{g:02x}{b:02x}'

palette = [rgb_to_hex(c) for c in px.colors.qualitative.Safe]

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return random.choice(palette)

####
BASE = Path(__file__).resolve().parent
oval_path = BASE / 'oval.png'

## Visualizations
def create_jobs_wc(df: pd.DataFrame):
    comp_names = df['Company Name'].str.title().value_counts().reset_index()

    vib_map = {'Vib': 'VIB'}
    comp_names['Company Name'] = comp_names['Company Name'].map(vib_map).fillna(comp_names['Company Name'])
    comp_count = dict(zip(comp_names['Company Name'], comp_names['count']))

    mask = np.array(Image.open(oval_path))

    wc = WordCloud(width=400, height=400, background_color='white', 
                   mask=mask, contour_width=1, contour_color='white',
                   color_func=color_func).generate_from_frequencies(comp_count)

    fig = plt.figure(figsize=(8,8), dpi=120)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    return fig

def create_skills_dendrogram(df: pd.DataFrame, job_titles: list):
    unique_skills = df[df['Job Title'].isin(job_titles)]['skill_name'].unique()

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(unique_skills)
    Z = linkage(embeddings, method="ward")
    fig = plt.figure(figsize=(8, 8))
    dendrogram(Z, labels=unique_skills, orientation='right')
    plt.rcParams['axes.prop_cycle'] = cycler(color=palette)
    # plt.title("Required Skills According to Job Postings")
    return fig

def create_job_freq(df:pd.DataFrame):
    grouped = df.groupby(by=['Job Title', 'Location']).size().reset_index(name='count')
    totals = grouped.groupby('Job Title')['count'].sum().sort_values(ascending=False)
    grouped['Job Title'] = pd.Categorical(grouped['Job Title'], categories=totals.index, ordered=True)
    category_order = totals.index.tolist()

    fig = px.bar(
    data_frame=grouped,barmode='stack', height=400,
    x='Job Title', y='count', color='Location', 
    category_orders={'title_cleaned': category_order},
    color_discrete_sequence=px.colors.qualitative.Safe
)   
    fig.update_layout(yaxis_title = 'Number of Jobs')
    return fig