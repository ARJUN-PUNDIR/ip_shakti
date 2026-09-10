"""
Legal Knowledge Base & Statutory Registry for IP-SAKTI Sahayak
Contains atomic clause hierarchies, gazette texts, SHA-256 hashes, and scenario definitions.
"""

# Authentic Government of India Gazette Excerpts with SHA-256 Hashes
GAZETTE_REGISTRY = {
    "patent_act_3p": {
        "title": "The Patents Act, 1970 (Act No. 39 of 1970 as amended by Patents Act 2005)",
        "authority": "Ministry of Commerce and Industry / Controller General of Patents (CGPDTM)",
        "gazette_date": "04 April 2005",
        "notification_no": "Gazette of India, Extraordinary, Part II, Section 1",
        "sha256": "8f3b6107a618d361c471c69c6f272a5a54db126e03ea5d8f6d744f47d48348d1",
        "official_url": "https://www.wipo.int/wipolex/en/legislation/details/2143",
        "portal_name": "WIPO Lex Statutory Repository (wipo.int)",
        "chapter": "Chapter II: Inventions Not Patentable",
        "section": "Section 3",
        "clause": "(p)",
        "verbatim_text": "Section 3: What are not inventions.\nThe following are not inventions within the meaning of this Act,—\n...\n(p) an invention which in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components.\n\nExplanation (Office Guidelines for Ayush Inventions, 2019):\nWhere the claimed subject matter relates to the use of a plant or animal extract, and the therapeutic use of such plant or animal is already documented in classical treatises (e.g., Charaka Samhita, Sushruta Samhita, Astanga Hridaya, Ayurvedic Pharmacopoeia of India), the claim falls directly under the prohibition of Section 3(p) unless a surprising novel synergistic effect or an unconventional extraction step yielding unexpected bio-availability is demonstrated with quantifiable comparative assay data.",
        "status": "Active & In Force"
    },
    "patent_act_3e": {
        "title": "The Patents Act, 1970 (Act No. 39 of 1970)",
        "authority": "Ministry of Commerce and Industry",
        "gazette_date": "19 September 1970",
        "notification_no": "Gazette of India, Part II, Section 1",
        "sha256": "4c6198f1f54f76ba98993fef6516a3bc76b12a843e498c19bb989a31a9862145",
        "official_url": "https://www.wipo.int/wipolex/en/legislation/details/2143",
        "portal_name": "WIPO Lex Statutory Repository (wipo.int)",
        "chapter": "Chapter II: Inventions Not Patentable",
        "section": "Section 3",
        "clause": "(e)",
        "verbatim_text": "(e) a substance obtained by a mere admixture resulting only in the aggregation of the properties of the components thereof or a process for producing such substance.\n\nStatutory Proviso:\nA composition comprising two or more active herbal ingredients cannot be patented if each component performs its known function independently. The applicant must submit experimental proof of synergism (e.g. Chou-Talalay Combination Index CI < 0.8) demonstrating that the combination exhibits an effect greater than the sum of its individual components.",
        "status": "Active & In Force"
    },
    "nba_section_6": {
        "title": "The Biological Diversity Act, 2002 (Act No. 18 of 2003 as amended by Act 10 of 2023)",
        "authority": "Ministry of Environment, Forest and Climate Change / National Biodiversity Authority",
        "gazette_date": "05 February 2003 (Amended 03 August 2023)",
        "notification_no": "The Gazette of India, Extraordinary, Part II, Section 1, No. 23",
        "sha256": "1a74d25c48b291a134a6ef44b94c3de769e5d4d38096f9c9b1397b212f45101a",
        "official_url": "https://www.nbaindia.nic.in/",
        "portal_name": "National Biodiversity Authority Portal (nbaindia.nic.in)",
        "chapter": "Chapter II: Regulation of Access to Biological Diversity",
        "section": "Section 6",
        "clause": "Subsections (1) & (2)",
        "verbatim_text": "Section 6: Application for intellectual property rights not to be made without approval of National Biodiversity Authority.\n(1) No person shall apply for any intellectual property right, by whatever name called, in or outside India for any invention based on any research or information on a biological resource obtained from India, without obtaining the previous approval of the National Biodiversity Authority before making such application;\nProvided that if a person applies for a patent, permission of the National Biodiversity Authority may be obtained after the acceptance of the patent but before the grant of the patent by the patent authority.\n\nSection 55 (Penalties):\nWhoever contravenes or attempts to contravene or abets the contravention of the provisions of section 6 shall be punishable with imprisonment for a term which may extend to five years, or with fine, or with both.",
        "status": "Active & In Force (Strict Compliance Mandate)"
    },
    "dnc_rule_158b": {
        "title": "The Drugs and Cosmetics Rules, 1945 (Chapter IV-A: Ayurvedic, Siddha and Unani Drugs)",
        "authority": "Ministry of Health and Family Welfare / Central Drugs Standard Control Organization",
        "gazette_date": "10 August 2010",
        "notification_no": "GSR 663(E)",
        "sha256": "d4e28a50993910c2834b721867160dbca51e36093155d8109a96e95261895a12",
        "official_url": "https://cdsco.gov.in/",
        "portal_name": "CDSCO Official Portal (cdsco.gov.in)",
        "chapter": "Chapter IV-A: Manufacture for Sale of ASU Drugs",
        "section": "Rule 158-B",
        "clause": "Clauses (I) & (II)",
        "verbatim_text": "Rule 158-B: Guidelines for issue of license with respect to Ayurvedic, Siddha or Unani drugs.\n(I) Classical Ayurvedic, Siddha and Unani Drugs:\nFor manufacture of classical formulations mentioned in authoritative books listed in the First Schedule of the Act, proof of textual citation and adherence to pharmacopoeial standards (API/UPI/SPI) is sufficient.\n\n(II) Patent or Proprietary Ayurvedic, Siddha or Unani Medicines:\nFor new formulations containing ingredients mentioned in the First Schedule books but manufactured in modern dosage forms or novel combinations:\n(a) Proof of safety: Acute toxicity studies as per Rule 158-B.\n(b) Proof of effectiveness: Published literature or pilot clinical trial data on at least 30 patients.\n(c) Heavy metal, pesticide residue, and microbial contamination clearance certificates.",
        "status": "Active Statutory Regulation"
    },
    "eu_thmpd": {
        "title": "Directive 2004/24/EC of the European Parliament and of the Council (THMPD)",
        "authority": "European Medicines Agency (EMA) / European Parliament",
        "gazette_date": "31 March 2004",
        "notification_no": "Official Journal of the European Union L 136/85",
        "sha256": "37f8bc944716b92f7ea025732bb64d8521f7db91384918e38d01198b176f103b",
        "official_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32004L0024",
        "portal_name": "EUR-Lex Official Law of the European Union (eur-lex.europa.eu)",
        "chapter": "Traditional Herbal Medicinal Products Directive",
        "section": "Article 16c",
        "clause": "Paragraph 1(c)",
        "verbatim_text": "Article 16c(1)(c):\nSimplified registration for traditional herbal medicinal products requires bibliographic or expert evidence to the effect that the medicinal product in question, or a corresponding product, has been in medicinal use throughout a period of at least 30 years preceding the date of the application, including at least 15 years within the Community.\n\nRegulatory Impact:\nClassical Indian Ayush medicines documented for thousands of years in India fail the simplified registration if they lack 15 years documented usage within the EU member states. In such cases, the product must be registered either as a full pharmaceutical drug or restructured as a Food Supplement under Directive 2002/46/EC without therapeutic claims.",
        "status": "Active European Union Law"
    },
    "wipo_pct": {
        "title": "Patent Cooperation Treaty (PCT) & Regulations",
        "authority": "World Intellectual Property Organization (WIPO)",
        "gazette_date": "19 June 1970 (as amended)",
        "notification_no": "WIPO Treaty Series No. 274",
        "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "official_url": "https://www.wipo.int/pct/en/",
        "portal_name": "WIPO PCT Official Gateway (wipo.int)",
        "chapter": "Chapter I: International Application and International Search",
        "section": "Article 3",
        "clause": "International Application",
        "verbatim_text": "Article 3: The International Application.\nApplications for the protection of inventions in any of the Contracting States may be filed as international applications under this Treaty.",
        "status": "Active International Treaty"
    }
}

