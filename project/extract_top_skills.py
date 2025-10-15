import pandas as pd
from bs4 import BeautifulSoup
import json
from pathlib import Path
from pydantic_ai import Agent
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessagesTypeAdapter
from logs import log_interaction_to_file
from tqdm import tqdm


def clean_html(raw_html):
    return BeautifulSoup(raw_html, 'html.parser').get_text(separator='\n')

def clean_description_html(df:pd.DataFrame):
    df['description'] = df['description'].apply(clean_html)
    return df

def build_prompt(row):
  return f"""

JOB_TITLE: "{row['title_cleaned']}"

TEXT:
\"\"\"{row['description']}\"\"\"

YOUR TASK:
- Extract skills that are explicitly present. No guesses. Be specific. For example, SQL and Python are skills.
- Extract between 5 to 10 skills.
- Extract between 5 to 10 technologies required.
- For each skill, include: skill name, category include hard or soft, types of tools or technologies mentioned, evidence (verbatim phrase), confidence between 0 and 1. Be strict with this instruction.
- Please provide an answer. No answer is not an option.
""".strip()

def create_prompt_list(df:pd.DataFrame) -> list:
   
   df_cleaned = clean_description_html(df)
   prompts = [build_prompt(r) for _, r in df_cleaned.iterrows()]
   return prompts

context = """
You are an information extraction expert. Extract only what is explicitly supported by the provided text. Return response in a list with JSON elements.
"""

class SkillsList(BaseModel):
    job_title: str
    skills:list[str]

def create_skills_extractor():
    skills_extractor = Agent(
        model='gpt-4o-mini',
        output_type=SkillsList, 
        instructions=context
    )
    return skills_extractor

async def get_skills_data(prompt:str):
    skills_extractor = create_skills_extractor()
    result = await skills_extractor.run(prompt)
    return result

async def iterate_get_skills_data(df:pd.DataFrame):
    prompts = create_prompt_list(df)
    skills_extractor = create_skills_extractor()

    for p in tqdm(prompts):
        result = await skills_extractor.run(user_prompt=p)

        log_interaction_to_file(
            agent = skills_extractor,
            messages = result.new_messages(),
            source='user'
        )
        print()


def load_log_file(log_file):
    with open(log_file, 'r') as f_in:
        log_data = json.load(f_in)
        log_data['log_file'] = log_file
    return log_data


def parse_json(directory:str) -> pd.DataFrame:
    LOG_DIR = Path(directory)

    rows = []
    for log in LOG_DIR.glob('*.json'):
        log_record = load_log_file(log)
        row = log_record['messages'][1]['parts'][0]['args']
        item = json.loads(row)

        job_title = item['job_title']

        for s in item.get("skills", []):
            try:
                skill = json.loads(s) 
                skill['job_title'] = job_title
                rows.append(skill)
            except json.JSONDecodeError:
                rows.append({'job_title': job_title, 'raw_skill': s})
    return pd.DataFrame(rows)[['job_title', 'skill_name', 'category', 'types_of_tools_or_technologies', 'evidence']]

mapping = {
    'statistical modelling': 'statistical analysis and modelling',
    'statistical modeling': 'statistical analysis and modelling',
    'statistical analysis': 'statistical analysis and modelling', 
    'statistics': 'statistical analysis and modelling',
    'biomedical data analysis': 'data analysis',
    'relational modelling (sql)' : 'relational data modelling',
    'relational database': 'relational data modelling',
    'visualization tools': 'data visualization',
    'data science leadership': 'leadership',
    'data preprocessing': 'data processing',
    'data wrangling': 'data processing',
    'python programming': 'python',
    'lua': 'lua',
    'programming languages': 'programming',
    'team support': 'collaboration',
    'coaching and guiding': 'leadership',
    'collaborative skills': 'collaboration',
    'data modeling': 'data modelling',
    'communicatie': 'communication',
    'analytical thinking': 'analytical skills', 
    'analytical mindset': 'analytical skills',
    'problem identification': 'problem solving',
    'problem-solving': 'problem solving',
    'team collaboration': 'collaboration',
    'team work': 'collaboration',
    'bilingual (french and english)': 'french and english',
    'team building': 'collaboration',
    'communication skills': 'communication',
    'curiosity and learning orientation': 'curiosity',
    'data mining': 'data processing',
    'teamwork': 'collaboration',
    'algorithm development': 'algorithm development and tuning',
    'algorithm tuning': 'algorithm development and tuning',
    'datamodellering': 'data modelling',
    'microsoft excel': 'excel',
    'data quality assessment': 'data quality assessment and optimization',
    'data quality optimization': 'data quality assessment and optimization',
    'ai knowledge': 'ai',
    'visualisatie': 'data visualization',
    'etl processes':'etl',
    'data-analyse': 'data analysis',
    'dutch proficiency': 'dutch',
    'english proficiency': 'english',
    'data-verzameling': 'data collection',
    'problem-solving mindset': 'problem solving',
    'english fluency': 'english', 
    'samenwerken': 'collaboration',
    'power query': 'etl',
    'fluency in english': 'english'
}

def normalize_skills(df:pd.DataFrame):
    df['skill_name'] = df['skill_name'].str.lower()
    df['skill_name'] = df['skill_name'].map(mapping).fillna(df['skill_name'])
    return df


