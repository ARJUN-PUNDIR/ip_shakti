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
    """Node 6: Cross-Regulatory Collision & Conflict Detection Node."""
    start_time = time.time()
    ipo = state.get("ipo_evaluation", {})
    nba = state.get("nba_evaluation", {})
    ayush = state.get("ayush_evaluation", {})
    glo = state.get("global_evaluation", {})

    conflict_matrix = [ipo, nba, ayush, glo]
    detected_collisions = []

    # Check Collision 1: IPO Rejection vs Ayush Manufacturing Approval
    if ipo.get("color") == "red" and ayush.get("color") in ["green", "yellow"]:
        collision = (
            "COLLISION DETECTED [IPO vs SALA]: Formulation is permitted for commercial manufacture under "
            "Ayush Rule 158-B, but direct patent protection is barred under Section 3(p) as traditional knowledge."
        )
        detected_collisions.append(collision)

    # Check Collision 2: NBA Prior Approval vs IPO Patent Grant
    if nba.get("color") == "red" and ipo.get("color") in ["green", "yellow"]:
        collision = (
            "STATUTORY PRE-REQUISITE [NBA vs IPO]: Indian Patent Office cannot grant patent rights until the applicant "
            "furnishes unconditional prior approval from the National Biodiversity Authority under Section 6(1)."
        )
        detected_collisions.append(collision)

    # Check Collision 3: Domestic Ayush Licensure vs EU THMPD 15-Year Rule
    if "EU THMPD" in glo.get("status", "") and ayush.get("color") == "green":
        collision = (
            "EXPORT MARKET BARRIER [SALA vs EMA]: Classical Ayurvedic formulation authorized in India cannot be sold "
            "as a therapeutic medicine in the EU due to Directive 2004/24/EC 15-year European usage requirement."
        )
        detected_collisions.append(collision)

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "ConflictDetectorNode",
        "description": f"Analyzed 4 regulatory vectors. Detected {len(detected_collisions)} statutory collisions.",
        "latency_ms": max(latency_ms, 8)
    }

    return {
        "conflict_matrix": conflict_matrix,
        "detected_collisions": detected_collisions,
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
