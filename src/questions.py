
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
    "Is this headline about an announcement for a conference, forum, or event?",
    "Is this headline about sports, movies, fashion (like watches), food, or pop culture?",
    "Is the headline about new leadership in a company or a merge, acquisition, or consolidation? If it is about a collaboration, say no.",
    "Does the headline explicitly mention iron or steel consumption? If it is about a supply agreement or innovation to manufacturing green steel, say no.",
    "Is this headline about net profit or profit results of a company? Is the headline about total production?",
    "Is this headline *only* reporting broad production capacity figures or targets (e.g. annual tonnage goals) without referencing a specific green-steel project, investment, or scale-up effort?",
    "Is this headline *only* about broad macroeconomic or trade policies (e.g. inflation, tariffs, costs, imports, exports) and *not* about a specific green-steel project’s financing, investment, or production activities?",
    "Is this headline about a metal product unrelated to steel, such as coal?",
    "Is this headline about stock market performances, layoffs or creating jobs, dividends, financial results, or commodity prices? Does it mention the words market or sector in a way that does not signify a potential new project in green iron/steel?",
    "Is this headline about politics, national or international policy, trade, or warfare? If it mentions fundraising, a developing steel plant or technology, or green-steel project, say no.",
    "Is this headline about an award or prize? If it is about an investment or grant for steel, say no.",
    "Is this headline only about general logistics (deliveries, shipping) or warnings/threats, without referring to a specific project partnership, green-hydrogen plant installation, or collaboration in green-steel/green-hydrogen initiatives?",
    "Is this headline a broad review or opinion piece?",
    "Is this headline about a government or international body's high-level CO₂ reduction targets or sourcing policies, *without* referring to a concrete green-steel production project?",
    "Is this headline about a mining operation (e.g. a mine opening, expansion, closure or production restart)? If it’s about logistics or offtake agreements (deliveries, shipments, test consignments, pellet offtake, etc.) or any green-initiative (hydrogen partnerships, plant renovations, emission-reduction projects, etc.), answer no.",
    "Is the headline about the release of a company report or the financial/fiscal year (FY)?",
    "Is the headline about the ability to produce bars, or the amount of steel bars that can be produced?",
    "Determine whether this headline is **only** a generic corporate or market announcement with **no** concrete project details. \n **Project details** include any mention of: \n a manufacturing or steel-production operation (mine opening, plant expansion, closure, restart)  \n a technology or infrastructure deployment   \n a partnership, offtake or logistics agreement  \n a new initiative, mission statement, pilot program, or strategy rollout  \n a monetary figure indicating project funding (e.g. “$X million”, “€Y billion”). If the headline contains **any** project detail, answer: `{ 'answer': 'no' }`.  Otherwise answer `{ 'answer': 'yes' }`."
]

IRON_YES = [
    "Is the headline related to iron for green steel?",
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
    "Is this headline about an announcement for a conference or forum, or related event? Answer no if it is about a new project in green iron or steel that was announced, or an announced investment.",
    "Is this headline about sports, movies, fashion (like watches), food, or pop culture?",
    "Is the headline about new leadership in a company or a merge, acquisition, or consolidation? If it is about a collaboration, say no.",
    "Is this headline about iron or steel consumption? If it is explictly about a supply agreement, say no."
    "Is this headline about net profit or profit results of a company?",
    "Is this headline *only* reporting broad production capacity figures or targets (e.g. annual tonnage goals) without referencing a specific green-iron project, investment, or scale-up effort?",
    "Is this headline *only* about broad macroeconomic or trade policies (e.g. inflation, tariffs, costs, imports, exports) and *not* about a specific green-iron project’s financing, investment, or production activities?",
    "Is this headline about a mining product unrelated to iron, steel, or hydrogen, such as coal?",
    "Is this headline about stock market performances, layoffs or creating jobs, dividends, financial results, or commodity prices? Does it mention the words market or sector in a way that does not signify a potential new project in green iron/steel?",
    "Is this headline about politics, national or international policy, trade, or warfare? If it mentions fundraising, a developing steel/iron plant or technology, or green-iron project, say no.",
    "Is this headline about a government or international body's high-level CO₂ reduction targets or sourcing policies, *without* referring to a concrete green-iron production project?",
    "Is this headline about an award or prize? If it is about an investment or grant for iron, say no.",
    "Is this headline only about general logistics (deliveries, shipping) or warnings/threats, without referring to a specific project partnership, green-hydrogen plant installation, or collaboration in green-iron/green-hydrogen initiatives?",
    "Is this headline an opinion piece? If it relates to green iron/steel/metal or iron/steel/metal production, including green hydrogen, so no.",
    "Is this headline about a mining operation (e.g. a mine opening, expansion, closure or production restart)? If it’s about logistics or offtake agreements (deliveries, shipments, test consignments, pellet offtake, etc.) or any green-initiative (hydrogen partnerships, plant renovations, emission-reduction projects, etc.), answer no.",
    "Is the headline about the release of a company report or financial/fiscal year (FY) results?",
    "Is this headline about a country or group's broad goals for CO2 emission cuts or product sourcing?",
    "Determine whether this headline is **only** a generic corporate or market announcement with **no** concrete project details. \n **Project details** include any mention of: \n a manufacturing or iron-production operation (mine opening, plant expansion, closure, restart)  \n a technology or infrastructure deployment   \n a partnership, offtake or logistics agreement  \n a new initiative, mission statement, pilot program, or strategy rollout  \n a monetary figure indicating project funding (e.g. “$X million”, “€Y billion”). If the headline contains **any** project detail, answer: `{ 'answer': 'no' }`.  Otherwise answer `{ 'answer': 'yes' }`."
]


