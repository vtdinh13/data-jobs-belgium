import plotly.express as px
import pandas as pd


def create_bar_chart_all_jobs(df:pd.DataFrame):

    df['clean_title_cap'] = df['title_cleaned'].str.title()
    df['location_cap'] = df['location'].str.title()

    grouped = df.groupby(by=['clean_title_cap', 'location_cap']).size().reset_index(name='count')
    totals = grouped.groupby('clean_title_cap')['count'].sum().sort_values(ascending=False)
    grouped['clean_title_cap'] = pd.Categorical(grouped['clean_title_cap'], categories=totals.index, ordered=True)
    category_order = totals.index.tolist()

    fig = px.bar(
        data_frame = grouped,
        barmode = 'stack',
        x = 'clean_title_cap', 
        y = 'count', 
        color = 'location_cap', 
        category_orders = {'clean_title_cap': category_order}
    )

    fig.update_layout(
        title = 'Added Job Postings by Job Title',
        xaxis_title = 'Job Titles',
        yaxis_title = 'Number of Job Postings Added',
        legend_title_text = 'Location'
    )

    return fig.show()