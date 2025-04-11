from rapidfuzz import fuzz
STEEL_IRON_TECH = [
    "H-DRI (hydrogen direct reduced iron or sponge iron)",
    "CCS for BF-BOF (carbon capture storage for blast furnace)",
    "H-DRI + EAF (hydrogen direct reduced iron and electric arc furnace)",
    "CCS for power station (carbon capture storage)",
    "H-DRI + ESF (hydrogen direct reduced iron and electric smelting furnace)",
    "CCUS for BF-BOF (carbon capture and utilization and storage for blast furnace)",
    "MOE (molten oxide electrolysis)",
    "CCU for BF-BOF (carbon capture and utilization for blast furnace)",
    "Electrowinning",
    "H2 (hydrogen) production",
    "ESR (electric smelting reduction)",
    "Biomass for BF (blast furnace)",
    "Electric Smelting Furnace (ESF)",
    "BF-BOF to EAF for green iron (blast furnace to electric arc furnace)",
    "Induction melting furnace",
    "BF-BOF to HIsarna (blast furnace)",
    "NG-DRI (natural gas-based direct reduction) to H-DRI (hydrogen direct reduced iron)",
    "H2-based rolling mill",
    "NG-DRI to H-DRI + EAF (natural gas-based direct reduction to hydrogen direct reduced iron and electric arc furnace)",
    "EAF using imported NG-DRI (electric arc furnace using imported natural gas-based direct reduction)",
    "NG-DRI to H-DRI + ESF (natural gas-based direct reduction to hydrogen direct reduced iron and electric smelting furnace)",
    "NG-DRI (natural gas-based direct reduction )",
    "Biogenic syngas DRI (direct reduced iron)",
    "NG-DRI + EAF (natural gas-based direct reduction  and electric arc furnace)",
    "Electrochemical process",
    "NG-DRI + CCS (natural gas-based direct reduction and carbon capture storage)",
    "H2 injection to BF (blast furnace)",
    "Green hydrogen",
    "SOEC (solid oxide electrolysis cell)",
    "biochar use",
    "CCS (carbon capture)",
    "briquetted iron"
]

CEMENT_TECH = [
    "CCS (carbon capture )",
    "CCUS (carbon capture and utilization )",
    "Meca clay",
    "Kiln for calcined clay"
]

def check_detail_in_text_fuzzy(detail, article_text):
    """
    Returns the fuzzy matching score between detail and article_text.
    """
    detail_norm = detail.strip().lower()
    text_norm = article_text.lower()
    score = fuzz.partial_ratio(detail_norm, text_norm)
    return score

def get_check_results_flag(extracted_details, article_text):
    """
    For each non-empty field in extracted_details, compute the fuzzy match score with article_text.
    For the 'technology' field, the full technology (with its descriptive text in parentheses) is used
    for matching if the abbreviation matches one of the full names in STEEL_IRON_TECH or CEMENT_TECH.
    If any score is below the threshold, return "CHECK RESULTS: " followed by the column names that flagged.
    Otherwise, return an empty string.
    """
    threshold = 80
    scores = {}
    flagged_columns = []
    for key, value in extracted_details.items():
        if value.strip():
            detail_to_check = value
            # If this is the technology field, replace the abbreviation with the full technology name.
            if key.lower() == "technology":
                all_techs = STEEL_IRON_TECH + CEMENT_TECH
                for tech in all_techs:
                    # Split on " (" to get the abbreviation part.
                    abbr = tech.split(" (")[0].strip()
                    if abbr.lower() == value.strip().lower():
                        detail_to_check = tech
                        break
            score = check_detail_in_text_fuzzy(detail_to_check, article_text)
            scores[key] = score
            if score < threshold:
                flagged_columns.append(key)
    if flagged_columns:
        return "CHECK RESULTS: " + ", ".join(flagged_columns), scores
    return "", scores
