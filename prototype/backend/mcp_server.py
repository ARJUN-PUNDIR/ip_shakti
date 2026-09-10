"""
Model Context Protocol (MCP) Server for IP-SAKTI Sahayak.
Compliant with standard MCP JSON-RPC 2.0 specifications.
Allows external AI clients (Claude Desktop, Cursor, Antigravity, LLM agents)
to interactively query Indian Patent Office (IPO), National Biodiversity Authority (NBA),
and Ministry of Ayush regulatory engines as modular external tools.
"""

import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from pipeline.graph import regulatory_graph
from vernacular_kb import get_vernacular_entry
from legal_kb import GAZETTE_REGISTRY

# Standard MCP Tool Definitions
MCP_TOOLS = [
    {
        "name": "screen_patentability",
        "description": "Evaluates herbal/botanical formulation against Indian Patents Act Section 3(p) (Traditional Knowledge) and Section 3(e) (Synergistic Admixture). Returns statutory verdict, TKDL overlap, and formulation defensibility recommendations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "botanicals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of botanical ingredients or common/vernacular herbal names (e.g. ['Curcuma longa', 'Asgandh Nagori'])"
                },
                "dosage_form": {
                    "type": "string",
                    "description": "Dosage technology (e.g. 'Liposomal / Phospholipid Nanocarrier', 'Crude Churna', 'Aqueous Extract')"
                },
                "jurisdiction": {
                    "type": "string",
                    "default": "India",
                    "description": "Target patent jurisdiction"
                }
            },
            "required": ["botanicals"]
        }
    },
    {
        "name": "check_nba_clearance",
        "description": "Determines Biological Diversity Act, 2002 compliance. Evaluates Section 6 mandatory Form 3 prior approval for IPR filings, Section 3 foreign entity restrictions, Section 40 Normally Traded Commodities (NTCO) exemptions, and Section 55 criminal liabilities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "biological_resources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of biological resources accessed in India"
                },
                "applicant_type": {
                    "type": "string",
                    "enum": ["Indian Citizen / Company", "Foreign National / Non-Resident Indian", "Body Corporate with Foreign Equity"],
                    "default": "Indian Citizen / Company",
                    "description": "Entity classification for Section 3 vs Section 7 determination"
                },
                "applying_for_ipr": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether an intellectual property right (patent) is being sought"
                }
            },
            "required": ["biological_resources"]
        }
    },
    {
        "name": "get_ayush_licensing",
        "description": "Evaluates commercial manufacturing and marketing compliance under Chapter IV-A of Drugs & Cosmetics Rules, 1945. Differentiates Classical ASU medicines from Proprietary Patent Formulations under Rule 158-B and Schedule T GMP requirements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["Classical ASU Medicine (Authoritative Treatise)", "Ayurvedic Proprietary Medicine (Patent / Novel Formulation)"],
                    "default": "Ayurvedic Proprietary Medicine (Patent / Novel Formulation)"
                },
                "ingredients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Ingredients list"
                },
                "dosage_form": {
                    "type": "string",
                    "description": "Dosage form (e.g. Cream, Tablet, Syrup)"
                }
            },
            "required": ["category", "ingredients"]
        }
    },
    {
        "name": "calculate_abs_royalty",
        "description": "Calculates mandatory Access and Benefit Sharing (ABS) financial royalty obligations to the National Biodiversity Authority (NBA) and State Biodiversity Boards (SBB) under NBA ABS Regulations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "annual_gross_ex_factory_sale_inr": {
                    "type": "number",
                    "description": "Annual gross ex-factory sale in INR (e.g. 5000000 for 50 Lakhs)"
                },
                "raw_material_purchase_cost_inr": {
                    "type": "number",
                    "description": "Annual purchase cost of biological resources from local farmers/traders in INR"
                },
                "option_chosen": {
                    "type": "string",
                    "enum": ["Percentage of Gross Ex-Factory Sale (0.1% to 0.5%)", "Percentage of Purchase Price (3.0% to 5.0%)"],
                    "default": "Percentage of Gross Ex-Factory Sale (0.1% to 0.5%)"
                }
            },
            "required": ["annual_gross_ex_factory_sale_inr"]
        }
    },
    {
        "name": "resolve_vernacular_botanical",
        "description": "Resolves regional colloquial, Unani Hakim, Siddha Vaidyar, or folk herbal dialect terms into canonical Latin binomials, PCIM&H pharmacopoeial monographs (API/UPI/SPI), and CSIR-TKDL classification codes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vernacular_term": {
                    "type": "string",
                    "description": "Regional spoken term (e.g. 'Asgandh Nagori', 'Filfil Siyah', 'Amukkara', 'Nilavembu', 'Hadjod')"
                }
            },
            "required": ["vernacular_term"]
        }
    },
    {
        "name": "get_gazette_citation",
        "description": "Fetches authentic Government of India statutory gazette text, notification metadata, official government portal hyperlink, and cryptographic SHA-256 integrity hash for an atomic legal clause.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "enum": ["patent_act_3p", "patent_act_3e", "nba_section_6", "dnc_rule_158b", "eu_thmpd_2004_24_ec"],
                    "description": "Statutory identifier of the gazette document"
                }
            },
            "required": ["doc_id"]
        }
    }
]

