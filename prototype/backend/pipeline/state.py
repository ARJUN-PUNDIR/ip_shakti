"""
RegulatoryGraphState definition for IP-SAKTI Sahayak
Typed State dictionary passed through all Nodes in the Multi-Agent StateGraph.
"""

from typing import TypedDict, List, Dict, Any, Optional

class RegulatoryState(TypedDict, total=False):
    # Initial Input
    query: str
    domain: str
    language: str
    scenario_id: Optional[str]

    # Node 1: Normalizer Node Outputs
    normalized_query: str
    detected_botanicals: List[Dict[str, str]]
    dosage_form: str
    target_jurisdictions: List[str]
    intent_categories: List[str]
    is_cosmetic: bool
    is_food_supplement: bool
    is_ecommerce: bool
    is_factory_setup: bool
    is_foreign_entity: bool
    vernacular_mappings: Dict[str, Any]

    # Nodes 2-5: Specialized Regulatory Agent Outputs
    ipo_evaluation: Dict[str, Any]
    nba_evaluation: Dict[str, Any]
    ayush_evaluation: Dict[str, Any]
    global_evaluation: Dict[str, Any]

    # Node 6: Cross-Regulatory Collision Detector Output
    conflict_matrix: List[Dict[str, Any]]
    detected_collisions: List[str]

    # Node 7: Strategic Workaround & Synthesis Node Output
    strategic_workaround: str
    patent_claim_recommendations: List[str]
    filing_roadmap: List[str]

    # Node 8: Cryptographic Gazette Verifier Output
    citations: List[Dict[str, Any]]
    verified_hashes: List[Dict[str, str]]
    all_grounded: bool

    # Final Combined Outputs
    title: str
    summary: str
    direct_short_summary: str
    llm_live: bool
    llm_source: str  # "nvidia_nim", "local_ollama", or "grounded_rules"
    model: str
    execution_trace: List[Dict[str, Any]]