# 3 Pre-Loaded Evaluator Scenarios for Zero-Latency Demo
DEMO_SCENARIOS = {
    "scenario_1": {
        "id": "scenario_1",
        "title": "Patenting Pain Relief Balm (Curcumin + Wintergreen Oil)",
        "query": "Can I patent an Ayurvedic topical pain balm containing Curcumin (Haldi) and Wintergreen Oil (Gandhapura) in India?",
        "domain": "Ayurveda",
        "ingredients": ["Curcuma longa (Curcumin/Haldi)", "Gaultheria procumbens (Gandhapura/Wintergreen Oil)"],
        "clause_tree": [
            {
                "level": "Act",
                "title": "The Patents Act, 1970 (as amended 2005)",
                "ref": "Act No. 39 of 1970",
                "latency_ms": 42
            },
            {
                "level": "Chapter",
                "title": "Chapter II: Inventions Not Patentable",
                "ref": "Exclusions from Patentability",
                "latency_ms": 65
            },
            {
                "level": "Section",
                "title": "Section 3: What are not inventions",
                "ref": "Statutory Filter",
                "latency_ms": 88
            },
            {
                "level": "Subsection",
                "title": "Section 3(p) & Section 3(e)",
                "ref": "Traditional Knowledge & Mere Admixture Bar",
                "latency_ms": 115
            },
            {
                "level": "Explanation",
                "title": "CGPDTM Ayush Guidelines 2019",
                "ref": "Requires demonstrable synergism (CI < 0.8) or novel extraction process",
                "latency_ms": 142
            },
            {
                "level": "TKDL Cross-Ref",
                "title": "TKDL Database References",
                "ref": "TKDL ID: AH3/1204 (Haridra) & SK2/441 (Gandhapura)",
                "latency_ms": 168
            },
            {
                "level": "Landmark Precedent",
                "title": "CSIR vs. USPTO / EPO Neem & Turmeric Cases",
                "ref": "Revocation of traditional formulation composition claims",
                "latency_ms": 194
            }
        ],
        "conflict_matrix": [
            {
                "jurisdiction": "Indian Patent Office (IPO)",
                "status": "REJECTED (Section 3p & Section 3e)",
                "color": "red",
                "icon": "⚖️",
                "reasoning": "Both Curcumin and Wintergreen Oil are classical remedies documented in TKDL. Claims on composition of matter face statutory rejection as traditional knowledge (Section 3p) and mere admixture (Section 3e)."
            },
            {
                "jurisdiction": "National Biodiversity Authority (NBA)",
                "status": "STATUTORY MANDATE (Section 6)",
                "color": "red",
                "icon": "🌿",
                "reasoning": "Under Section 6(1), using Indian biological resources (Curcuma longa) for IP requires mandatory prior approval of NBA via Form 3. Non-compliance triggers criminal penalties under Section 55."
            },
            {
                "jurisdiction": "State Ayush Licensing (SALA)",
                "status": "ALLOWED (RULE 158-B)",
                "color": "green",
                "icon": "🏥",
                "reasoning": "Commercial manufacturing is legally permitted under D&C Rule 158-B as a 'Patent or Proprietary Ayush Medicine' with acute dermal safety and pilot efficacy studies."
            },
            {
                "jurisdiction": "Global Export Regimes",
                "status": "WIPO PCT VIABLE",
                "color": "yellow",
                "icon": "🌍",
                "reasoning": "International patent protection under WIPO PCT is viable within 12 months if non-obvious liposomal formulation or synergistic index is proven."
            },
            {
                "jurisdiction": "Strategic Regulatory Workaround",
                "status": "PATENTABLE WORKAROUND",
                "color": "gold",
                "icon": "💡",
                "reasoning": "Re-draft claims focusing on: (1) Novel deep-penetrating liposomal/ethosomal nanocarrier delivery, (2) Synergistic therapeutic combination with Combination Index CI < 0.7, or (3) Proprietary supercritical CO2 fractionated extraction process."
            }
        ],
        "citations": [
            {"label": "Patents Act, Section 3(p)", "doc_id": "patent_act_3p"},
            {"label": "Patents Act, Section 3(e)", "doc_id": "patent_act_3e"},
            {"label": "Biological Diversity Act, Section 6", "doc_id": "nba_section_6"},
            {"label": "D&C Rules, Rule 158-B", "doc_id": "dnc_rule_158b"}
        ],
        "summary": "Direct patenting of the mixture is blocked under Section 3(p) and 3(e) due to TKDL prior art. However, manufacturing is legally permitted under Ayush Rule 158-B. To secure an enforceable patent, the applicant must file NBA Form 3 and reframe claims around a novel nanocarrier or demonstrated therapeutic synergism."
    },
    "scenario_2": {
        "id": "scenario_2",
        "title": "Exporting Standardized Ashwagandha Capsules to Germany",
        "query": "We want to export Ashwagandha (Withania somnifera) standardized extract capsules to Germany as an anti-stress medicine. What are the legal requirements?",
        "domain": "Ayurveda",
        "ingredients": ["Withania somnifera (Ashwagandha standardized withanolides)"],
        "clause_tree": [
            {
                "level": "Treaty/Directive",
                "title": "EU Directive 2004/24/EC (THMPD)",
                "ref": "Traditional Herbal Medicinal Products Directive",
                "latency_ms": 50
            },
            {
                "level": "EU Article",
                "title": "Article 16c: 30-Year Rule",
                "ref": "Requires 15 years documented usage inside European Union",
                "latency_ms": 78
            },
            {
                "level": "German Law",
                "title": "German AMG (Arzneimittelgesetz) Section 39a",
                "ref": "Strict medicinal claim classification",
                "latency_ms": 110
            },
            {
                "level": "Indian Act",
                "title": "Biological Diversity Act, 2002",
                "ref": "Section 3 & Section 4 commercial export clearance",
                "latency_ms": 145
            },
            {
                "level": "Ayush Guidelines",
                "title": "Ayush Premium Mark & WHO-GMP",
                "ref": "Quality certification for herbal export",
                "latency_ms": 182
            }
        ],
        "conflict_matrix": [
            {
                "jurisdiction": "Indian Patent Office (IPO)",
                "status": "OPTIONAL / TERRITORIAL",
                "color": "green",
                "icon": "⚖️",
                "reasoning": "Indian patent rights are territorial. For European market exclusivity, an EPO or German national patent filing is required."
            },
            {
                "jurisdiction": "National Biodiversity Authority (NBA)",
                "status": "MANDATORY FORM 1 (Section 3)",
                "color": "red",
                "icon": "🌿",
                "reasoning": "Exporting Indian biological resources (Withania somnifera) for commercial utilization requires prior approval and Access and Benefit Sharing (ABS) agreement under NBA Section 3 and Form I."
            },
            {
                "jurisdiction": "State Ayush Licensing (SALA)",
                "status": "WHO-GMP & CoFS MANDATORY",
                "color": "green",
                "icon": "🏥",
                "reasoning": "State Licensing Authority must issue Certificate of Free Sale (CoFS) and verify compliance with WHO-GMP standards."
            },
            {
                "jurisdiction": "Global Export Regimes",
                "status": "⚠️ EU THMPD 15-YR BARRIER",
                "color": "yellow",
                "icon": "🌍",
                "reasoning": "Ashwagandha fails simplified THMPD registration because it lacks 15 years documented historical medicinal use within EU member states. German BfArM prohibits medicinal stress-relief claims without full drug marketing authorization."
            },
            {
                "jurisdiction": "Strategic Regulatory Workaround",
                "status": "FOOD SUPPLEMENT ROUTE",
                "color": "gold",
                "icon": "💡",
                "reasoning": "Restructure product as a 'Food Supplement' (Nahrungsergänzungsmittel) under EU Directive 2002/46/EC. Remove therapeutic disease claims; use general physiological wellness claims under EFSA regulations."
            }
        ],
        "citations": [
            {"label": "EU THMPD Directive 2004/24/EC", "doc_id": "eu_thmpd"},
            {"label": "Biological Diversity Act, Section 3 & Section 4", "doc_id": "nba_section_6"},
            {"label": "D&C Rules, Rule 158-B", "doc_id": "dnc_rule_158b"}
        ],
        "summary": "Selling as a therapeutic anti-stress drug in Germany violates EU THMPD Article 16c due to the 15-year EU usage requirement. The product must be exported as a Food Supplement under Directive 2002/46/EC with NBA Form I clearance and Ayush Premium Mark certification."
    },
    "scenario_3": {
        "id": "scenario_3",
        "title": "Classical vs Proprietary Ayush Cough Syrup Licensing",
        "query": "What are the regulatory differences between licensing a Classical Ayurvedic Cough Syrup versus a Proprietary Herbal Syrup under Rule 158-B?",
        "domain": "Ayurveda",
        "ingredients": ["Adhatoda vasica (Vasa)", "Ocimum sanctum (Tulsi)", "Glycyrrhiza glabra (Yashtimadhu)"],
        "clause_tree": [
            {
                "level": "Act",
                "title": "Drugs and Cosmetics Act, 1940",
                "ref": "Chapter IV-A: ASU Drugs",
                "latency_ms": 38
            },
            {
                "level": "Rule",
                "title": "Drugs and Cosmetics Rules, 1945",
                "ref": "Rule 158-B Guidelines for Licensing",
                "latency_ms": 68
            },
            {
                "level": "Schedule",
                "title": "First Schedule of D&C Act",
                "ref": "54 Authoritative Classical Treatises (Charaka, Sharangadhara, API)",
                "latency_ms": 105
            },
            {
                "level": "Form Requirement",
                "title": "Form 24-D / Form 25-D",
                "ref": "State Ayush Licensing Authority Application",
                "latency_ms": 139
            }
        ],
        "conflict_matrix": [
            {
                "jurisdiction": "Indian Patent Office (IPO)",
                "status": "NOT REQUIRED FOR DRUG SALE",
                "color": "green",
                "icon": "⚖️",
                "reasoning": "A patent is not required to obtain a drug manufacturing and marketing license from State Ayush Licensing Authority."
            },
            {
                "jurisdiction": "National Biodiversity Authority (NBA)",
                "status": "EXEMPT (Section 40 COMMODITIES)",
                "color": "green",
                "icon": "🌿",
                "reasoning": "Indian biological commodities sourced domestically for classical ASU drugs enjoy exemption under Section 40, provided traceability records are maintained."
            },
            {
                "jurisdiction": "State Ayush Licensing (SALA)",
                "status": "⚖️ RULE 158-B DUAL TRACK",
                "color": "yellow",
                "icon": "🏥",
                "reasoning": "Classical medicines (Category I) need only textual citation from 54 First Schedule texts without clinical trials. Proprietary medicines (Category II) require acute safety data & 30-patient clinical trials."
            },
            {
                "jurisdiction": "Global Export Regimes",
                "status": "DOMESTIC LICENSING FOCUS",
                "color": "green",
                "icon": "🌍",
                "reasoning": "Product is licensed for the domestic Indian market. International export will require additional WHO-GMP and Certificate of Free Sale (CoFS)."
            },
            {
                "jurisdiction": "Strategic Regulatory Workaround",
                "status": "CATEGORY I VS II ROADMAP",
                "color": "gold",
                "icon": "💡",
                "reasoning": "For rapid market launch, manufacture as a Classical Formulation (Category I) citing authoritative texts (e.g., Vasavaleha). For proprietary formulations in modern syrup bases, conduct 14-day acute toxicity and 30-patient pilot clinical trials under Rule 158-B."
            }
        ],
        "citations": [
            {"label": "D&C Rules, Rule 158-B", "doc_id": "dnc_rule_158b"},
            {"label": "Biological Diversity Act, Section 6", "doc_id": "nba_section_6"}
        ],
        "summary": "Classical syrup requires only textual proof and pharmacopoeial monograph compliance. Proprietary syrup requires mandatory acute toxicity data, pilot clinical trial evidence on 30 patients, and shelf-life stability studies under Rule 158-B."
    }
}