CEMENT_NO = [
    "Is this headline about an announcement for a conference or forum, or related event? Answer no if it is about a new project in green cement that was announced, or an announced investment.",
    "Is this headline about sports, movies, fashion (like watches), food, or pop culture?",
    "Is the headline about new leadership in a company or a merge, acquisition, or consolidation? If it is about a collaboration, say no.",
    "Is this headline about net profit or profit results of a company?",
    "Is this headline *only* reporting broad production capacity figures or targets (e.g. annual tonnage goals) without referencing a specific green-cement project, investment, or scale-up effort?",
    "Is this headline about workloads, operating margins, exports, bonds, or dispatches?",
    "Is this headline about the construction sector or construction, with no mention of cement innovations or projects?",
    "Does this headline explicitly mention consumption? If it is explictly about a supply agreement, say no.",
    "Is this headline *only* about broad macroeconomic or trade policies (e.g. inflation, tariffs, costs, imports, exports) and *not* about a specific green-cement project’s financing, investment, or production activities?",
    "Is this headline about stock market performances, layoffs or creating jobs, dividends, financial results, or commodity prices? Does it mention the words market or sector in a way that does not signify a potential new project in green cement?",
    "Is this headline about politics, national or international policy, trade, or warfare? If it mentions fundraising, a developing cement plant or technology, or green-cement project, say no.",
    "Is this headline about an award or prize? If it is about an investment or grant for cement, say no. If it is about a certification or permission, say no.",
    "Is this headline only about general logistics (deliveries, shipping) or warnings/threats, without referring to a specific project partnership, green-hydrogen plant installation, or collaboration in green-cement/green-hydrogen initiatives?",
    "Is this headline an opinion piece? If it relates to green cement, green cement production, carbon capture/usage, or renewable energy sources, say no.",
    "Is the headline about the release of a company report or financial/fiscal year (FY) results?",
    "Determine whether this headline is **only** a generic corporate or market announcement with **no** concrete project details. \n **Project details** include any mention of: \n a manufacturing or cement-production operation (mine opening, plant expansion, closure, restart)  \n a technology or infrastructure deployment   \n a partnership, offtake or logistics agreement  \n a new initiative, mission statement, pilot program, or strategy rollout  \n a monetary figure indicating project funding (e.g. “$X million”, “€Y billion”). If the headline contains **any** project detail, answer: `{ 'answer': 'no' }`.  Otherwise answer `{ 'answer': 'yes' }`."
    "Is this headline about a government or international body's high-level CO₂ reduction targets or sourcing policies, *without* referring to a concrete green-cement production project?"
]

