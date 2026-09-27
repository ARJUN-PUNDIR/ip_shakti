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
    allied_agent_node,
    wipo_gratk_agent_node,
    cbd_nagoya_agent_node,
    eu_thmpd_agent_node,
    us_fda_agent_node,
    conflict_detector_node,
    workaround_synthesizer_node,
    verifier_node
)

try:
    from langsmith import traceable
except ImportError:
    def traceable(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

START = "__start__"
END = "__end__"

class RegulatoryStateGraph:
    """
    Explicit Multi-Agent StateGraph with Nodes, Edges, Parallel Fan-out and Fan-in.
    Supports Dual Jurisdictions: National (India) vs International (Global Treaties & Markets).
    """
    def __init__(self):
        self.nodes: Dict[str, Callable[[RegulatoryState], Dict[str, Any]]] = {}
        self.edges: List[Dict[str, str]] = []
        self.parallel_groups: Dict[str, List[str]] = {}

    def add_node(self, name: str, fn: Callable[[RegulatoryState], Dict[str, Any]]):
        self.nodes[name] = fn

    def add_edge(self, from_node: str, to_node: str):
        self.edges.append({"from": from_node, "to": to_node})

    def get_topology(self, jurisdiction: str = "india") -> Dict[str, Any]:
        """Returns complete list of nodes and edges for UI visualization based on active jurisdiction."""
        is_intl = jurisdiction.lower() == "international"
        
        if is_intl:
            node_metadata = [
                {"id": "normalizer", "label": "Query Normalizer & Botanical NER", "type": "input_parser", "icon": "🔍"},
                {"id": "wipo_gratk_agent", "label": "WIPO & GRATK Treaty 2024 Agent", "type": "regulatory_agent", "icon": "🌐"},
                {"id": "cbd_nagoya_agent", "label": "CBD & Nagoya ABS Agent (Budapest)", "type": "regulatory_agent", "icon": "🌿"},
                {"id": "eu_thmpd_agent", "label": "EU EMA & THMPD Agent (Directive 2004/24/EC)", "type": "regulatory_agent", "icon": "🇪🇺"},
                {"id": "us_fda_agent", "label": "US FDA & Global Regulators (DSHEA/Botanicals)", "type": "regulatory_agent", "icon": "🇺🇸"},
                {"id": "conflict_detector", "label": "International Collision Matrix", "type": "evaluator", "icon": "⚡"},
                {"id": "workaround_synthesizer", "label": "Strategic Workaround Synthesizer", "type": "synthesizer", "icon": "💡"},
                {"id": "verifier", "label": "SHA-256 Gazette Verifier", "type": "verifier", "icon": "🛡️"}
            ]
            active_edges = [
                {"from": START, "to": "normalizer"},
                {"from": "normalizer", "to": "wipo_gratk_agent"},
                {"from": "normalizer", "to": "cbd_nagoya_agent"},
                {"from": "normalizer", "to": "eu_thmpd_agent"},
                {"from": "normalizer", "to": "us_fda_agent"},
                {"from": "wipo_gratk_agent", "to": "conflict_detector"},
                {"from": "cbd_nagoya_agent", "to": "conflict_detector"},
                {"from": "eu_thmpd_agent", "to": "conflict_detector"},
                {"from": "us_fda_agent", "to": "conflict_detector"},
                {"from": "conflict_detector", "to": "workaround_synthesizer"},
                {"from": "workaround_synthesizer", "to": "verifier"},
                {"from": "verifier", "to": END}
            ]
        else:
            node_metadata = [
                {"id": "normalizer", "label": "Query Normalizer & Botanical NER", "type": "input_parser", "icon": "🔍"},
                {"id": "ipr_agent", "label": "IPO Patent Agent (Section 3p/3e)", "type": "regulatory_agent", "icon": "⚖️"},
                {"id": "biodiversity_agent", "label": "NBA Biodiversity Agent (Section 6)", "type": "regulatory_agent", "icon": "🌿"},
                {"id": "ayush_agent", "label": "SALA Ayush Licensing Agent (Rule 158-B)", "type": "regulatory_agent", "icon": "🏥"},
                {"id": "allied_agent", "label": "Allied Regimes Agent (FSSAI / DMROA 1954 / GI)", "type": "regulatory_agent", "icon": "🏷️"},
                {"id": "conflict_detector", "label": "Cross-Regulatory Collision Matrix", "type": "evaluator", "icon": "⚡"},
                {"id": "workaround_synthesizer", "label": "Strategic Workaround Synthesizer", "type": "synthesizer", "icon": "💡"},
                {"id": "verifier", "label": "SHA-256 Gazette Verifier", "type": "verifier", "icon": "🛡️"}
            ]
            active_edges = [
                {"from": START, "to": "normalizer"},
                {"from": "normalizer", "to": "ipr_agent"},
                {"from": "normalizer", "to": "biodiversity_agent"},
                {"from": "normalizer", "to": "ayush_agent"},
                {"from": "normalizer", "to": "allied_agent"},
                {"from": "ipr_agent", "to": "conflict_detector"},
                {"from": "biodiversity_agent", "to": "conflict_detector"},
                {"from": "ayush_agent", "to": "conflict_detector"},
                {"from": "allied_agent", "to": "conflict_detector"},
                {"from": "conflict_detector", "to": "workaround_synthesizer"},
                {"from": "workaround_synthesizer", "to": "verifier"},
                {"from": "verifier", "to": END}
            ]
            
        return {
            "nodes": node_metadata,
            "edges": active_edges
        }

    @traceable(name="IP_SAKTI_StateGraph_Pipeline", run_type="chain")
    def invoke(self, initial_state: Any, domain: str = "Ayurveda", language: str = "en", jurisdiction: str = "india") -> RegulatoryState:
        """
        Executes the StateGraph across defined nodes and edges based on jurisdiction.
        India Mode:
          normalizer -> [ipr_agent, biodiversity_agent, ayush_agent, allied_agent] -> conflict_detector -> workaround_synthesizer -> verifier
        International Mode:
          normalizer -> [wipo_gratk_agent, cbd_nagoya_agent, eu_thmpd_agent, us_fda_agent] -> conflict_detector -> workaround_synthesizer -> verifier
        """
        try:
            from nemotron_client import sync_langsmith_config
            sync_langsmith_config()
        except Exception:
            pass

        if isinstance(initial_state, str):
            state: RegulatoryState = {
                "query": initial_state,
                "raw_query": initial_state,
                "normalized_query": initial_state,
                "domain": domain,
                "jurisdiction": jurisdiction.lower(),
                "botanicals_detected": [],
                "dosage_form": "General Formulation",
                "intent": "general_regulatory",
                "ipr_evaluation": {},
                "biodiversity_evaluation": {},
                "ayush_evaluation": {},
                "global_evaluation": {},
                "allied_evaluation": {},
                "wipo_evaluation": {},
                "cbd_evaluation": {},
                "eu_evaluation": {},
                "us_evaluation": {},
                "conflict_matrix": [],
                "strategic_workaround": "",
                "citations": [],
                "execution_trace": [],
                "gazette_verification": {}
            }
        else:
            q_val = initial_state.get("query") or initial_state.get("raw_query") or initial_state.get("normalized_query", "")
            chosen_jurisdiction = initial_state.get("jurisdiction", jurisdiction).lower()
            state: RegulatoryState = {
                "query": q_val,
                "raw_query": q_val,
                "normalized_query": q_val,
                "domain": initial_state.get("domain", domain),
                "jurisdiction": chosen_jurisdiction,
                "botanicals_detected": initial_state.get("botanicals_detected", []),
                "dosage_form": initial_state.get("dosage_form", "General Formulation"),
                "intent": initial_state.get("intent", "general_regulatory"),
                "ipr_evaluation": initial_state.get("ipr_evaluation", {}),
                "biodiversity_evaluation": initial_state.get("biodiversity_evaluation", {}),
                "ayush_evaluation": initial_state.get("ayush_evaluation", {}),
                "global_evaluation": initial_state.get("global_evaluation", {}),
                "allied_evaluation": initial_state.get("allied_evaluation", {}),
                "wipo_evaluation": initial_state.get("wipo_evaluation", {}),
                "cbd_evaluation": initial_state.get("cbd_evaluation", {}),
                "eu_evaluation": initial_state.get("eu_evaluation", {}),
                "us_evaluation": initial_state.get("us_evaluation", {}),
                "conflict_matrix": initial_state.get("conflict_matrix", []),
                "strategic_workaround": initial_state.get("strategic_workaround", ""),
                "citations": initial_state.get("citations", []),
                "execution_trace": [],
                "gazette_verification": initial_state.get("gazette_verification", {})
            }

        active_jurisdiction = state.get("jurisdiction", "india")

        # Step 1: Normalizer Node
        norm_updates = self.nodes["normalizer"](state)
        state.update(norm_updates)

        # Step 2: Parallel 4 Regulatory Agents (Fan-out) conditioned on Jurisdiction
        if active_jurisdiction == "international":
            parallel_nodes = ["wipo_gratk_agent", "cbd_nagoya_agent", "eu_thmpd_agent", "us_fda_agent"]
        else:
            # India Mode (replaces global agent with Allied Regimes: FSSAI, DMROA 1954, Cosmetics, GI)
            parallel_nodes = ["ipr_agent", "biodiversity_agent", "ayush_agent", "allied_agent"]

        for p_name in parallel_nodes:
            if p_name in self.nodes:
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
        collisions = state.get("detected_collisions", [])
        workaround = state.get("strategic_workaround", "")
        roadmap = state.get("filing_roadmap", [])

        if active_jurisdiction == "international":
            wipo = state.get("wipo_evaluation", {})
            cbd = state.get("cbd_evaluation", {})
            eu = state.get("eu_evaluation", {})
            us = state.get("us_evaluation", {})

            if language == "hi":
                title = f"{herbs_str} — अंतर्राष्ट्रीय बौद्धिक संपदा एवं संधि विश्लेषण" if botanicals else "अंतर्राष्ट्रीय संधि एवं वैश्विक बाजार विश्लेषण"
                summary_parts = [
                    f"### अंतर्राष्ट्रीय वैधानिक निष्कर्ष: {herbs_str} ({dosage})",
                    f"WIPO GRATK संधि 2024, सीबीडी नगोया प्रोटोकॉल ABS, बुडापेस्ट संधि, ईयू हर्बल निर्देश 2004/24/EC तथा यूएस एफडीए वानस्पतिक दवा दिशानिर्देशों के अंतर्गत वैश्विक बहु-एजेंट रिपोर्ट:",
                    "",
                    f"### 1. WIPO एवं GRATK संधि 2024 (अनिवार्य पूर्वज प्रकटीकरण)",
                    f"• **संधि स्थिति**: {wipo.get('status', 'प्रकटीकरण अनिवार्य')}",
                    f"• **वैधानिक विश्लेषण**: {wipo.get('reasoning', 'पारंपरिक ज्ञान एवं आनुवंशिक स्रोत प्रकटीकरण अनिवार्य।')}",
                    f"• **PCT फाइलिंग सिफारिश**: {wipo.get('recommended_claims', 'PCT अध्याय 1 के तहत उद्गम देश घोषणा संलग्न करें।')}",
                    "",
                    f"### 2. CBD, नगोया प्रोटोकॉल ABS एवं बुडापेस्ट संधि",
                    f"• **नियामक स्थिति**: {cbd.get('status', 'ABS सहमति एवं MAT आवश्यक')}",
                    f"• **अनुपालन अधिदेश**: {cbd.get('reasoning', 'अंतर्राष्ट्रीय स्रोत पहुंच हेतु पूर्व सूचित सहमति (PIC) आवश्यक।')}",
                    f"• **सूक्ष्मजीव/बायोटेक प्रपत्र**: {cbd.get('form_required', 'IRCC प्रमाण पत्र')}",
                    "",
                    f"### 3. यूरोपीय संघ EMA एवं THMPD (निर्देश 2004/24/EC)",
                    f"• **ईयू प्रवेश मार्ग**: {eu.get('status', 'THMPD 30-वर्षीय पारंपरिक उपयोग या खाद्य पूरक')}",
                    f"• **पंजीकरण आवश्यकताएं**: {eu.get('reasoning', 'EMA HMPC मोनोग्राफ अनुरूपता या 15 वर्ष ईयू + 15 वर्ष मूल देश साक्ष्य आवश्यक।')}",
                    "",
                    f"### 4. यूएस एफडीए एवं वैश्विक विनियामक (DSHEA / वानस्पतिक औषधियां)",
                    f"• **यूएस वर्गीकरण**: {us.get('status', 'आहार पूरक (DSHEA 21 CFR 101/111) या NDI सूचना')}",
                    f"• **एफडीए/एफटीसी अनुपालन**: {us.get('reasoning', 'रोग उपचार के भ्रामक दावों से बचें, केवल संरचना/कार्य दावे मान्य।')}",
                ]

                if collisions:
                    summary_parts.extend([
                        "",
                        f"### 5. अंतर्राष्ट्रीय विनियामक टकराव एवं निवारण (Cross-Border Collision Matrix)",
                        f"• ⚠️ **पहचाना गया टकराव**: {collisions[0]}"
                    ])

                if workaround:
                    summary_parts.extend([
                        "",
                        f"### 6. वैश्विक पेटेंट संरक्षण एवं निर्यात अनुपालन रणनीति",
                        f"• **अनुशंसित रणनीति**: {workaround}"
                    ])
                    if roadmap:
                        for step in roadmap:
                            summary_parts.append(f"• {step}")

                direct_bullets = []
                if wipo.get("status"):
                    direct_bullets.append(f"• **WIPO GRATK संधि (2024)**: {wipo.get('status')} — {wipo.get('reasoning', '').split('.')[0]}.")
                if cbd.get("status"):
                    direct_bullets.append(f"• **CBD/नगोया ABS & बुडापेस्ट**: {cbd.get('status')} — {cbd.get('reasoning', '').split('.')[0]}.")
                if eu.get("status"):
                    direct_bullets.append(f"• **यूरोपीय संघ (EMA THMPD)**: {eu.get('status')} — {eu.get('reasoning', '').split('.')[0]}.")
                if us.get("status"):
                    direct_bullets.append(f"• **यूएस एफडीए एवं वैश्विक बाजार**: {us.get('status')} — {us.get('reasoning', '').split('.')[0]}.")
                if workaround:
                    direct_bullets.append(f"• **वैश्विक रणनीतिक समाधान**: {workaround.split('.')[0]}.")

                state["direct_short_summary"] = "\n".join(direct_bullets)
                state["title"] = title
                state["summary"] = "\n".join(summary_parts)
                return state

            title = f"{herbs_str} — International Treaty & Global Market Assessment" if botanicals else "International Treaty & Cross-Border Intelligence"
            summary_parts = [
                f"### International Statutory Verdict: {herbs_str} ({dosage})",
                f"Cross-border multi-agent synthesis under WIPO GRATK Treaty 2024, CBD Nagoya Protocol ABS, Budapest Treaty, EU Directive 2004/24/EC (THMPD), and US FDA Botanical Drug Guidance:",
                "",
                f"### 1. WIPO & Diplomatic Conference GRATK Treaty (2024)",
                f"• **Statutory Status**: {wipo.get('status', 'Mandatory Disclosure Active')}",
                f"• **Treaty Examination**: {wipo.get('reasoning', 'Mandatory disclosure of country of origin and associated traditional knowledge.')}",
                f"• **PCT Filing Route**: {wipo.get('recommended_claims', 'Execute PCT Chapter 1 Declaration of Origin and TK source citing TKDL references.')}",
                "",
                f"### 2. CBD, Nagoya Protocol ABS & Budapest Treaty",
                f"• **ABS Status**: {cbd.get('status', 'Prior Informed Consent & MAT Mandatory')}",
                f"• **Statutory Mandate**: {cbd.get('reasoning', 'Cross-border access to genetic resources requires compliance with Nagoya ABS Clearing-House.')}",
                f"• **Certificate / Form**: {cbd.get('form_required', 'Internationally Recognized Certificate of Compliance (IRCC)')}",
                "",
                f"### 3. European Union Herbal Medicine Regime (EMA / Directive 2004/24/EC THMPD)",
                f"• **EU Gateway**: {eu.get('status', 'THMPD Traditional Use (30yr / 15yr EU) or Food Supplement')}",
                f"• **Registration Criteria**: {eu.get('reasoning', 'Requires EMA HMPC monograph alignment or 30-year bibliographic proof of safety.')}",
                "",
                f"### 4. US FDA & FTC Regime (Botanical Drug Guidance / DSHEA)",
                f"• **US Pathway**: {us.get('status', 'Dietary Supplement (21 CFR 101/111) or Investigational Botanical IND')}",
                f"• **FDA & FTC Compliance**: {us.get('reasoning', 'Structure/function claims only; strict prohibition on disease claims without drug approval.')}",
            ]

            if collisions:
                summary_parts.extend([
                    "",
                    f"### 5. International Cross-Regulatory Collision Matrix",
                    f"• ⚠️ **Detected Conflict**: {collisions[0]}"
                ])

            if workaround:
                summary_parts.extend([
                    "",
                    f"### 6. Actionable Strategy & International Filing Roadmap",
                    f"• **Recommended Strategy**: {workaround}"
                ])
                if roadmap:
                    for step in roadmap:
                        summary_parts.append(f"• {step}")

            direct_bullets = []
            if wipo.get("status"):
                direct_bullets.append(f"• **WIPO GRATK Treaty (2024)**: {wipo.get('status')} — {wipo.get('reasoning', '').split('.')[0]}.")
            if cbd.get("status"):
                direct_bullets.append(f"• **CBD/Nagoya Protocol ABS**: {cbd.get('status')} — {cbd.get('reasoning', '').split('.')[0]}.")
            if eu.get("status"):
                direct_bullets.append(f"• **European Union (EMA THMPD)**: {eu.get('status')} — {eu.get('reasoning', '').split('.')[0]}.")
            if us.get("status"):
                direct_bullets.append(f"• **US FDA & FTC Regimes**: {us.get('status')} — {us.get('reasoning', '').split('.')[0]}.")
            if workaround:
                direct_bullets.append(f"• **Strategic Workaround**: {workaround.split('.')[0]}.")

            state["direct_short_summary"] = "\n".join(direct_bullets)
            state["title"] = title
            state["summary"] = "\n".join(summary_parts)
            return state

        # National (India) Mode
        ipo = state.get("ipo_evaluation", {})
        nba = state.get("nba_evaluation", {})
        ayush = state.get("ayush_evaluation", {})
        allied = state.get("allied_evaluation", {})

        title = f"{herbs_str} — Multi-Agent Regulatory Assessment" if botanicals else f"Ayush Regulatory Intelligence Assessment"
        if language == "hi":
            title = f"{herbs_str} — बहु-एजेंट नियामक मूल्यांकन" if botanicals else "आयुष विनियामक बुद्धिमत्ता मूल्यांकन"

        if language == "hi":
            summary_parts = [
                f"### वैधानिक निष्कर्ष: {herbs_str} ({dosage})",
                f"भारतीय पेटेंट अधिनियम 1970, जैविक विविधता अधिनियम 2002/2023, औषधि एवं प्रसाधन सामग्री नियम 1945, FSSAI आयुर्वेद-आहार तथा DMROA 1954 के अंतर्गत बहु-एजेंट वैधानिक रिपोर्ट:",
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
                f"### 4. संबद्ध विनियामक प्रणालियाँ (FSSAI आयुर्वेद-आहार, DMROA 1954 एवं प्रसाधन)",
                f"• **संबद्ध व्यवस्था स्थिति**: {allied.get('status', 'FSSAI/DMROA विनियामक अनुपालन')}",
                f"• **विज्ञापन एवं वर्गीकरण**: {allied.get('reasoning', 'DMROA धारा 3 के अंतर्गत 54 अनुसूचीबद्ध रोगों के दावों पर पूर्ण प्रतिबंध। FSSAI आयुर्वेद-आहार विनियम 2022 का पालन करें।')}",
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
            if allied.get("status"):
                direct_bullets.append(f"• **FSSAI एवं विज्ञापन व्यवस्था**: {allied.get('status')} — {allied.get('reasoning', '').split('.')[0]}.")
            if workaround:
                direct_bullets.append(f"• **रणनीतिक समाधान**: {workaround.split('.')[0]}.")

            direct_short_summary = "\n".join(direct_bullets)
            state["direct_short_summary"] = direct_short_summary
            state["title"] = title
            state["summary"] = "\n".join(summary_parts)
            return state

        summary_parts = [
            f"### Statutory Verdict: {herbs_str} ({dosage})",
            f"Cross-regulatory multi-agent synthesis under the Patents Act 1970, Biological Diversity Act 2002/2023, Drugs & Cosmetics Rules 1945, and Allied Regimes (FSSAI / DMROA 1954):",
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
            f"### 4. Allied Regimes (FSSAI Ayurveda-Aahar, DMROA 1954 & Cosmetics)",
            f"• **Allied Regime Status**: {allied.get('status', 'FSSAI/DMROA Compliance Verification')}",
            f"• **Statutory Prohibitions & Standards**: {allied.get('reasoning', 'Section 3 DMROA strictly prohibits claims on 54 scheduled diseases. FSSAI Ayurveda-Aahar Regulations 2022 govern non-medicinal nutritional formulations.')}",
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
        if allied.get("status"):
            direct_bullets.append(f"• **Allied (FSSAI/DMROA) Regimes**: {allied.get('status')} — {allied.get('reasoning', '').split('.')[0]}.")
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

    # 1. Register All Nodes (India + International)
    graph.add_node("normalizer", normalizer_node)
    graph.add_node("ipr_agent", ipr_agent_node)
    graph.add_node("biodiversity_agent", biodiversity_agent_node)
    graph.add_node("ayush_agent", ayush_agent_node)
    graph.add_node("global_agent", global_agent_node)
    graph.add_node("allied_agent", allied_agent_node)
    graph.add_node("wipo_gratk_agent", wipo_gratk_agent_node)
    graph.add_node("cbd_nagoya_agent", cbd_nagoya_agent_node)
    graph.add_node("eu_thmpd_agent", eu_thmpd_agent_node)
    graph.add_node("us_fda_agent", us_fda_agent_node)
    graph.add_node("conflict_detector", conflict_detector_node)
    graph.add_node("workaround_synthesizer", workaround_synthesizer_node)
    graph.add_node("verifier", verifier_node)

    # 2. Wire Explicit Edges
    graph.add_edge(START, "normalizer")
    # India fan-out
    graph.add_edge("normalizer", "ipr_agent")
    graph.add_edge("normalizer", "biodiversity_agent")
    graph.add_edge("normalizer", "ayush_agent")
    graph.add_edge("normalizer", "allied_agent")
    graph.add_edge("ipr_agent", "conflict_detector")
    graph.add_edge("biodiversity_agent", "conflict_detector")
    graph.add_edge("ayush_agent", "conflict_detector")
    graph.add_edge("allied_agent", "conflict_detector")

    # International fan-out
    graph.add_edge("normalizer", "wipo_gratk_agent")
    graph.add_edge("normalizer", "cbd_nagoya_agent")
    graph.add_edge("normalizer", "eu_thmpd_agent")
    graph.add_edge("normalizer", "us_fda_agent")
    graph.add_edge("wipo_gratk_agent", "conflict_detector")
    graph.add_edge("cbd_nagoya_agent", "conflict_detector")
    graph.add_edge("eu_thmpd_agent", "conflict_detector")
    graph.add_edge("us_fda_agent", "conflict_detector")

    # Fan-in & verification pipeline
    graph.add_edge("conflict_detector", "workaround_synthesizer")
    graph.add_edge("workaround_synthesizer", "verifier")
    graph.add_edge("verifier", END)

    return graph

# Singleton instance
regulatory_graph = create_regulatory_graph()

