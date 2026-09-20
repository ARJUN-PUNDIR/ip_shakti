"""
International Specialist Pipeline Nodes for IP-SAKTI Sahayak
Implements 4 distinct global regulatory and treaty agents:
1. WIPO & GRATK Treaty Specialist Node (WIPO GRATK Treaty 2024 & PCT)
2. CBD, Nagoya Protocol & Budapest Treaty Specialist Node (Nagoya ABS & Microorganism Deposits)
3. European Union (EMA / HMPC) Market Access Specialist Node (THMPD 15-Yr Rule & Food Supplements)
4. US FDA & Global Regulators Specialist Node (DSHEA 1994, Botanical Drugs, Madrid & Hague Systems)
"""

import time
from typing import Dict, Any
from pipeline.state import RegulatoryState

def wipo_gratk_agent_node(state: RegulatoryState) -> Dict[str, Any]:
    """Agent 1: WIPO & GRATK Treaty 2024 Specialist Agent."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "").lower()
    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Ayush formulation"

    # WIPO GRATK Treaty (Adopted May 2024) mandates origin disclosure
    status = "🌐 WIPO GRATK 2024 Mandatory Origin Disclosure"
    color = "yellow"
    reasoning = (
        f"Under the historic WIPO GRATK Treaty (adopted May 2024), patent applications in contracting states based on "
        f"{herbs_str} MUST disclose the country of origin (India) and the indigenous/local community providing associated "
        "traditional knowledge. Patent applications concealing biological provenance face revocation or non-grant."
    )

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "WIPOGratkAgentNode",
        "description": f"Evaluated WIPO GRATK 2024 & PCT filing for {herbs_str}. Status: {status}",
        "latency_ms": max(latency_ms, 12)
    }

    return {
        "wipo_evaluation": {
            "jurisdiction": "WIPO & GRATK Treaty 2024",
            "status": status,
            "color": color,
            "icon": "🌐",
            "reasoning": reasoning,
            "statutory_act": "WIPO Treaty on Intellectual Property, Genetic Resources & Associated TK (2024) & PCT",
            "filing_route": "WIPO PCT Chapter I International Application with Form GRATK Origin Disclosure"
        },
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }


def cbd_nagoya_agent_node(state: RegulatoryState) -> Dict[str, Any]:
    """Agent 2: CBD, Nagoya Protocol & Budapest Treaty Specialist Agent."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "").lower()
    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Biological material"

    # Check for fermentation / microbial / asava / arishta (Budapest Treaty trigger)
    is_microbial = any(k in query for k in ["ferment", "asava", "arishta", "microb", "probiotic", "yeast", "bacteria", "dhataki", "culture", "fungus"])

    if is_microbial:
        status = "🔬 Budapest Treaty Microorganism Deposit Mandate"
        color = "red"
        reasoning = (
            "Fermented Ayurvedic formulations (Asavas, Arishtas, or microbial bio-transforms) claiming proprietary strains "
            "require mandatory physical deposition at an International Depositary Authority (IDA) under the Budapest Treaty "
            "(e.g. MTCC IMTECH Chandigarh) prior to patent filing, obtaining an official accession number."
        )
        treaty_basis = "Budapest Treaty on the International Recognition of the Deposit of Microorganisms Rule 6.1"
    else:
        status = "🧬 Nagoya Protocol ABS & Prior Informed Consent"
        color = "yellow"
        reasoning = (
            f"Under the Convention on Biological Diversity (CBD) and Nagoya Protocol, international commercial utilization of "
            f"{herbs_str} requires Prior Informed Consent (PIC) and Mutually Agreed Terms (MAT) with the National Focal Point. "
            "Guarantees fair and equitable sharing of benefits arising from commercial utilization."
        )
        treaty_basis = "Nagoya Protocol on Access to Genetic Resources and Benefit-Sharing (Articles 6 & 15)"

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "CbdNagoyaAgentNode",
        "description": f"Evaluated Nagoya ABS & Budapest deposit for {herbs_str}. Status: {status}",
        "latency_ms": max(latency_ms, 12)
    }

    return {
        "cbd_evaluation": {
            "jurisdiction": "CBD, Nagoya & Budapest Treaty",
            "status": status,
            "color": color,
            "icon": "🧬",
            "reasoning": reasoning,
            "statutory_act": treaty_basis,
            "compliance_requirement": "International ABS Clearing-House (ABSCH) & MTCC Deposition"
        },
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }


