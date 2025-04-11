
STEEL_YES = [
    "Is the headline talking about steel production?",
    "Is the headline mentioning the name of a steel producer?",
    "Is the headline mentioning the name of a technology provider for the steel industry?",
    "Is the headline mentioning an existing green steel project?",
    "Does the headline insinuate that a pilot project for green steel production will be built?",
    "Does the headline insinuate that a demonstration project for green steel production will be built?",
    "Does the headline insinuate that a full scale project for green steel production will be built?",
    "Is the headline mentioning hydrogen use for steel production?",
    "Is the headline mentioning carbon capture for steel production?",
    "Is the headline mentioning biochar OR biomass for steel production?",
    "Is the headline announcing a company innovation or new approaches to steel production?",
    "Is the headline mentioning research and development partnership(s) for green steel production?",
    "Is the headline mentioning memorandum of understanding (OR MoU) for green steel production?",
    "Is the headline mentioning the signatory of an agreement for green steel production?",
    "Is the headline mentioning supply agreement for low-carbon (OR green) steel?",
    "Is the headline mentioning a collaboration between a steel producer and another company to reduce steel production emissions?",
    "Is the headline mentioning investment on green steel?",
    "Is the headline mentioning final investment decisions on green steel?",
    "Is the headline mentioning grants for green steel production?",
    "Is the headline mentioning grants for green steel production?",
]

STEEL_NO = [
    "Is the headline mentioning green steel market growth or shrinkage, or about commodity prices?",
    "Is the headline mentioning market intelligence?",
    "Is the headline mentioning announcing a conference or forum, or related?",
    "Is the headline mentioning sports?",
    "Is this headline about an award that a company has been granted?",
    "Is the headline mentioning new leadership in steel producing company?",
    "Is the headline mentioning net profit or profit results of a steel producing company?",
    "Is the headline about the release of a company report or financial year results?"

]

IRON_YES = [
    # "Is the headline related to iron for green steel?",
    "Does the headline refer to iron reduction?",
    "Does the headline menmention the name of an iron mining company?",
    "Does the headline mention the name of a technology provider for iron reduction?",
    "Does the headline refer to an existing green iron project?",
    "Does the headline insinuate that a pilot project for green iron production will be built?",
    "Does the headline insinuate that a demonstration project for green iron production will be built?",
    "Does the headline insinuate that a full scale project for green iron production will be built?",
    "Does the headline refer to hydrogen use for iron reduction?",
    "Does the headline refer to green hydrogen use for iron reduction?",
    "Does the headline refer to renewable hydrogen use for iron reduction?",
    "Does the headline refer to natural gas use for iron reduction?",
    "Does the headline refer to biochar use for iron reduction?",
    "Does the headline refer to carbon capture for iron reduction?",
    "Does the headline refer to briquetted iron?",
    "Does the headline refer to a company innovation or new approaches to iron reduction?",
    "Does the headline refer to research and development partnership for iron reduction?",
    "Does the headline refer to a memorandum of understanding for iron reduction?",
    "Does the headline insinuate the signatory of an agreement for iron reduction?",
    "Does the headline refer to a supply agreement of green iron or reduced iron?",
    "Does the headline refer to a collaboration between an iron mining company and another company to reduce emissions?",
    "Does the headline refer to an investment on green iron?",
    "Does the headline refer to a final investment decisions on green iron?",
    "Does the headline refer to grants for green iron OR iron reduction?",
    "Does the headline mention a research project for iron production?",
]

IRON_NO = [
    "Is this headline about an announcement for a conference or forum, or related event?",
    "Does this headline indicate the article is about sports or movies?",
    "Does this headline mention new leadership in a company?",
    "Is this headline about net profit or profit results of a company?",
    "Is this headline about a mining product unrelated to iron?",
    "Is this headline about stock market performances or commodity prices?",
    "Is this headline about politics, trade, or warfare?",
    "Is this headline about an award that a company has been granted?",
    "Is this headline about a mine that is opening?"
    "Is the headline about the release of a company report or financial year results?"

]


CEMENT_NO = [
    "Is this headline about an announcement for a conference or forum, or related event?",
    "Does this headline indicate the article is about sports or movies?",
    "Does this headline mention new leadership in a company?",
    "Is this headline about net profit or profit results of a company?",
    "Is this headline about an award?",
    "Is this headline about stock market performances, dividends, financial results, commodity prices?",
    "Is this headline about the cement market or the general cement industry?",
    "Is this headline about politics, policy, trade, or warfare?",
    "Is this headline about the acquisition of a cement company?",
    "Is this headline about workloads, operating margins, exports, bonds, or dispatches?",
    "Is this headline about the construction sector or construction?",
    "Is the headline about the release of a company report or financial results?"
]

STEEL_IRON_TECH = ["H-DRI (hydrogen direct reduced iron or sponge iron)", "CCS for BF-BOF (carbon capture storage for blast furnace)", "H-DRI + EAF (H-DRI and electric arc furnace)", "CCS for power station", "H-DRI + ESF (H-DRI and electric smelting furnace)", "CCUS for BF-BOF (carbon capture and utilization and storage for BF)",
"MOE (molten oxide electrolysis)", "CCU for BF-BOF", "Electrowinning", "H2 (hydrogen) production", "ESR (electric smelting reduction)", "Biomass for BF", "Electric Smelting Furnace (ESF)",
"BF-BOF to EAF for green iron", "Induction melting furnace", "BF-BOF to HIsarna", "NG-DRI (natural gas-based direct reduction) to H-DRI", "H2-based rolling mill",
"NG-DRI to H-DRI + EAF", "EAF using imported NG-DRI", "NG-DRI to H-DRI + ESF", "NG-DRI", "Biogenic syngas DRI", "NG-DRI + EAF",
"Electrochemical process", "NG-DRI + CCS", "H2 injection to BF", "Green hydrogen", "SOEC (solid oxide electrolysis cell)", "biochar use", "CCS (carbon capture storage)", "briquetted iron"]
CEMENT_TECH = ["CCS (carbon capture storage)", "CCUS (carbon capture and utilization storage)", "Meca clay", "Kiln for calcined clay"]
PROJECT_STATUS = ["Announced", "Cancelled", "Construction", "Operating", "Finalized (research & testing)", "Paused/postponed"]