# Tool Handlers Execution
def handle_screen_patentability(args: Dict[str, Any]) -> Dict[str, Any]:
    botanicals = args.get("botanicals", [])
    dosage_form = args.get("dosage_form", "Standardized Extract")
    query = f"Patentability analysis for {', '.join(botanicals)} in {dosage_form} dosage form."
    
    state = regulatory_graph.invoke(query, domain="Ayurveda")
    ipo_eval = state.get("ipo_evaluation", {})
    return {
        "verdict": ipo_eval.get("status", "Screening Complete"),
        "reasoning": ipo_eval.get("reasoning", ""),
        "section_3p_barred": "Barred" in ipo_eval.get("status", ""),
        "section_3e_synergy_required": "3(e)" in ipo_eval.get("reasoning", "") or len(botanicals) > 1,
        "recommended_workaround": state.get("strategic_workaround", ""),
        "formulation_score": 88 if "Nano" in dosage_form or "Liposom" in dosage_form else 35
    }

def handle_check_nba_clearance(args: Dict[str, Any]) -> Dict[str, Any]:
    resources = args.get("biological_resources", [])
    applicant_type = args.get("applicant_type", "Indian Citizen / Company")
    is_ipr = args.get("applying_for_ipr", True)

    query = f"NBA clearance for {', '.join(resources)} by {applicant_type} for IPR patent filing."
    state = regulatory_graph.invoke(query, domain="Ayurveda")
    nba_eval = state.get("nba_evaluation", {})

    return {
        "status": nba_eval.get("status", "Form 3 Approval Required"),
        "statutory_mandate": "Section 6(1) of Biological Diversity Act, 2002 mandates prior approval from NBA before grant of patent.",
        "applicable_form": "Form III (Rule 18) for IPR applications; Form I (Rule 14) for commercial utilization by foreign entities.",
        "criminal_liability": "Section 55: Imprisonment up to 5 years or fine up to INR 10 Lakhs, or both, for contravention of Section 6.",
        "exemption_check": "Non-commercial Indian entities are exempt from Section 7 intimation, but ALL entities require Section 6 prior approval before patent grant."
    }

def handle_get_ayush_licensing(args: Dict[str, Any]) -> Dict[str, Any]:
    cat = args.get("category", "")
    ingredients = args.get("ingredients", [])
    is_classical = "Classical" in cat

    if is_classical:
        return {
            "license_type": "Classical ASU Formulation (Authoritative Treatise)",
            "statutory_rule": "Drugs & Cosmetics Rules, 1945 Rule 158-B(I)",
            "safety_efficacy_dossier": "Exempt from clinical trials if exact formulation matches 54 First Schedule books (e.g. Charaka Samhita, API)",
            "facility_requirement": "Schedule T Good Manufacturing Practices (minimum 1,200 sq. ft. dedicated manufacturing area)",
            "application_form": "Form 24-D for Manufacturing License; Form 24-E for Loan License"
        }
    else:
        return {
            "license_type": "Ayurvedic Proprietary Medicine (Novel Composition)",
            "statutory_rule": "Drugs & Cosmetics Rules, 1945 Rule 158-B(II)",
            "safety_efficacy_dossier": "Mandatory submission of published scientific safety literature or Phase III clinical trial data",
            "facility_requirement": "Schedule T GMP certified facility with QC Lab testing active botanical markers",
            "application_form": "Form 24-D with Rule 158-B technical dossier to State Ayush Licensing Authority (SALA)"
        }

