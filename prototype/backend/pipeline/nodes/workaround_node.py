"""
Node 7: WorkaroundSynthesizerNode
Generates strategic patent workarounds, formulation re-engineering strategies,
and regulatory filing roadmaps to overcome statutory collisions.
"""

import time
from typing import Dict, Any, List
from pipeline.state import RegulatoryState

def workaround_synthesizer_node(state: RegulatoryState) -> Dict[str, Any]:
    """Node 7: Strategic Formulation & Workaround Synthesis Node."""
    start_time = time.time()
    botanicals = state.get("detected_botanicals", [])
    query = state.get("query", "")
    q = query.lower()
    ipo = state.get("ipo_evaluation", {})
    ayush = state.get("ayush_evaluation", {})
    glo = state.get("global_evaluation", {})
    is_cosmetic = state.get("is_cosmetic", False)
    is_food = state.get("is_food_supplement", False)
    is_factory = state.get("is_factory_setup", False)
    is_foreign = state.get("is_foreign_entity", False)
    dosage = state.get("dosage_form", "")

    herbs_str = ", ".join([b["common_name"] for b in botanicals]) if botanicals else "Herbal / Botanical Formulation"

    # Determine optimal strategic workaround
    if is_factory:
        workaround = (
            "Infrastructure & Licensing Strategy: If setting up a 1,200 sq. ft. Schedule T facility is capital-prohibitive, "
            "apply for a **Loan License (Form 24-E)** to manufacture your proprietary formulation at an established GMP facility, "
            "allowing commercial launch within 30-45 days."
        )
        roadmap = [
            "1. Prepare technical specification and batch formulation dossier.",
            "2. Execute third-party contract manufacturing agreement with GMP certified unit.",
            "3. Submit Form 24-E to State Ayush Licensing Authority with technical person details.",
            "4. Obtain Form 24-E license approval and commence commercial sales."
        ]
    elif is_foreign:
        workaround = (
            "Foreign Investment Compliance Roadmap: Establish an Indian incorporated subsidiary and submit **NBA Form 1** "
            "for prior commercial access approval. Negotiate an Access & Benefit Sharing (ABS) agreement before initiating raw material procurement."
        )
        roadmap = [
            "1. Incorporate Indian Private Limited entity with DPIIT reporting.",
            "2. File NBA Form 1 with proposed biological material list and research intent.",
            "3. Execute ABS agreement with National Biodiversity Authority.",
            "4. File patent or manufacturing applications with verified NBA approval on record."
        ]
    elif "EU THMPD" in glo.get("status", ""):
        workaround = (
            "Strategic Export Restructuring: (1) Re-classify product as a 'Food Supplement' (Nahrungsergänzungsmittel) under EU Directive 2002/46/EC; "
            "(2) Eliminate all curative disease claims from consumer labels; use EFSA-permitted botanical physiological wellness claims; "
            "(3) File NBA Form 1 for commercial export approval; (4) Obtain Ayush Premium Mark and WHO-GMP certification."
        )
        roadmap = [
            "1. Re-format packaging to comply with EU Directive 2002/46/EC (Food Supplement).",
            "2. Conduct batch heavy metal, pesticide, and aflatoxin screening per Ph. Eur. standards.",
            "3. Apply for NBA Form 1 export clearance from the National Biodiversity Authority.",
            "4. Obtain Certificate of Free Sale (CoFS) from State Ayush Licensing Authority."
        ]
    elif is_cosmetic:
        workaround = (
            "Topical Formulation Strategy: To patent: Formulate into a lipid nanocarrier or cold-process micro-emulsion (particle size < 180 nm) "
            "demonstrating unexpected dermal penetration. To sell immediately: Obtain a Proprietary Ayush manufacturing license under Form 24-D."
        )
        roadmap = [
            "1. Develop lipid nano-vesicular carrier or phospholipid complex to overcome Section 3(p) & Section 3(e).",
            "2. Conduct in-vitro Franz diffusion cell transdermal flux assays.",
            "3. File provisional patent Form 1 & Form 2 Complete Specification.",
            "4. Submit NBA Form 3 prior to patent grant."
        ]
    elif is_food:
        workaround = (
            "Nutraceutical Portfolio Strategy: Launch wellness blends under FSSAI Ayurveda Aahara Regulations 2022 for immediate retail, "
            "while maintaining separate therapeutic lines under formal State Ayush Rule 158-B manufacturing licenses."
        )
        roadmap = [
            "1. Formulate strictly with ingredients approved in Ayurveda Aahara Schedule.",
            "2. Ensure zero disease treatment claims on product labels.",
            "3. Register on FSSAI FoSCoS portal under Category 13 / Ayurveda Aahara.",
            "4. Procure raw materials under Section 40 normally traded commodity norms."
        ]
    else:
        workaround = (
            f"Defensible Patent & Commercial Roadmap for {herbs_str}: (1) Re-engineer the formulation into an advanced "
            "phospholipid nanocarrier, liposome, or standardized supercritical CO2 fraction; (2) Conduct in-vitro Chou-Talalay assays "
            "demonstrating Combination Index CI < 0.75; (3) File NBA Form 3 prior to patent grant; (4) Obtain Rule 158-B manufacturing license for market entry."
        )
        roadmap = [
            f"1. Formulate {herbs_str} into a phyto-phospholipid complex or standardized extract.",
            "2. Generate quantitative synergy assay data demonstrating Combination Index CI < 0.75.",
            "3. File Indian Patent Form 2 complete specification with process and carrier claims.",
            "4. Submit NBA Form 3 to National Biodiversity Authority prior to patent grant.",
            "5. Apply for State Ayush Rule 158-B Proprietary ASU drug manufacturing license."
        ]

    # Append Strategic Workaround to Conflict Matrix
    conflict_matrix = state.get("conflict_matrix", [])
    workaround_card = {
        "jurisdiction": "Strategic Regulatory Workaround",
        "status": "ACTIONABLE STRATEGY",
        "color": "gold",
        "icon": "💡",
        "reasoning": workaround
    }
    conflict_matrix_with_workaround = conflict_matrix + [workaround_card]

    latency_ms = int((time.time() - start_time) * 1000)
    trace_entry = {
        "node": "WorkaroundSynthesizerNode",
        "description": f"Generated actionable workaround roadmap with {len(roadmap)} milestones.",
        "latency_ms": max(latency_ms, 10)
    }

    return {
        "strategic_workaround": workaround,
        "filing_roadmap": roadmap,
        "conflict_matrix": conflict_matrix_with_workaround,
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
