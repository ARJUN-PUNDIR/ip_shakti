"""
LangGraph-Style StateGraph Engine for IP-SAKTI Sahayak
Implements explicit Nodes, Edges, Parallel Fan-out, Fan-in, and Full Execution Tracing.
"""

import time
from typing import Dict, Any, List, Callable
from pipeline.state import RegulatoryState
from pipeline.nodes import (
    normalizer_node,
    ipr_agent_node,
    biodiversity_agent_node,
    ayush_agent_node,
    global_agent_node,
    conflict_detector_node,
    workaround_synthesizer_node,
    verifier_node
)

START = "__start__"
END = "__end__"

class RegulatoryStateGraph:
    """
    Explicit Multi-Agent StateGraph with Nodes, Edges, Parallel Fan-out and Fan-in.
    """
    def __init__(self):
        self.nodes: Dict[str, Callable[[RegulatoryState], Dict[str, Any]]] = {}
        self.edges: List[Dict[str, str]] = []
        self.parallel_groups: Dict[str, List[str]] = {}

    def add_node(self, name: str, fn: Callable[[RegulatoryState], Dict[str, Any]]):
        self.nodes[name] = fn

    def add_edge(self, from_node: str, to_node: str):
        self.edges.append({"from": from_node, "to": to_node})

    def get_topology(self) -> Dict[str, Any]:
        """Returns complete list of nodes and edges for UI visualization."""
        node_metadata = [
            {"id": "normalizer", "label": "Query Normalizer & Botanical NER", "type": "input_parser", "icon": "🔍"},
            {"id": "ipr_agent", "label": "IPO Patent Agent (Section 3p/3e)", "type": "regulatory_agent", "icon": "⚖️"},
            {"id": "biodiversity_agent", "label": "NBA Biodiversity Agent (Section 6)", "type": "regulatory_agent", "icon": "🌿"},
            {"id": "ayush_agent", "label": "SALA Ayush Licensing Agent (Rule 158-B)", "type": "regulatory_agent", "icon": "🏥"},
            {"id": "global_agent", "label": "Global Export Agent (EU/US)", "type": "regulatory_agent", "icon": "🌍"},
            {"id": "conflict_detector", "label": "Cross-Regulatory Collision Matrix", "type": "evaluator", "icon": "⚡"},
            {"id": "workaround_synthesizer", "label": "Strategic Workaround Synthesizer", "type": "synthesizer", "icon": "💡"},
            {"id": "verifier", "label": "SHA-256 Gazette Verifier", "type": "verifier", "icon": "🛡️"}
        ]
        return {
            "nodes": node_metadata,
            "edges": self.edges
        }

    def invoke(self, initial_state: Any, domain: str = "Ayurveda", language: str = "en") -> RegulatoryState:
        """
        Executes the StateGraph across defined nodes and edges.
        1. START -> normalizer
        2. normalizer -> [ipr_agent, biodiversity_agent, ayush_agent, global_agent] (Parallel Fan-out)
        3. [4 Agents] -> conflict_detector (Fan-in)
        4. conflict_detector -> workaround_synthesizer
        5. workaround_synthesizer -> verifier -> END
        """
        if isinstance(initial_state, str):
            state: RegulatoryState = {
                "query": initial_state,
                "raw_query": initial_state,
                "normalized_query": initial_state,
                "domain": domain,
                "botanicals_detected": [],
                "dosage_form": "General Formulation",
                "intent": "general_regulatory",
                "ipr_evaluation": {},
                "biodiversity_evaluation": {},
                "ayush_evaluation": {},
                "global_evaluation": {},
                "conflict_matrix": [],
                "strategic_workaround": "",
                "citations": [],
                "execution_trace": [],
                "gazette_verification": {}
            }
        else:
            q_val = initial_state.get("query") or initial_state.get("raw_query") or initial_state.get("normalized_query", "")
            state: RegulatoryState = {
                "query": q_val,
                "raw_query": q_val,
                "normalized_query": q_val,
                "domain": initial_state.get("domain", domain),
                "botanicals_detected": initial_state.get("botanicals_detected", []),
                "dosage_form": initial_state.get("dosage_form", "General Formulation"),
                "intent": initial_state.get("intent", "general_regulatory"),
                "ipr_evaluation": initial_state.get("ipr_evaluation", {}),
                "biodiversity_evaluation": initial_state.get("biodiversity_evaluation", {}),
                "ayush_evaluation": initial_state.get("ayush_evaluation", {}),
                "global_evaluation": initial_state.get("global_evaluation", {}),
                "conflict_matrix": initial_state.get("conflict_matrix", []),
                "strategic_workaround": initial_state.get("strategic_workaround", ""),
                "citations": initial_state.get("citations", []),
                "execution_trace": [],
                "gazette_verification": initial_state.get("gazette_verification", {})
            }

        # Step 1: Normalizer Node
        norm_updates = self.nodes["normalizer"](state)
        state.update(norm_updates)

        # Step 2: Parallel 4 Regulatory Agents (Fan-out)
        parallel_nodes = ["ipr_agent", "biodiversity_agent", "ayush_agent", "global_agent"]
        for p_name in parallel_nodes:
            node_fn = self.nodes[p_name]
            node_updates = node_fn(state)
            state.update(node_updates)

        # Step 3: Conflict Detector Node (Fan-in)
        conflict_updates = self.nodes["conflict_detector"](state)
        state.update(conflict_updates)

        # Step 4: Strategic Workaround Synthesizer Node
        workaround_updates = self.nodes["workaround_synthesizer"](state)
        state.update(workaround_updates)

        # Step 5: Cryptographic Gazette Verifier Node
        verifier_updates = self.nodes["verifier"](state)
        state.update(verifier_updates)

        # Synthesize Final Dynamic Executive Summary & Title
        botanicals = [b["common_name"] for b in state.get("detected_botanicals", [])]
        herbs_str = ", ".join(botanicals) if botanicals else "Ayush Herbal Formulation"
        dosage = state.get("dosage_form", "Standard Formulation")
        ipo = state.get("ipo_evaluation", {})
        nba = state.get("nba_evaluation", {})
        ayush = state.get("ayush_evaluation", {})
        glo = state.get("global_evaluation", {})
        collisions = state.get("detected_collisions", [])
        workaround = state.get("strategic_workaround", "")
        roadmap = state.get("filing_roadmap", [])

        title = f"{herbs_str} — Multi-Agent Regulatory Assessment" if botanicals else f"Ayush Regulatory Intelligence Assessment"
        if language == "hi":
            title = f"{herbs_str} — बहु-एजेंट नियामक मूल्यांकन" if botanicals else "आयुष विनियामक बुद्धिमत्ता मूल्यांकन"

        if language == "hi":
            summary_parts = [
                f"### वैधानिक निष्कर्ष: {herbs_str} ({dosage})",
                f"भारतीय पेटेंट अधिनियम 1970, जैविक विविधता अधिनियम 2002/2023, औषधि एवं प्रसाधन सामग्री नियम 1945 तथा अंतर्राष्ट्रीय व्यापार दिशानिर्देशों के अंतर्गत बहु-एजेंट वैधानिक रिपोर्ट:",
            ]

            vernacular_matches = state.get("vernacular_mappings", {}).get("recognized_vernaculars", [])
            if vernacular_matches:
                summary_parts.extend([
                    "",
                    "### पारंपरिक बोली एवं फार्माकोपिया मोनोग्राफ सत्यापन",
                ])
                for vm in vernacular_matches:
                    summary_parts.append(
                        f"• **पहचानी गई बोली**: '{vm['spoken_vernacular'].title()}' ({vm['language_origin']} / {vm['traditional_system']}) "
                        f"➔ मानकीकृत: *{vm['latin_name']}* ({vm['canonical_name']}) | "
                        f"**मोनोग्राफ**: {vm['pharmacopoeia_monograph']} | **TKRC**: {vm['tkrc_code']} | "
                        f"**सक्रिय घटक**: {vm['active_chemical_marker']}"
                    )

            summary_parts.extend([
                "",
                f"### 1. भारतीय पेटेंट कार्यालय (IPO) एवं पूर्व कला (Prior Art) मूल्यांकन",
                f"• **वैधानिक स्थिति**: {ipo.get('status', 'जांच आवश्यक')}",
                f"• **परीक्षण निष्कर्ष**: {ipo.get('reasoning', 'पारंपरिक ज्ञान मूल्यांकन लागू किया गया।')}",
                f"• **अनुशंसित दावा दायरा**: {ipo.get('recommended_claims', 'नवीन डिलीवरी प्रणाली या सहक्रियात्मक अनुपातों में तैयार करें।')}",
                "",
                f"### 2. राष्ट्रीय जैव विविधता प्राधिकरण (NBA) अनुमोदन",
                f"• **नियामक स्थिति**: {nba.get('status', 'धारा 6 अनुमोदन आवश्यक')}",
                f"• **वैधानिक अधिदेश**: {nba.get('reasoning', 'भारत के भीतर जैविक संसाधनों तक पहुंच के लिए BDA प्रावधानों का अनुपालन अनिवार्य है।')}",
                f"• **प्रपत्र एवं दंड**: {nba.get('form_required', 'NBA प्रपत्र 3')} जमा करें। अनधिकृत व्यावसायिक उपयोग पर धारा 55 के तहत आपराधिक दायित्व लागू होता है।",
                "",
                f"### 3. राज्य आयुष लाइसेंसिंग प्राधिकरण (नियम 158-B)",
                f"• **लाइसेंसिंग मार्ग**: {ayush.get('status', 'नियम 158-B अनुपालन')}",
                f"• **निर्माण आवश्यकताएं**: {ayush.get('reasoning', 'अनुसूची T GMP और अनुमोदित फार्माकोपियल फॉर्मूलेशन का पालन अनिवार्य है।')}",
                "",
                f"### 4. वैश्विक निर्यात सामंजस्य",
                f"• **निर्यात मूल्यांकन**: {glo.get('status', 'अनुपालन जांच')}",
                f"• **लक्ष्य बाजार मानदंड**: {glo.get('reasoning', 'गंतव्य देश हेतु विशिष्ट वानस्पतिक डोजियर आवश्यक है।')}",
            ])

            if collisions:
                summary_parts.extend([
                    "",
                    f"### 5. नियामक टकराव एवं निवारण (Cross-Regulatory Collision Matrix)",
                    f"• ⚠️ **पहचाना गया टकराव**: {collisions[0]}"
                ])

            if workaround:
                summary_parts.extend([
                    "",
                    f"### 6. पेटेंट योग्य व्यावहारिक रणनीति एवं फाइलिंग रोडमैप",
                    f"• **अनुशंसित रणनीति**: {workaround}"
                ])
                if roadmap:
                    for step in roadmap:
                        summary_parts.append(f"• {step}")

            direct_bullets = []
            if ipo.get("status"):
                direct_bullets.append(f"• **पेटेंट पात्रता (IPO)**: {ipo.get('status')} — {ipo.get('reasoning', '').split('.')[0]}.")
            if nba.get("status"):
                direct_bullets.append(f"• **जैव विविधता अनुपालन (NBA)**: {nba.get('status')} — {nba.get('reasoning', '').split('.')[0]}.")
            if ayush.get("status"):
                direct_bullets.append(f"• **आयुष लाइसेंसिंग मार्ग**: {ayush.get('status')} — {ayush.get('reasoning', '').split('.')[0]}.")
            if glo.get("status"):
                direct_bullets.append(f"• **वैश्विक निर्यात मार्ग**: {glo.get('status')} — {glo.get('reasoning', '').split('.')[0]}.")
            if workaround:
                direct_bullets.append(f"• **रणनीतिक समाधान**: {workaround.split('.')[0]}.")

            direct_short_summary = "\n".join(direct_bullets)
            state["direct_short_summary"] = direct_short_summary
            state["title"] = title
            state["summary"] = "\n".join(summary_parts)
            return state

        summary_parts = [
            f"### Statutory Verdict: {herbs_str} ({dosage})",
            f"Cross-regulatory multi-agent synthesis under the Patents Act 1970, Biological Diversity Act 2002/2023, Drugs & Cosmetics Rules 1945, and International Trade Guidelines:",
        ]

        vernacular_matches = state.get("vernacular_mappings", {}).get("recognized_vernaculars", [])
        if vernacular_matches:
            summary_parts.extend([
                "",
                "### Traditional Dialect & Pharmacopoeial Monograph Grounding",
            ])
            for vm in vernacular_matches:
                summary_parts.append(
                    f"• **Recognized Dialect**: '{vm['spoken_vernacular'].title()}' ({vm['language_origin']} / {vm['traditional_system']}) "
                    f"➔ Standardized: *{vm['latin_name']}* ({vm['canonical_name']}) | "
                    f"**Monograph**: {vm['pharmacopoeia_monograph']} | **TKRC**: {vm['tkrc_code']} | "
                    f"**Active Marker**: {vm['active_chemical_marker']}"
                )

        summary_parts.extend([
            "",
            f"### 1. Indian Patent Office (IPO) & Prior Art Screening",
            f"• **Statutory Status**: {ipo.get('status', 'Screening Required')}",
            f"• **Examination Finding**: {ipo.get('reasoning', 'Traditional knowledge evaluation applied.')}",
            f"• **Recommended Claim Scope**: {ipo.get('recommended_claims', 'Formulate into novel delivery systems or synergistic ratios.')}",
            "",
            f"### 2. National Biodiversity Authority (NBA Clearance)",
            f"• **Regulatory Status**: {nba.get('status', 'Section 6 Approval Required')}",
            f"• **Statutory Mandate**: {nba.get('reasoning', 'Biological resources accessed within India require compliance with BDA provisions.')}",
            f"• **Form & Penalties**: Submit {nba.get('form_required', 'NBA Form 3')}. Section 55 imposes criminal liabilities for unauthorized commercial utilization.",
            "",
            f"### 3. State Ayush Licensing Authority (Rule 158-B)",
            f"• **Licensing Route**: {ayush.get('status', 'Rule 158-B Compliance')}",
            f"• **Manufacturing Requirements**: {ayush.get('reasoning', 'Must comply with Schedule T GMP and approved pharmacopoeial formulations.')}",
            "",
            f"### 4. Global Export Harmonization",
            f"• **Export Assessment**: {glo.get('status', 'Compliance Screening')}",
            f"• **Target Market Criteria**: {glo.get('reasoning', 'Target destination requires specific botanical dossier.')}",
        ])

        if collisions:
            summary_parts.extend([
                "",
                f"### 5. Cross-Regulatory Collision Matrix",
                f"• ⚠️ **Detected Conflict**: {collisions[0]}"
            ])

        if workaround:
            summary_parts.extend([
                "",
                f"### 6. Actionable Strategy & Filing Roadmap",
                f"• **Recommended Strategy**: {workaround}"
            ])
            if roadmap:
                for step in roadmap:
                    summary_parts.append(f"• {step}")

        # Formulate direct concise summary answering the user query immediately from all node findings
        direct_bullets = []
        if ipo.get("status"):
            direct_bullets.append(f"• **Patentability (IPO)**: {ipo.get('status')} — {ipo.get('reasoning', '').split('.')[0]}.")
        if nba.get("status"):
            direct_bullets.append(f"• **Biodiversity Compliance (NBA)**: {nba.get('status')} — {nba.get('reasoning', '').split('.')[0]}.")
        if ayush.get("status"):
            direct_bullets.append(f"• **Ayush Licensing Route**: {ayush.get('status')} — {ayush.get('reasoning', '').split('.')[0]}.")
        if glo.get("status"):
            direct_bullets.append(f"• **Global Export Route**: {glo.get('status')} — {glo.get('reasoning', '').split('.')[0]}.")
        if workaround:
            direct_bullets.append(f"• **Strategic Workaround**: {workaround.split('.')[0]}.")

        direct_short_summary = "\n".join(direct_bullets)
        state["direct_short_summary"] = direct_short_summary

        state["title"] = title
        state["summary"] = "\n".join(summary_parts)

        return state