def handle_calculate_abs_royalty(args: Dict[str, Any]) -> Dict[str, Any]:
    sale = float(args.get("annual_gross_ex_factory_sale_inr", 0))
    purchase_cost = float(args.get("raw_material_purchase_cost_inr", sale * 0.15))
    option = args.get("option_chosen", "Percentage of Gross Ex-Factory Sale (0.1% to 0.5%)")

    if sale <= 10000000:
        sale_rate = 0.001
        rate_label = "0.1% (Slab: Turnover Up to INR 1 Crore)"
    elif sale <= 30000000:
        sale_rate = 0.002
        rate_label = "0.2% (Slab: Turnover INR 1 to 3 Crores)"
    else:
        sale_rate = 0.005
        rate_label = "0.5% (Slab: Turnover Above INR 3 Crores)"

    abs_on_sale = round(sale * sale_rate, 2)
    abs_on_purchase = round(purchase_cost * 0.04, 2)

    return {
        "annual_gross_sale_inr": sale,
        "raw_material_cost_inr": purchase_cost,
        "calculation_basis": option,
        "calculated_abs_royalty_inr": abs_on_sale if "Sale" in option else abs_on_purchase,
        "applied_rate": rate_label if "Sale" in option else "4.0% of Raw Material Purchase Cost",
        "beneficiary": "National Biodiversity Authority (NBA) for distribution to local Biodiversity Management Committees (BMCs) and cultivators.",
        "statutory_framework": "Guidelines on Access to Biological Resources and Associated Knowledge and Benefits Sharing Regulations, 2014"
    }

def handle_resolve_vernacular_botanical(args: Dict[str, Any]) -> Dict[str, Any]:
    term = args.get("vernacular_term", "").strip()
    norm = get_vernacular_entry(term)
    if norm:
        return {
            "status": "matched",
            "spoken_term": term,
            "canonical_name": norm["canonical_name"],
            "latin_binomial": norm["latin_name"],
            "botanical_family": norm["family"],
            "traditional_system": norm["system"],
            "pharmacopoeia_monograph": norm["pharmacopoeia_ref"],
            "tkdl_classification_code": norm["tkrc_code"],
            "active_chemical_marker": norm["active_marker"]
        }
    return {
        "status": "unmatched",
        "spoken_term": term,
        "message": "Term not found in current PCIM&H / NMPB dictionary. Please provide standard English/Latin name."
    }

def handle_get_gazette_citation(args: Dict[str, Any]) -> Dict[str, Any]:
    doc_id = args.get("doc_id", "")
    if doc_id in GAZETTE_REGISTRY:
        doc = GAZETTE_REGISTRY[doc_id]
        return {
            "doc_id": doc_id,
            "title": doc.get("title", ""),
            "chapter_section": f"{doc.get('chapter', '')} • {doc.get('section', '')} {doc.get('clause', '')}",
            "authority": doc.get("authority", ""),
            "gazette_date": doc.get("gazette_date", ""),
            "official_url": doc.get("official_url", ""),
            "portal_name": doc.get("portal_name", "Official Gazette Portal"),
            "sha256": doc.get("sha256", ""),
            "verbatim_text": doc.get("verbatim_text", "")
        }
    return {"error": f"Doc ID '{doc_id}' not found in Gazette Registry"}

TOOL_DISPATCHER = {
    "screen_patentability": handle_screen_patentability,
    "check_nba_clearance": handle_check_nba_clearance,
    "get_ayush_licensing": handle_get_ayush_licensing,
    "calculate_abs_royalty": handle_calculate_abs_royalty,
    "resolve_vernacular_botanical": handle_resolve_vernacular_botanical,
    "get_gazette_citation": handle_get_gazette_citation
}

def list_tools() -> List[Dict[str, Any]]:
    return MCP_TOOLS

def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    handler = TOOL_DISPATCHER.get(name)
    if not handler:
        raise ValueError(f"Unknown MCP tool: {name}")
    return handler(arguments)

# Standard MCP JSON-RPC 2.0 Stdio Loop
async def run_stdio_mcp_server():
    """Runs a standard JSON-RPC 2.0 stdio loop for Claude Desktop / Cursor / Antigravity integration."""
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    while True:
        line = await reader.readline()
        if not line:
            break
        raw_msg = line.decode("utf-8").strip()
        if not raw_msg:
            continue
        try:
            req = json.loads(raw_msg)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "ip-sakti-sahayak-mcp",
                            "version": "2.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": list_tools()}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                tool_result = execute_tool(tool_name, tool_args)
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(tool_result, indent=2)
                            }
                        ]
                    }
                }
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            out_bytes = (json.dumps(res) + "\n").encode("utf-8")
            sys.stdout.buffer.write(out_bytes)
            sys.stdout.buffer.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": req_id if 'req_id' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.buffer.write((json.dumps(err_res) + "\n").encode("utf-8"))
            sys.stdout.buffer.flush()

if __name__ == "__main__":
    asyncio.run(run_stdio_mcp_server())
