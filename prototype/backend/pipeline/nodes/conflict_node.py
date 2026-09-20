"""
Node 6: ConflictDetectorNode
Aggregates independent regulatory agent findings and detects cross-statutory collisions:
- Patent Law (Section 3p/3e) vs Ayush Drug Licensing (Rule 158-B)
- Biodiversity Act (Section 6) vs Indian Patent Office Grant
- Domestic ASU Approval vs International Import Restrictions (EU THMPD 15-Yr Rule)
"""

import time
from typing import Dict, Any, List
from pipeline.state import RegulatoryState

def conflict_detector_node(state: RegulatoryState) -> Dict[str, Any]:
    """Node 6: Cross-Regulatory Collision & Conflict Detection Node (Jurisdiction-Aware)."""
    start_time = time.time()
    jurisdiction = state.get("jurisdiction", "india")

    detected_collisions = []

    if jurisdiction == "international":
        wipo = state.get("wipo_evaluation", {})
        cbd = state.get("cbd_evaluation", {})
        eu = state.get("eu_evaluation", {})
        us = state.get("us_evaluation", {})
        conflict_matrix = [wipo, cbd, eu, us]

        # Collision 1: EU THMPD 15-Year Rule vs Traditional Use
        if "EU THMPD" in eu.get("status", "") or "Barrier" in eu.get("status", ""):
            detected_collisions.append(
                "EXPORT MARKET BARRIER [EU THMPD 15-Year Rule]: Classical Ayush formulation cannot obtain simplified "
                "medicinal registration in Europe under Directive 2004/24/EC due to lack of 15-year continuous use within the EU. "
                "Must restructure as a Food Supplement under Directive 2002/46/EC."
            )

        # Collision 2: WIPO GRATK 2024 Mandatory Origin Disclosure
        if "GRATK" in wipo.get("status", ""):
            detected_collisions.append(
                "MANDATORY DISCLOSURE [WIPO GRATK 2024]: International patent applications claiming Ayush biological resources "
                "must disclose India as the country of origin. Concealing origin triggers patent invalidation in treaty member states."
            )

        # Collision 3: Budapest Treaty Deposition for Fermented Formulations
        if "Budapest" in cbd.get("status", ""):
            detected_collisions.append(
                "BIOLOGICAL DEPOSIT MANDATE [Budapest Treaty]: Proprietary microbial strains for Asava/Arishta fermentation "
                "require prior physical deposition at an International Depositary Authority (MTCC IMTECH) before patent grant."
            )

        # Collision 4: US FDA Disease Claims vs DSHEA Supplement Boundary
        if "DSHEA" in us.get("status", ""):
            detected_collisions.append(
                "LABELING RESTRICTION [US FDA DSHEA]: Product cannot carry therapeutic cure claims in the US market without "
                "Investigational New Drug (IND) approval. Must formulate claims as structure/function wellness statements."
            )
    else:
        # National (India) Regime: IPO, NBA, SALA, Allied (FSSAI/DMROA)
        ipo = state.get("ipo_evaluation", {})
        nba = state.get("nba_evaluation", {})
        ayush = state.get("ayush_evaluation", {})
        allied = state.get("allied_evaluation", {})
        conflict_matrix = [ipo, nba, ayush, allied]

        # Check Collision 1: IPO Rejection vs Ayush Manufacturing Approval
        if ipo.get("color") == "red" and ayush.get("color") in ["green", "yellow"]:
            detected_collisions.append(
                "COLLISION DETECTED [IPO vs SALA]: Formulation is permitted for commercial manufacture under "
                "Ayush Rule 158-B, but direct patent protection is barred under Section 3(p) as traditional knowledge."
            )

        # Check Collision 2: NBA Prior Approval vs IPO Patent Grant
        if nba.get("color") == "red" and ipo.get("color") in ["green", "yellow"]:
            detected_collisions.append(
                "STATUTORY PRE-REQUISITE [NBA vs IPO]: Indian Patent Office cannot grant patent rights until the applicant "
                "furnishes unconditional prior approval from the National Biodiversity Authority under Section 6(1)."
            )

        # Check Collision 3: SALA License vs DMROA Advertising Bar
        if allied.get("color") == "red":
            detected_collisions.append(
                "MARKETING CONFLICT [SALA vs DMROA 1954]: While authorized for manufacture under Rule 158-B, "
                "advertising therapeutic cures for scheduled diseases (arthritis, diabetes, cancer) is strictly punishable under Section 3 of DMROA 1954."
            )

        # Check Collision 4: FSSAI Ayurveda-Aahar vs ASU Drug Classification
        if "Ayurveda-Aahar" in allied.get("status", "") and "Proprietary" in ayush.get("status", ""):
            detected_collisions.append(
                "DUAL CLASSIFICATION CHOICE [FSSAI vs SALA]: Formulation qualifies as an Ayurveda-Aahar food product for rapid "
                "non-clinical commercialization, but claiming specific therapeutic indications requires a formal Rule 158-B ASU Drug License."
            )

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "ConflictDetectorNode",
        "description": f"Analyzed {jurisdiction.upper()} regulatory vectors. Detected {len(detected_collisions)} statutory collisions.",
        "latency_ms": max(latency_ms, 8)
    }

    return {
        "conflict_matrix": conflict_matrix,
        "detected_collisions": detected_collisions,
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
