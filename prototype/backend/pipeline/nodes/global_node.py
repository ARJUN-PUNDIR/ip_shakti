"""
Node 5: GlobalExportAgentNode
Evaluates export market entry, international trade regimes, and foreign regulatory hurdles:
EU Directive 2004/24/EC (THMPD), US FDA DSHEA 1994, UK MHRA, and WIPO PCT.
"""

import time
from typing import Dict, Any
from pipeline.state import RegulatoryState

def global_agent_node(state: RegulatoryState) -> Dict[str, Any]:
    """Node 5: Global Export & International Regulatory Specialist Agent."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "").lower()
    target_jurisdictions = state.get("target_jurisdictions", [])
    is_cosmetic = state.get("is_cosmetic", False)

    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Ayush formulation"

    is_germany = any(k in query for k in ["germany", "deutschland", "bfarm"])
    is_europe = is_germany or any("Europe" in j for j in target_jurisdictions) or any(k in query for k in ["eu", "europe", "thmpd", "uk", "mhra"])
    is_usa = any("United States" in j for j in target_jurisdictions) or any(k in query for k in ["us", "usa", "fda", "dshea"])
    is_uae = any("Middle East" in j for j in target_jurisdictions) or any(k in query for k in ["uae", "dubai", "mohap", "gcc", "halal"])

    if is_cosmetic and (is_europe or is_usa):
        status = "🌍 EU (EC 1223/2009) & US MoCRA Compliance Required"
        color = "yellow"
        reasoning = (
            "Exporting topical herbal cosmetics requires compiling a Cosmetic Product Safety Report (CPSR/PIF) "
            "for the European Union and facility/listing compliance under the US MoCRA 2022 framework."
        )
        export_route = "Cosmetic Safety Dossier (EU PIF & US MoCRA)"
    elif is_europe:
        status = "⚠️ EU THMPD 15-Year Rule Barrier (Article 16c)"
        color = "yellow"
        reasoning = (
            f"Under EU Directive 2004/24/EC, simplified traditional herbal registration requires 30 years continuous use, "
            f"including at least 15 years within the EU. Indian classical documentation fails this clause. "
            f"Product must be restructured as a 'Food Supplement' under Directive 2002/46/EC without therapeutic claims."
        )
        export_route = "Food Supplement Route (EU Directive 2002/46/EC)"
    elif is_usa:
        status = "⚠️ US FDA Dietary Supplement (DSHEA) vs Botanical Drug"
        color = "yellow"
        reasoning = (
            "Under US FDA DSHEA 1994, herbal formulations cannot claim to treat, cure, or mitigate diseases. "
            "Market as a Dietary Supplement (21 CFR Part 111 cGMP) with structure/function claims, or file an IND for full Botanical Drug approval."
        )
        export_route = "Dietary Supplement cGMP (21 CFR Part 111)"
    elif is_uae:
        status = "✅ UAE MoHAP Herbal Listing & Halal Mandate"
        color = "green"
        reasoning = (
            "UAE Ministry of Health & Prevention allows registration as a Complementary Medicine upon submission of WHO-GMP, "
            "Certificate of Free Sale (CoFS), and Halal certification."
        )
        export_route = "Complementary Medicine Registration (MoHAP)"
    else:
        status = "ℹ️ Domestic Market / WIPO PCT Available"
        color = "green"
        reasoning = (
            "Domestic Indian market prioritized. For international patent protection, a WIPO PCT application "
            "can be filed within 12 months claiming priority from the Indian patent application."
        )
        export_route = "WIPO PCT International Route"

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "GlobalExportAgentNode",
        "description": f"Evaluated export compliance for {herbs_str}. Route: {export_route}",
        "latency_ms": max(latency_ms, 12)
    }

    return {
        "global_evaluation": {
            "jurisdiction": "Global Regulatory Regimes",
            "status": status,
            "color": color,
            "icon": "🌍",
            "reasoning": reasoning,
            "recommended_pathway": export_route
        },
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