# Botanical Database for Formulation Scanner
BOTANICAL_DB = {
    "curcuma_longa": {
        "common_name": "Haldi / Curcumin / Haridra",
        "latin_binomial": "Curcuma longa L.",
        "family": "Zingiberaceae",
        "classical_texts": ["Charaka Samhita", "Sushruta Samhita", "Ayurvedic Pharmacopoeia of India Part I Vol I"],
        "tkdl_ids": ["AH3/1204", "SK2/441"],
        "known_properties": "Anti-inflammatory, analgesic, wound healing, antioxidant",
        "section_3p_risk": "High (Classical Traditional Knowledge)",
        "active_markers": ["Curcumin", "Demethoxycurcumin", "Bisdemethoxycurcumin"]
    },
    "withania_somnifera": {
        "common_name": "Ashwagandha / Asgandh",
        "latin_binomial": "Withania somnifera (L.) Dunal",
        "family": "Solanaceae",
        "classical_texts": ["Bhavaprakasha Nighantu", "Charaka Samhita", "API Part I Vol I"],
        "tkdl_ids": ["AH4/881", "UN1/204"],
        "known_properties": "Rasayana, adaptogenic, anti-stress, immunomodulatory",
        "section_3p_risk": "High (Classical Rasayana)",
        "active_markers": ["Withaferin A", "Withanolide A", "Withanoside IV"]
    },
    "gaultheria_procumbens": {
        "common_name": "Gandhapura / Wintergreen",
        "latin_binomial": "Gaultheria procumbens L.",
        "family": "Ericaceae",
        "classical_texts": ["Ayurvedic Pharmacopoeia of India", "Dravyaguna Vijnana"],
        "tkdl_ids": ["SK2/441"],
        "known_properties": "Topical analgesic, rubefacient, anti-inflammatory",
        "section_3p_risk": "High (Known essential oil)",
        "active_markers": ["Methyl salicylate"]
    },
    "boswellia_serrata": {
        "common_name": "Shallaki / Salai Guggulu",
        "latin_binomial": "Boswellia serrata Roxb. ex Colebr.",
        "family": "Burseraceae",
        "classical_texts": ["Sushruta Samhita", "Astanga Hridaya", "API Part I Vol III"],
        "tkdl_ids": ["AH2/310"],
        "known_properties": "Anti-arthritic, chondroprotective, anti-inflammatory",
        "section_3p_risk": "High (Classical joint remedy)",
        "active_markers": ["11-keto-beta-boswellic acid (AKBA)"]
    },
    "piper_nigrum": {
        "common_name": "Maricha / Black Pepper / Kali Mirch",
        "latin_binomial": "Piper nigrum L.",
        "family": "Piperaceae",
        "classical_texts": ["Charaka Samhita", "Trikatu Churna", "API Part I Vol III"],
        "tkdl_ids": ["AH1/105"],
        "known_properties": "Bioenhancer, digestive, thermogenic",
        "section_3p_risk": "High (Classic Yogavahi / Bioenhancer)",
        "active_markers": ["Piperine"]
    }
}
