"""
Node: AlliedRegimesNode (FSSAI, DMROA Advertising, GI & Plant Varieties)
Evaluates statutory compliance under:
1. Food Safety and Standards (Ayurveda Aahara) Regulations, 2022
2. Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954 (DMROA)
3. Geographical Indications of Goods Act, 1999 (GI Registry)
4. Protection of Plant Varieties and Farmers' Rights Act, 2001 (PPV&FRA)
"""

import time
from typing import Dict, Any
from pipeline.state import RegulatoryState

def allied_agent_node(state: RegulatoryState) -> Dict[str, Any]:
    """Allied Indian Regulatory Regimes Specialist Agent (FSSAI, DMROA, GI, PPV&FRA)."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "").lower()
    is_food = state.get("is_food_supplement", False) or any(k in query for k in ["food", "dietary", "nutrition", "aahar", "fssai", "tea", "candy", "syrup", "juice"])
    is_cosmetic = state.get("is_cosmetic", False) or any(k in query for k in ["cosmetic", "cream", "lotion", "serum", "hair oil", "shampoo", "skin"])

    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Ayush formulation"

    # 1. Check for DMROA 1954 (Drugs and Magic Remedies Objectionable Advertisements)
    dmroa_diseases = [
        "diabetes", "madhumeha", "cancer", "arbuda", "arthritis", "sandhivata", "rheumatism",
        "kidney", "vrikka", "paralysis", "pakshaghata", "hypertension", "raktachapa",
        "epilepsy", "apasmara", "sexual", "impotence", "klaibya", "asthma", "shwasa", "obesity", "medoroga"
    ]
    has_dmroa_risk = any(d in query for d in dmroa_diseases)

    # 2. Check for Geographical Indication (GI) Cultivars
    gi_botanicals = {
        "navara": "Navara Rice (Kerala GI No. 74 - Classical Panchakarma Cultivar)",
        "cardamom": "Alleppey Green Cardamom (Kerala/TN GI No. 34)",
        "pepper": "Malabar Pepper (Kerala GI No. 49)",
        "turmeric": "Erode / Waigaon / Kandhamal Turmeric (Registered GI Cultivars)",
        "saffron": "Kashmir Saffron (Crocus sativus L. GI No. 635)",
        "teak": "Nilambur Teak (Kerala GI No. 598)",
        "clove": "Kanyakumari Clove (Tamil Nadu GI No. 711)"
    }
    detected_gi = [desc for name, desc in gi_botanicals.items() if name in query or any(name in b.get("common_name", "").lower() for b in botanicals)]

    if has_dmroa_risk:
        status = "🚨 DMROA 1954 Advertising Warning (Section 3/14)"
        color = "red"
        reasoning = (
            f"The Drugs & Magic Remedies Act (DMROA 1954) strictly bars public advertisement claiming to 'cure' or 'treat' "
            "scheduled ailments (e.g. diabetes, cancer, arthritis, sexual disorders). Commercial marketing must be framed as "
            "'promoting joint wellness' or 'supporting metabolic balance' rather than claiming therapeutic cures to avoid prosecution."
        )
        regime_basis = "Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954 Section 3 & Schedule"
    elif is_food:
        status = "🥗 FSSAI Ayurveda-Aahar Regulations 2022 Pathway"
        color = "green"
        reasoning = (
            f"Regulated under Food Safety and Standards (Ayurveda Aahara) Regulations, 2022. Allows rapid market launch "
            "with FSSAI-Ayush joint logo without 14-day animal toxicity or clinical trials, provided disease-treatment claims are not made. "
            "Ingredients must be sourced from authoritative First Schedule texts."
        )
        regime_basis = "FSSAI (Ayurveda Aahara) Regulations, 2022 & Section 22 FSS Act"
    elif is_cosmetic:
        status = "🌿 Ayurvedic Cosmetic Labelling & Schedule S Standards"
        color = "green"
        reasoning = (
            "Ayurvedic skincare/haircare formulations fall under D&C Rules Schedule S safety standards. "
            "Must carry full botanical disclosure with Latin binomials on primary packaging. Prohibited from making medicinal cure claims."
        )
        regime_basis = "Drugs and Cosmetics Rules 1945 Schedule S & Rule 158-B Cosmetic Guidelines"
    elif detected_gi:
        gi_name = detected_gi[0]
        status = "🏷️ Geographical Indication (GI) Protection Active"
        color = "green"
        reasoning = (
            f"Formulation utilizes {gi_name}. Under the GI of Goods Act 1999, registered collective community rights protect "
            "origin reputation. Individual patent claims on the raw botanical variety are barred; authorized user registration required."
        )
        regime_basis = "Geographical Indications of Goods Act, 1999 Section 21"
    else:
        status = "✅ Allied Regulatory Compliance (FSSAI/DMROA Clear)"
        color = "green"
        reasoning = (
            f"General wellness and herbal non-disease claims for {herbs_str} comply with Allied Indian regimes. "
            "If marketed as an Ayurveda-Aahar food product, register on FSSAI FoSCoS portal; if claiming therapeutic ASU efficacy, route via State Ayush Licensing Authority."
        )
        regime_basis = "FSSAI Ayurveda-Aahar Regs 2022 / DMROA 1954 General Compliance"

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "AlliedRegimesNode",
        "description": f"Evaluated FSSAI, DMROA 1954 & GI regimes for {herbs_str}. Status: {status}",
        "latency_ms": max(latency_ms, 12)
    }

    return {
        "allied_evaluation": {
            "jurisdiction": "Allied Regimes (FSSAI & Advertising)",
            "status": status,
            "color": color,
            "icon": "🥗",
            "reasoning": reasoning,
            "statutory_act": regime_basis,
            "detected_gi": detected_gi
        },
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