STEEL_IRON_TECH = [{"EAF (eletric arc furnace)": "Electric arc furnaces (EAFs) are used in steelmaking to melt scrap metal using electricity to create new steel. Electricity is passed through graphite electrodes to create an electric arc, generating intense heat that melts the scrap."}, {"H-DRI (hydrogen direct reduced iron or sponge iron)": "This process involves reducing iron using hydrogen gas (H2). However, NOT all hydrogen-based steel production uses HDRI"}, {"CCS for BF-BOF (carbon capture storage for blast furnace)": "CCS involves capturing CO2 emissions from various points in the BF-BOF process (like the coke oven, hot-blast stoves, and power plant) and storing it underground. NOT all instances of CCS involve BF-BOF abatement."}, {"H-DRI + EAF (H-DRI and electric arc furnace)": "This is an integrated process with the previously defined H-DRI method. This approach uses hydrogen to reduce iron ore into DRI, which is then melted in an EAF. Both the H-DRI component and EAF component must be present for a project to qualify for using this technology."}, {"CCS for power station": "Carbon capture and storage (CCS) for power stations involves capturing carbon dioxide emissions from power plants and storing them underground or using them for other purposes. Not all instances of CCS involve power stations."}, {"H-DRI + ESF (H-DRI and electric smelting furnace)": "This combines the previously defined H-DRI process with electric smelting furnaces. ESF and EAF are NOT the same, and the H-DRI process + ESF is typically also combined with BOF. NOT all uses of ESFs involve H-DRI."}, {"CCUS for BF-BOF (carbon capture and utilization and storage for BF)": "This is similar to the previously defined CCS for BF-BOF. The difference lies in the UTILIZATION of the CO2 in other processes. NOT all CCS processes include utilization."},
{"MOE (molten oxide electrolysis)": "Molten oxide electrolysis (MOE) is a process that uses electricity to extract metals from their oxides in a molten state. Molten oxide electrolysis distinguishes itself from all molten salt electrolytic technologies through its use of carbon-free anodes, facilitating the production of oxygen gas at the anode."}, {"CCU for BF-BOF": "This process is similar to the previously defined CCUS for BF-BOF, but it DOES NOT include storage of CO2. If the process involves storage, it is NOT CCU for BF-BOF."}, {"Electrowinning": "Electrowinning is an electrochemical process used to recover metals from solutions. It involves passing an electric current through a solution containing dissolved metal ions, causing the metal to deposit onto a cathode as a solid, pure metal. This process is a type of electrolysis, where electricity is used to drive a non-spontaneous chemical reaction"}, {"H2 (hydrogen) production": "Hydrogen is primarily produced via electrolysis, using electricity to split water into hydrogen and oxygen. If the electricity is from renewable sources (like solar or wind), this is known as 'green hydrogen'. This is NOT the same as H-DRI, it is focused on the PRODUCTION of hydrogen."}, {"ESR (electric smelting reduction)": "Also known as electro slag remelting, this is a secondary refining process used to purify and enhance the microstructure of metal ingots, particularly steels and alloys. It is CRITICAL to note that this is a secondary refining process."}, {"Biomass for BF": "Biomass can be used in blast furnaces as a fuel or reducing agent in sintering, bio-coke production, or direct injection. This is a very specific method, and NOT all green steel production involving blast furnaces uses biomass."}, {"Electric Smelting Furnace (ESF)": "Electric smelting furnaces are powered by electricity and can melt either direct reduced iron OR iron ore in place of a plastic furnace."},
{"BF-BOF to EAF for green iron": "This is when traditional blast furnace-basic oxygen furnace methods in iron making are transitioned to electric arc furnaces for production."}, {"Induction melting furnace": "In an induction furnace, the iron is heated by electromagnetic induction, eliminating the need for combustion or arcs."}, {"BF-BOF to HIsarna": "This focuses on the placement of BF-BOF with the HISARNA process. The HISARNA process is an alternative hot metal production process that combines several different technologies which eliminates the need for sinter and coke production plants. This is a combination of three different technologies: 1) heated screw coal pyrolysis feeder 2) cyclone converter furnace (CCF) and 3) HiSmelt vessel."}, {"NG-DRI (natural gas-based direct reduction) to H-DRI": "In NG-DRI, iron ore is reduced to metallic iron using a reducing gas composed of hydrogen (H2) and carbon monoxide (CO), produced by reforming natural gas (CH4). In NG-DRI to H-DRI, we are focusing on the transition from one technology to the other. NOT all instances of implementing H-DRI start as a transition from NG-DRI." }, {"H2-based rolling mill": "This technology refers to a process where hydrogen is used to reduce iron ore into iron, which is then rolled into various shapes using a rolling mill. NOT all rolling mills are H2 based. NOT all hydrogen-based iron production processes involve rolling mills."},
{"NG-DRI to H-DRI + EAF": "This process is similar to the previously defined NG-DRI to H-DRI, but in incorporates the use of electric arc furnaces after the H—DRI process for steel production."}, {"EAF using imported NG-DRI": "NG-DRI specifically refers to DRI produced using natural gas as the reducing agent. This process is an alternative to using coal and coke in traditional BF-BOF steelmaking. EAFs primarily use scrap steel as feedstock, but they can also incorporate DRI to improve steel quality and reduce reliance on scrap."
}, {"NG-DRI to H-DRI + ESF": "This focuses on the transition from the previously defined NG-DRI to the previously defined H-DRI + ESF process. NOT all H-DRI + ESF implementations were transitioned from NG-DRI, and NOT all NG-DRI to H-DRI transitions involve ESF."}, {"NG-DRI": "In NG-DRI, iron ore is reduced to metallic iron using a reducing gas composed of hydrogen (H2) and carbon monoxide (CO), produced by reforming natural gas (CH4)."}, {"Biogenic syngas DRI": "Biogenic syngas, or biosyngas, is a mixture of gases primarily composed of hydrogen and carbon monoxide, produced from the gasification of biomass. Biomass gasification involves heating biomass at high temperatures  in the presence of a controlled amount of oxygen, steam, or other gasifying agents. Biogenic syngas can then be used for DRI, and it is NOT the same as NG-DRI."
}, {"NG-DRI + EAF": "This is similar to the previously defined H-DRI + EAF, but it does NOT use H2 for the DRI process. Instead, it uses natural gas. BOTH technologies (NG-DRI and EAF) must be present for this specific process."},
{"Electrochemical process": "These processes, often involving electrolysis, can replace or complement traditional blast furnaces by directly reducing iron oxide to iron using electricity. This can INCLUDE molten oxide electrolysis, alkaline electrolysis, and other approaches."}, {"NG-DRI + CCS": "NG-DRI (Natural Gas Direct Reduced Iron) combined with CCS (Carbon Capture and Storage) is a pathway for decarbonizing steel production. In this process, natural gas is used to reduce iron ore into DRI, and the CO2 emissions from this process are captured and stored using CCS technology. The primary source of CO2 emissions in the NG-DRI process comes from the reformation of natural gas to produce the reducing gas. CCS technology captures these emissions before they are released into the atmosphere."}, {"H2 injection to BF": "Hydrogen (H2) injection into a blast furnace (BF) is a technique used to reduce CO2 emissions during ironmaking by partially substituting coke with hydrogen as an iron-reducing agent. This produces water vapor instead of carbon dioxide."}, {"Green hydrogen": "Green hydrogen in steel/ironmaking is a GENERAL term to describe different methods of decarbonization, INCLUDING DRI processes, H2 injection to BF, or hydrogen production."}, {"SOEC (solid oxide electrolysis cell)": "A solid oxide electrolysis cell (SOEC) is a type of high-temperature electrolyzer that uses a solid oxide electrolyte to convert steam into hydrogen and oxygen. They can be integrated with DRI plants."}, {"biochar use": "Biochar, a renewable carbon material produced by heating biomass in the absence of oxygen, can be used in various processes like sintering, blast furnace injection, and as a reducing agent in electric arc furnaces. This is a VERY specific alternative to traditional methods, and NOT all green steel/iron production involving BF, EAF, or sintering uses biochar."}, {"CCS (carbon capture storage)": "CCS involves capturing CO2 emissions from various points in the iron and steel making process and storing it. This DOES NOT include utilization of the CO2 and is DIFFERENT from CCUS."}, {"briquetted iron": "hot briquetted iron (HBI) is produced by compressing DRI (which is essentially iron ore that has been reduced of its oxygen content) into dense, pillow-shaped briquettes at high temperatures. HBI is a premium feedstock for both blast furnaces and electric arc furnaces."}]

CEMENT_TECH = [{"CCS (carbon capture storage)": "CCS involves capturing CO2 emissions from various points in the cement making process and storing it. This DOES NOT include utilization of the CO2 and is DIFFERENT from CCUS."}, {"CCUS (carbon capture and utilization storage)": "This is similar to the previously defined CCS. The difference lies in the UTILIZATION of the CO2 in other processes. NOT all CCS processes include utilization."}, {"Meca clay": "mega-clay is a process that uses mechano-chemical activation of clay to produce a supplementary cementitious material (SCM) that can partially replace clinker in cement production. This process is fully electrified and powered by renewable energy, avoiding the need for fossil fuels and high-temperature calcination."}, {"Kiln for calcined clay": "a kiln for calcined clay is a specialized furnace used to heat clay to high temperatures (typically between 600°C and 900°C) to produce metakaolin. This calcined clay is then used as a supplementary cementitious material (SCM). Calcined clay  in the making of cement can help to make significant CO2 reductions, due to the lower amount of energy needed the manufacturing process."}]
PROJECT_STATUS = ["Announced", "Cancelled", "Construction", "Operating", "Finalized (research & testing)", "Paused/postponed"]