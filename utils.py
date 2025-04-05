# utils.py

import json
import re
import pandas as pd
from datetime import datetime
from openai import OpenAI

DEFAULT_GEN_KWARGS = {
    "max_tokens": 2048,
    "stream": False,
    "top_p": 0.95,
    "temperature": 1.0
}

url = "http://10.32.15.88:6000/generate"

def preprocess_text(text, max_length=2000):
    """
    Preprocess text by splitting into chunks if necessary.
    Adjust max_length based on model's context window.
    """
    paragraphs = text.strip().split('\n\n')
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 < max_length:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk)
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


import requests

def extract_information(text, **gen_kwargs):
    example_json = """
Example JSON format:
{
  "dates": [
    {
      "year": "xxxx",
      "event": "Some historical event"
    }
  ],
  "persons": [
    {
      "name": "Person Name",
      "role": "Role or significance"
    }
  ],
  "relationships": [
    {
      "person": "Person A",
      "relationship": "Relationship type or context",
      "other_person": "Person B"
    }
  ]
}
"""
    prompt = (
        "Please extract all dates, persons, and relationships between persons "
        "from the following text, with all dates in YYYY format. Provide results in JSON format.\n\n"
        f"{example_json}\n\nText:\n{text}"
    )

    payload = {
        "prompt": prompt,
        **gen_kwargs
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    generated_text = response_data.get('text', '')
    
    if isinstance(generated_text, list):
        generated_text = " ".join(generated_text)

    json_pattern = r'```json(.*?)```'
    match = re.search(json_pattern, generated_text, re.DOTALL)

    if match:
        json_str = match.group(1).strip()
    else:
        json_pattern = r'({.*})'
        match = re.search(json_pattern, generated_text, re.DOTALL)
        json_str = match.group(1).strip() if match else None

    if json_str:
        try:
            structured_output = json.loads(json_str)
            return structured_output
        except json.JSONDecodeError:
            return None
    return None


def process_text(text, **gen_kwargs):
    """
    Process the input text and extract structured information.
    """
    chunks = preprocess_text(text)
    all_dates = []
    all_persons = []
    all_relationships = []

    for chunk in chunks:
        extracted = extract_information(chunk, **gen_kwargs)
        if extracted:
            # Append dates
            dates = extracted.get('dates', [])
            for date in dates:
                if 'year' in date and 'event' in date:
                    all_dates.append({
                        'year': date['year'],
                        'event': date['event']
                    })

            # Append persons
            persons = extracted.get('persons', [])
            for person in persons:
                if 'name' in person and 'role' in person:
                    all_persons.append({
                        'name': person['name'],
                        'role': person['role']
                    })

            # Append relationships
            relationships = extracted.get('relationships', [])
            for relation in relationships:
                if 'person' in relation and 'relationship' in relation and 'other_person' in relation:
                    all_relationships.append({
                        'person': relation['person'],
                        'relationship': relation['relationship'],
                        'other_person': relation['other_person']
                    })

    dates_df = pd.DataFrame(all_dates).drop_duplicates().reset_index(drop=True)
    persons_df = pd.DataFrame(all_persons).drop_duplicates().reset_index(drop=True)
    relationships_df = pd.DataFrame(all_relationships).drop_duplicates().reset_index(drop=True)

    return dates_df, persons_df, relationships_df


def quality_estimation(dates_df, persons_df, relationships_df):
    """
    Perform quality estimation and self-correction on the extracted data.
    """

    def validate_year(year):
        try:
            year_int = int(year)
            # Basic validation: year should be between 1 and current year
            if 1 <= year_int <= datetime.now().year:
                return True
            else:
                return False
        except:
            return False

    if not dates_df.empty:
        dates_df['valid_year'] = dates_df['year'].apply(validate_year)
        dates_df = dates_df[dates_df['valid_year']].drop(columns=['valid_year']).reset_index(drop=True)

    # 2. Remove duplicate persons (by name)
    if not persons_df.empty:
        persons_df = persons_df.drop_duplicates(subset=['name']).reset_index(drop=True)

    # 3. Filter relationships to only those that appear in persons_df
    if not relationships_df.empty and not persons_df.empty:
        required_columns = {'person', 'other_person'}
        if required_columns.issubset(relationships_df.columns):
            relationships_df = relationships_df[
                relationships_df['person'].isin(persons_df['name']) &
                relationships_df['other_person'].isin(persons_df['name'])
            ].reset_index(drop=True)

    return dates_df, persons_df, relationships_df
