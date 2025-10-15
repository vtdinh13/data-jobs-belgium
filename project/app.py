import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import streamlit as st
import utils
from datetime import datetime
import plotly.express as px
from streamlit_dynamic_filters import DynamicFilters
from pathlib import Path

BASE = Path(__file__).resolve().parent
jobs_df = pd.read_csv(BASE.parent/'data'/'jobs_final.csv')
skills_df = pd.read_csv(BASE.parent/'data'/'skills.csv')

st.set_page_config(layout="wide")

# ---------------------------
# 2) SIDEBAR FILTERS
# ---------------------------

st.markdown(
    """
    ## 🇧🇪 Simplifying Your Data Job Search in Belgium
    
    I built this dashboard to provide insights into job opportunities and the in-demand skills needed to land a data role in Belgium today.

    Using [searchapi.io](http://searchapi.io/), I curated the latest job postings across Belgium's tech hubs and extracted the most in-demand skills with `gpt-40-mini` and hierarchical clustering using the Ward distance metric. The dataset covers jobs posted between September 19 and October 10, 2025, helping you develop the right skills or match your expertise with current market demands.
    
    """
    )
dynamic_filters = DynamicFilters(jobs_df, filters=['Job Title', 'Company Name', 'Location', 'Schedule'])

with st.sidebar:
    st.write(' ')
    st.write(' ')

    st.header("🔍 Select your desired options:")
    dynamic_filters.display_filters()


    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')
   


    st.markdown("""
    <div style="
        background-color: #E8F5E9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        ">
        💬 <b> Have feedback or suggestions? </b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("I'd love to hear from you! Let's connect on [LinkedIn](https://www.linkedin.com/in/vancesca-dinh/).")



filtered_df = dynamic_filters.filter_df()
    # selected_jobs = st.multiselect(
    #     "Job Title",
    #     options=sorted(visualization_df["Job Title"].unique()),
    #     default=sorted(visualization_df["Job Title"].unique())[:1],  # preselect a few
    # )
    # # (Optional extra filters—easy to extend later)
    # # selected_locations = st.multiselect("Location", options=sorted(df["location"].unique()))
    # selected_companies = st.multiselect("Company Name", options=sorted(skills_df["company_name"].unique()))

# filtered_jobs = visualization_df[visualization_df['Job Title'].isin(selected_jobs)]
# filtered_jobs_companies = filtered_jobs[filtered_jobs['Company Name'].isin(selected_companies)]


# @st.cache_data


# ---------------------------
# Top half
# ---------------------------


top_left, top_right = st.columns(2)

with top_left:
    
    job_freq = utils.create_job_freq(filtered_df)
    st.plotly_chart(job_freq, use_container_width=False)

with top_right:

    wc = utils.create_jobs_wc(filtered_df)
    st.pyplot(wc, width='stretch')


# st.divider()
# ---------------------------
# Bottom half
# ---------------------------
bottom_left, bottom_right = st.columns([1.4,1])

selected_jobs = filtered_df.get('Job Title', [])
with bottom_left:
    den = utils.create_skills_dendrogram(df=skills_df, job_titles=selected_jobs)
    st.pyplot(den, width='content')

    st.markdown('🌳 *The dendrogram displays the skills required for your desired job title(s). ' \
    'Similar skills are clustered together and displayed in the same color.*')


with bottom_right:
    # Collapsible expander
    with st.expander("Show table", expanded=True):
        st.data_editor(
            filtered_df,
            hide_index=True,
            width='content',
            column_config={
                "Apply Link": 
                st.column_config.LinkColumn(
                    label="Link",
                    display_text="Apply Now"
                )
            }
        )

        # Download the same data as CSV
        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download table",
            data=csv_bytes,
            file_name=f'be-jobs-{datetime.today()}.csv',
            # mime="text/csv",
            # help="Download the currently filtered rows as a CSV"
        )



