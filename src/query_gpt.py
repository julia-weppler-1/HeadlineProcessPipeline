from openai import OpenAI
import os
import pandas as pd
import string
import json
from src.questions import PROJECT_STATUS

def new_openai_session(openai_apikey):
    os.environ["OPENAI_API_KEY"] = openai_apikey
    client = OpenAI()
    gpt_model = "gpt-4.1" 
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
        top_p=1,      
        frequency_penalty=0,
        seed=999,
        presence_penalty=0,
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

def extract_numeric_facts_with_quotes(gpt_client, gpt_model, article_text: str, domain: str = "steel") -> dict:
    """
    Domain-aware extraction of numbers + supporting quotes.
    steel/iron -> ask 5 questions
    cement     -> ask 2 questions (investment + capture only)

    ANSWER FIELDS: digits ok, but ALL units & currencies in plain English words.
    QUOTE FIELDS: short verbatim substrings from the text.
    """
    domain = (domain or "").strip().lower()
    is_cement = (domain == "cement")

    if is_cement:
        schema = (
            "{\n"
            '  "cc_capacity": "<value + units in plain English words or no response>",\n'
            '  "cc_quote": "<short verbatim snippet>",\n'
            '  "investment": "<value + currency in plain English words or no response>",\n'
            '  "investment_quote": "<short verbatim snippet>"\n'
            "}\n"
        )
        q_block = (
            "1) What is the expected carbon capture capacity?\n"
            "2) What is the investment size?\n"
        )
        keys = ["cc_capacity","cc_quote","investment","investment_quote"]
    else:
        schema = (
            "{\n"
            '  "cc_capacity": "<value + units in plain English words or no response>",\n'
            '  "cc_quote": "<short verbatim snippet>",\n'
            '  "h2_capacity": "<value + units in plain English words or no response>",\n'
            '  "h2_quote": "<short verbatim snippet>",\n'
            '  "investment": "<value + currency in plain English words or no response>",\n'
            '  "investment_quote": "<short verbatim snippet>",\n'
            '  "iron_capacity": "<value + units in plain English words or no response>",\n'
            '  "iron_quote": "<short verbatim snippet>",\n'
            '  "steel_capacity": "<value + units in plain English words or no response>",\n'
            '  "steel_quote": "<short verbatim snippet>"\n'
            "}\n"
        )
        q_block = (
            "1) What is the expected carbon capture capacity?\n"
            "2) What is the hydrogen generation capacity?\n"
            "3) What is the investment size?\n"
            "4) What is the iron production capacity?\n"
            "5) What is the steel production capacity?\n"
        )
        keys = [
            "cc_capacity","cc_quote",
            "h2_capacity","h2_quote",
            "investment","investment_quote",
            "iron_capacity","iron_quote",
            "steel_capacity","steel_quote",
        ]

    schema_prompt = (
        "You are an extraction assistant. Using ONLY the text below, answer the following.\n"
        "Return strict JSON with exactly these keys:\n" + schema + "\n"
        "Formatting rules for ANSWERS (not quotes):\n"
        "• Use digits for numbers, but write all UNITS and CURRENCIES in plain English words only.\n"
        "• Do NOT use symbols or abbreviations (e.g., no €, $, £, ¥, MW, GW, Mt, kt, t/yr, tpa, MTPA, kWh).\n"
        "• Examples: '4.5 billion US dollars', '200 megawatts', '2.5 million tonnes per year', '1.2 million tonnes of CO2 per year'.\n"
        "• 'steel_capacity' is NOT the same as DRI output—do not confuse them.\n"
        "• If you cannot find a value, set the answer field to exactly ''.\n\n"
        "Quotes:\n"
        "• The *_quote fields must be short verbatim substrings from the text that support the answer.\n"
        "• Quotes may include the original symbols or abbreviations; do not rewrite quotes.\n\n"
        "Questions:\n" + q_block +
        "\nText:\n\"\"\"\n" + article_text + "\n\"\"\""
    )

    msgs = [
        {"role": "system", "content": "Return strict JSON only. Follow rules exactly."},
        {"role": "user", "content": schema_prompt},
    ]
    try:
        resp = gpt_client.chat.completions.create(
            model=gpt_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=msgs,
        )
        out = resp.choices[0].message.content.strip()
        data = json.loads(out)
    except Exception as e:
        print(f"Error extracting numeric facts: {e}")
        data = {}

    # normalize keys for this domain
    for k in keys:
        if k not in data or data[k] is None:
            data[k] = ""

    # fill missing answers
    for ans_key in [k for k in keys if k.endswith("_capacity") or k == "investment"]:
        if ans_key in data and not data[ans_key]:
            data[ans_key] = ""

    # clip quotes
    import re as _re
    for qk in [k for k in keys if k.endswith("_quote")]:
        data[qk] = _re.sub(r"\s+", " ", (data[qk] or "")).strip()[:300]

    return data

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
                print(f"Warning: Unrecognized answer format '{clean_answer}' from GPT. Defaulting to 'no'.")
                clean_answer = "yes"
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


def query_gpt_for_project_details(gpt_client, gpt_model, article_text, tech_list, domain):
    """
    Uses GPT to extract project details from the article text in two rounds.
    Returns a dictionary with all keys. Missing details are returned as empty strings.
    """
    entries = []
    for item in tech_list:
        if isinstance(item, dict):
            # each dict has exactly one key→value
            for name, definition in item.items():
                entries.append(f"{name}: {definition}")
        else:
            entries.append(str(item))

    tech_list_str = "\n".join(entries)
    
    # --- First round: Core details ---
    core_prompt = (
        "You are an information extraction assistant. Given the article text below, extract the following core details if available. "
        "You may need to infer them:\n"
        "- scale: one of 'pilot', 'demonstration', or 'full scale'\n"
        "- project_name: the name of the project mentioned\n"
        "- timeline: the year to be online, NOT necessarily when operations will begin (skip if not explicitly stated)\n"
        f"- technology: one of the following: {tech_list_str}\n\n. DO NOT select a technology if one is not mentioned in the article. If multiple are mentioned, feel free to list more than one, but ONLY if they are clearly being used in the same project."
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
            "For any missing detail, return an empty string.\n\n"
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

    try:
        num = extract_numeric_facts_with_quotes(gpt_client, gpt_model, article_text, domain=domain)
        combined_details.update(num) 
    except Exception as e:
        print(f"Numeric extraction error: {e}")

    return combined_details
