"""
Node 3: BiodiversityAgentNode
Evaluates statutory mandates under the Biological Diversity Act, 2002 (amended 2023).
Calculates ABS obligations, Section 6 prior approval pre-requisites, and Section 55 liabilities.
"""

import time
from typing import Dict, Any
from pipeline.state import RegulatoryState

def biodiversity_agent_node(state: RegulatoryState) -> Dict[str, Any]:
    """Node 3: National Biodiversity Authority (NBA) Specialist Agent."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "").lower()
    is_foreign = state.get("is_foreign_entity", False)
    target_jurisdictions = state.get("target_jurisdictions", [])
    is_export = any("Europe" in j or "United States" in j or "Middle East" in j for j in target_jurisdictions) or "export" in query
    is_food = state.get("is_food_supplement", False)

    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Indian biological material"

    if is_foreign:
        status = "🚨 NBA Section 3 Strict Scrutiny (Foreign Entity)"
        color = "red"
        reasoning = (
            "Under Section 3(2) of Biological Diversity Act, foreign individuals, NRIs, and Indian companies with any foreign equity "
            "are strictly prohibited from accessing Indian biological resources without prior NBA approval via Form 1. Penalty: Up to 5 yrs prison (Section 55)."
        )
        form_req = "NBA Form 1 (Access for Foreign Entity / Commercial Utilization)"
    elif is_export:
        status = "🚨 NBA Form 1 Export Mandate (Section 3 & Section 4)"
        color = "red"
        reasoning = (
            f"Transferring Indian biological resources ({herbs_str}) abroad for commercial utilization mandates prior approval "
            "from the National Biodiversity Authority under Section 3 & Form 1, with Access and Benefit Sharing (ABS) agreement."
        )
        form_req = "NBA Form 1 (Commercial Utilization / Export)"
    elif is_food and not any(k in query for k in ["patent", "ipr"]):
        status = "✅ Section 40 Commodity Exemption"
        color = "green"
        reasoning = (
            "Domestic food products utilizing normally traded commodities (NTCO) declared under Section 40 "
            "are exempt from NBA approvals, provided raw materials are sourced from domestic registered markets."
        )
        form_req = "None (Section 40 Notification)"
    elif botanicals or "patent" in query or "ip" in query:
        status = "🚨 NBA Form 3 Mandatory Prior Approval (Section 6)"
        color = "red"
        reasoning = (
            f"Under Section 6(1), applying for any Intellectual Property Right based on Indian biological resources ({herbs_str}) "
            "requires mandatory prior approval from the NBA via Form 3 before patent grant. Non-compliance violates Section 55."
        )
        form_req = "NBA Form 3 (Application for IPR Approval)"
    else:
        status = "✅ NBA Compliance Neutral"
        color = "green"
        reasoning = "No biological material collection from Indian territorial jurisdiction identified."
        form_req = "None"

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "BiodiversityAgentNode",
        "description": f"Evaluated BD Act Section 6/3/55 for {herbs_str}. Status: {status}",
        "latency_ms": max(latency_ms, 10)
    }

    return {
        "nba_evaluation": {
            "jurisdiction": "National Biodiversity Authority (NBA)",
            "status": status,
            "color": color,
            "icon": "🌿",
            "reasoning": reasoning,
            "statutory_act": "The Biological Diversity Act, 2002 (as amended 2023) Section 6, Section 3, Section 55",
            "mandatory_form": form_req,
            "abs_levy_pct": "0.1% - 0.5% ex-factory sales"
        },
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