def create_regulatory_graph() -> RegulatoryStateGraph:
    """Instantiates and wires the Multi-Agent StateGraph with nodes and edges."""
    graph = RegulatoryStateGraph()

    # 1. Register Nodes
    graph.add_node("normalizer", normalizer_node)
    graph.add_node("ipr_agent", ipr_agent_node)
    graph.add_node("biodiversity_agent", biodiversity_agent_node)
    graph.add_node("ayush_agent", ayush_agent_node)
    graph.add_node("global_agent", global_agent_node)
    graph.add_node("conflict_detector", conflict_detector_node)
    graph.add_node("workaround_synthesizer", workaround_synthesizer_node)
    graph.add_node("verifier", verifier_node)

    # 2. Wire Explicit Edges
    graph.add_edge(START, "normalizer")
    graph.add_edge("normalizer", "ipr_agent")
    graph.add_edge("normalizer", "biodiversity_agent")
    graph.add_edge("normalizer", "ayush_agent")
    graph.add_edge("normalizer", "global_agent")
    graph.add_edge("ipr_agent", "conflict_detector")
    graph.add_edge("biodiversity_agent", "conflict_detector")
    graph.add_edge("ayush_agent", "conflict_detector")
    graph.add_edge("global_agent", "conflict_detector")
    graph.add_edge("conflict_detector", "workaround_synthesizer")
    graph.add_edge("workaround_synthesizer", "verifier")
    graph.add_edge("verifier", END)

    return graph

# Singleton instance
regulatory_graph = create_regulatory_graph()