def eu_thmpd_agent_node(state: RegulatoryState) -> Dict[str, Any]:
    """Agent 3: European Union (EMA / HMPC) Market Access Specialist Agent."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "").lower()
    is_cosmetic = state.get("is_cosmetic", False) or any(k in query for k in ["cosmetic", "cream", "skin", "serum", "lotion", "oil"])
    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Botanical extract"

    if is_cosmetic:
        status = "🧴 EU Cosmetic Regulation (EC 1223/2009) PIF Required"
        color = "yellow"
        reasoning = (
            "Exporting to the EU as a topical cosmetic requires compiling a Product Information File (PIF), "
            "conducting a formal Cosmetic Product Safety Report (CPSR Part A & B) by an EU-qualified safety assessor, "
            "and notification on the European Cosmetic Product Notification Portal (CPNP)."
        )
        route = "EU Cosmetic CPNP Notification & Safety Dossier (EC 1223/2009)"
    else:
        status = "⚠️ EU THMPD 15-Year Rule Barrier (Article 16c)"
        color = "yellow"
        reasoning = (
            f"Under EU Directive 2004/24/EC (THMPD), simplified herbal medicine registration requires documented evidence "
            f"of 30 years continuous traditional use, including at least 15 years inside the European Union. "
            f"Indian classical formulations fail this clause. Strategic Workaround: Restructure export as a 'Food Supplement' "
            "under EU Directive 2002/46/EC without therapeutic disease-curing claims."
        )
        route = "Food Supplement Route (Directive 2002/46/EC) or Novel Food (EU 2015/2283)"

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "EuThmpdAgentNode",
        "description": f"Evaluated EU THMPD / Food Supplement route for {herbs_str}. Route: {route}",
        "latency_ms": max(latency_ms, 12)
    }

    return {
        "eu_evaluation": {
            "jurisdiction": "European Union (EMA / THMPD)",
            "status": status,
            "color": color,
            "icon": "🇪🇺",
            "reasoning": reasoning,
            "statutory_act": "EU Directive 2004/24/EC (THMPD) & Directive 2002/46/EC",
            "recommended_pathway": route
        },
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }


def us_fda_agent_node(state: RegulatoryState) -> Dict[str, Any]:
    """Agent 4: US FDA & Global Regulators Specialist Agent."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "").lower()
    is_cosmetic = state.get("is_cosmetic", False) or any(k in query for k in ["cosmetic", "cream", "skin", "serum", "lotion", "oil"])
    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Botanical extract"

    if is_cosmetic:
        status = "💄 US FDA MoCRA 2022 Facility Registration"
        color = "green"
        reasoning = (
            "Under the Modernization of Cosmetics Regulation Act of 2022 (MoCRA), foreign manufacturing facilities "
            "must register with US FDA, list all cosmetic product ingredients, maintain safety substantiation records, "
            "and establish an adverse event reporting pipeline."
        )
        route = "US FDA MoCRA Cosmetics Facility Listing & Safety Substantiation"
    else:
        status = "🇺🇸 US FDA DSHEA 1994 Dietary Supplement Route"
        color = "green"
        reasoning = (
            f"Under the Dietary Supplement Health and Education Act of 1994 (DSHEA, 21 U.S.C. § 321(ff)), {herbs_str} "
            "can enter the US market as a Dietary Supplement adhering to 21 CFR Part 111 cGMP. "
            "Labels may carry Structure/Function claims (e.g. 'supports joint mobility') with mandatory FDA disclaimer, "
            "strictly avoiding disease treatment claims. For therapeutic claims, file an IND under FDA Botanical Drug Guidance."
        )
        route = "Dietary Supplement (21 CFR Part 111 cGMP) / Madrid System Trademark"

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "UsFdaAgentNode",
        "description": f"Evaluated US FDA DSHEA & MoCRA for {herbs_str}. Route: {route}",
        "latency_ms": max(latency_ms, 12)
    }

    return {
        "us_evaluation": {
            "jurisdiction": "US FDA & Global Regulators",
            "status": status,
            "color": color,
            "icon": "🇺🇸",
            "reasoning": reasoning,
            "statutory_act": "US FDA DSHEA 1994 (21 CFR Part 111 cGMP) & Botanical Drug Guidance",
            "recommended_pathway": route
        },
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
