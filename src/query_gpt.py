from openai import OpenAI
import os
import pandas as pd
import string
import json
from src.questions import PROJECT_STATUS


def new_openai_session(openai_apikey):
    os.environ["OPENAI_API_KEY"] = openai_apikey
    client = OpenAI()
    gpt_model = "gpt-4o" 
    max_num_chars = 10
    return client, gpt_model, max_num_chars

def create_gpt_messages(query, run_on_full_text):
    text_label = "collection of text excerpts"
    if run_on_full_text:
        text_label = "document"
    # Explicit system instruction: GPT must reply with a JSON object having a single key "answer" whose value is either "yes" or "no".
    system_command = (
        "You are an assistant that answers questions with a single word response. "
        "When given a prompt, you must return your answer as a valid JSON object with exactly one key: 'answer'. "
        "The value must be either 'yes' or 'no', with no additional text, spaces, or formatting. "
        "For example: { \"answer\": \"yes\" } or { \"answer\": \"no\" }."
    )
    return [
        {"role": "system", "content": system_command},
        {"role": "user", "content": query},
    ]

def chat_gpt_query(gpt_client, gpt_model, msgs):
    response = gpt_client.chat.completions.create(
        model=gpt_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=msgs,
    )
    # For safety, parse the returned content as JSON.
    content = response.choices[0].message.content.strip()
    try:
        json_response = json.loads(content)
    except Exception as e:
        # If parsing fails, log the content and raise the error.
        raise ValueError(f"Failed to parse JSON from GPT response: {content}\nError: {e}")
    return json_response

def fetch_variable_info(gpt_client, gpt_model, query, run_on_full_text):
    msgs = create_gpt_messages(query, run_on_full_text)
    return chat_gpt_query(gpt_client, gpt_model, msgs)

def query_gpt_for_relevance_iterative(df, target_questions, run_on_full_text, gpt_client, gpt_model):
    """
    Iterates through target_questions for each article in df.
    For each article, it asks each question until one returns "yes".
    If any question returns "yes", the article is marked as irrelevant ("no").
    Otherwise, it's marked as relevant ("yes").
    
    Returns:
        pd.DataFrame: A DataFrame with one row per article including the article index, title, and a "relevant" flag.
    """
    results = []
    for index, row in df.iterrows():
        is_irrelevant = False
        for question in target_questions:
            query = (
                f'Forget all previous instructions. Answer the following question to the best of your ability: {question}. '
                f'Please analyze the headline and respond ONLY as JSON in the format exactly like: '
                f'{{ "answer": "yes" }} or {{ "answer": "no" }}. '
                f'Here is the headline: {row["text_column"]}'
            )
            response_dict = fetch_variable_info(gpt_client, gpt_model, query, run_on_full_text)
            raw_answer = response_dict.get("answer", "no")
            # Clean up the response.
            clean_answer = raw_answer.strip().lower()
            if clean_answer not in ["yes", "no"]:
                # Log a warning and default to 'no' so that the article is not considered irrelevant
                print(f"Warning: Unrecognized answer format '{clean_answer}' from GPT. Defaulting to 'no'.")
                clean_answer = "no"
            if clean_answer == "yes":
                is_irrelevant = True
                print("Skipping article due to query: ", query)
                break
        results.append({
            "index": index,
            "title": row.get("title", "Unknown Title"),
            "relevant": "no" if is_irrelevant else "yes"
        })
    return pd.DataFrame(results)


def query_gpt_for_project_details(gpt_client, gpt_model, article_text, tech_list):
    """
    Uses GPT to extract project details from the article text in two rounds.
    Returns a dictionary with all keys. Missing details are returned as empty strings.
    """
    tech_list_str = ", ".join(tech_list)
    
    # --- First round: Core details ---
    core_prompt = (
        "You are an information extraction assistant. Given the article text below, extract the following core details if available. "
        "You may need to infer them:\n"
        "- scale: one of 'pilot', 'demonstration', or 'full scale'\n"
        "- project_name: the name of the project mentioned\n"
        "- timeline: the year when it will be operative (skip if not explicitly stated)\n"
        f"- technology: one of the following: {tech_list_str}\n\n"
        "Return your answer as a JSON object with keys: 'scale', 'project_name', 'timeline', 'technology'. "
        "For any missing detail, return an empty string.\n\n"
        "Article text:\n\"\"\"\n" + article_text + "\n\"\"\""
    )
    
    msgs_core = [
        {"role": "system", "content": "You are an assistant that extracts project details from text."},
        {"role": "user", "content": core_prompt},
    ]
    
    try:
        response_core = gpt_client.chat.completions.create(
            model=gpt_model,
            temperature=0,
            messages=msgs_core,
        )
        output_core = response_core.choices[0].message.content.strip()
        if output_core.startswith("```json"):
            output_core = output_core[len("```json"):].strip()
        if output_core.endswith("```"):
            output_core = output_core[:-3].strip()
        core_details = json.loads(output_core)
    except Exception as e:
        print(f"Error extracting core project details: {e}")
        core_details = {}
    
    for key in ['scale', 'project_name', 'timeline', 'technology']:
        if key not in core_details:
            core_details[key] = ""
    
    # --- Second round: Additional details ---
    if any(core_details[key] for key in ['scale', 'project_name', 'timeline', 'technology']):
        additional_prompt = (
            "You are an assistant that extracts additional project details from text. Given the article text below, "
            "extract the following details if available, inferring when necessary:\n"
            "- company: the company leading the project\n"
            "- projects mentioned: the number of projects mentioned (Multiple or one main one)\n"
            "- partners: the names of partner organizations\n"
            "- continent: the continent where the project is located\n"
            "- country: the country where the project is located\n"
            f"- project_status: one of the following statuses: {', '.join(PROJECT_STATUS)}\n\n"
            "Return your answer as a JSON object with keys: 'company', 'projects mentioned', 'partners', 'continent', 'country', 'project_status'. "
            "For any missing detail, return an empty string. If the article is irrelevant, include a key 'irrelevant' with value true.\n\n"
            "Article text:\n\"\"\"\n" + article_text + "\n\"\"\""
        )
        
        msgs_additional = [
            {"role": "system", "content": "You are an assistant that extracts additional project details from text."},
            {"role": "user", "content": additional_prompt},
        ]
        
        try:
            response_additional = gpt_client.chat.completions.create(
                model=gpt_model,
                temperature=0,
                messages=msgs_additional,
            )
            output_additional = response_additional.choices[0].message.content.strip()
            if output_additional.startswith("```json"):
                output_additional = output_additional[len("```json"):].strip()
            if output_additional.endswith("```"):
                output_additional = output_additional[:-3].strip()
            additional_details = json.loads(output_additional)
        except Exception as e:
            print(f"Error extracting additional project details: {e}")
            additional_details = {}
        
        for key in ['company', 'partners', 'continent', 'country', 'project_status']:
            if key not in additional_details:
                additional_details[key] = ""
    else:
        additional_details = {
            'company': "",
            'projects mentioned': "",
            'partners': "",
            'continent': "",
            'country': "",
            'project_status': ""
        }
    
    combined_details = {**core_details, **additional_details}
    return combined_details
