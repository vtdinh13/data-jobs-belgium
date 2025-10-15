import pandas as pd
import time
import requests
import os
import json
import re
from dotenv import load_dotenv

def load_api_key():
    load_dotenv()
    return os.getenv('SEARCH_API')


def ingest_data(job_titles: list, locations: list) -> pd.DataFrame:
    api_key = load_api_key()

    os.makedirs('BE_Jobs', exist_ok=True)

    all_jobs_df = pd.DataFrame()
    url = "https://www.searchapi.io/api/v1/search"

    for j in job_titles:
        for l in locations:
            query = f'{j}{l}'
            params = {
                'engine': 'google_jobs', 
                'q': query,
                'api_key': api_key,
                'gl': 'be'
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                with open(f"be/{j}_{l}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                job_listings = data.get('jobs', [])
                if job_listings:
                    jobs_df = pd.DataFrame(job_listings)
                    all_jobs_df = pd.concat([all_jobs_df, jobs_df], ignore_index=True)
            else:
                print(f"Error: Received status code {response.status_code} for {j}")
            time.sleep(1)
     
    all_jobs_df.to_csv('jobs.csv', index=False)

def normalize_dataframe(df:pd.DataFrame) -> pd.DataFrame:

    # make everything lowercase
    str_cols = df.select_dtypes(['object']).columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.lower())

    # drop columns
    columns_to_drop = ['extensions', 'apply_link', 'sharing_link', 'thumbnail']
    df.drop(columns=columns_to_drop, inplace=True)

    # normalize job titles
    de_mask = df['title'].str.contains('engin', na=False)
    df.loc[de_mask, 'title_cleaned'] = 'data engineer'

    ds_mask = df['title'].str.contains('scien', na=False)
    df.loc[ds_mask, 'title_cleaned'] = 'data scientist'

    da_mask = df['title'].str.contains('anal', na=False)
    df.loc[da_mask, 'title_cleaned'] = 'data analyst'

    advisor = df['title'].str.contains('advisor', na=False)
    df.loc[advisor, 'title_cleaned'] = 'data consultant'

    internship_mask = df['title'].str.contains(r'(traineeship|internship)')
    df.loc[internship_mask, 'title_cleaned'] = 'internship'

    # normalize location
    ghent = df['location'].str.contains('ghent', na=False)
    df.loc[ghent, 'location'] = 'ghent'

    antwerp = df['location'].str.contains(r'(antwerp|schoten)', na=False)
    df.loc[antwerp, 'location'] = 'antwerp'
    
    return df