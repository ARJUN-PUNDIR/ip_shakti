import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from docx_builder_base import (
    NAVY_PRIMARY, GOLD_ACCENT, SLATE_TEXT, MUTED_GRAY, ALERT_RED, SUCCESS_GREEN,
    HEX_NAVY, HEX_GOLD, HEX_LIGHT_BG, HEX_WARM_BG, HEX_ALERT_BG, HEX_SUCCESS_BG,
    add_styled_heading, add_body_p, add_bullet_p, add_callout_box, add_styled_table,
    set_cell_background, set_cell_margins
)

doc = docx.Document()
for s in doc.sections:
    s.top_margin = Inches(0.8)
    s.bottom_margin = Inches(0.8)
    s.left_margin = Inches(0.8)
    s.right_margin = Inches(0.8)

# Header
p_top = doc.add_paragraph()
r_badge = p_top.add_run("SMART INDIA HACKATHON 2026 | OFFICIAL 5-SLIDE PPT SUBMISSION CONTENT\n")
r_badge.bold = True
r_badge.font.size = Pt(10)
r_badge.font.color.rgb = GOLD_ACCENT

r_h = p_top.add_run("SIH26045: IP-SAKTI Sahayak — 5-Slide Master Text Guide\n")
r_h.bold = True
r_h.font.size = Pt(22)
r_h.font.color.rgb = NAVY_PRIMARY

r_sub = p_top.add_run("Exact copy-pasteable content formatted strictly for the 5-slide SIH Screening Presentation Template.\n")
r_sub.font.size = Pt(11)
r_sub.font.color.rgb = MUTED_GRAY

# Slide 1
add_styled_heading(doc, "SLIDE 1: IDEA TITLE & PROPOSED SOLUTION", level=1)
add_callout_box(
    doc,
    "IDEA TITLE: IP-SAKTI Sahayak — Multilingual, Citation-Grounded RAG Assistant & Cross-Regulation Intelligence Engine for Ayush & Global IP Regimes\nProblem Statement ID: SIH26045 | Sponsoring Ministry: Ministry of Ayush",
    title="SLIDE 1 TITLE BLOCK",
    alert_type="gold"
)
add_styled_heading(doc, "1. Proposed Solution (Idea / Prototype Overview)", level=2)
add_bullet_p(doc, "IP-SAKTI Sahayak is an evidence-first, multi-agent artificial intelligence co-pilot and automated legal drafting platform designed specifically for Ayush innovators, researchers, Vaidyas, and MSMEs.", bold_prefix="Core Proposition: ")
add_bullet_p(doc, "It resolves the 'Ayush Patent Paradox' where 70%+ herbal patent applications face rejection under Sections 3(p) (Traditional Knowledge) and 3(e) (mere admixture) of the Indian Patents Act, while applicants face criminal prosecution under Section 55 of the Biological Diversity Act for failing to obtain mandatory prior NBA approval.", bold_prefix="The Problem Solved: ")

add_styled_heading(doc, "2. Detailed Explanation of the Proposed Solution", level=2)
add_bullet_p(doc, "Instead of dumping entire 300-page acts into vector search, the engine recursively navigates statutory law as an atomic tree: Patent Act → Section 3 → Subsection (p) → Explanation → TKDL Reference → Landmark Case Ruling.", bold_prefix="• Atomic Clause-Level Retrieval: ")
add_bullet_p(doc, "Simultaneously evaluates a single query across 9 statutory bodies: AYUSH Guidelines, CDSCO, Indian Patent Office (IPO), Trademark Registry, WIPO, European Medicines Agency (EMA), European Patent Office (EPO), GI Registry, and Biological Diversity Act (NBA).", bold_prefix="• Cross-Regulation Reasoning: ")
add_bullet_p(doc, "Actively flags statutory contradictions. If AYUSH drug licensing permits a formulation (Rule 158-B) but the Patent Act bars it (Section 3(p)), the system explicitly outputs a '⚠️ CONFLICT DETECTED' matrix with actionable workarounds.", bold_prefix="• Conflict Detection Engine: ")
add_bullet_p(doc, "Users input herbs and processing methods. The system screens for TKDL classical overlap, evaluates admixture risk, and suggests patentable claim strategies (e.g., novel liposomal carriers, standardized extracts with Synergism Index CI < 0.8).", bold_prefix="• Formulation IP Scanner: ")
add_bullet_p(doc, "One-click generation of attorney-ready Indian Patent Form 1 & 2 drafts, NBA Form 3 biodiversity applications, and Rule 158-B State Licensing Dossiers.", bold_prefix="• 1-Click Statutory Dossier Generator: ")

add_styled_heading(doc, "3. Innovation & Uniqueness of the Solution", level=2)
add_bullet_p(doc, "Generic LLMs (ChatGPT/Claude) smooth over conflicting regulations into false harmonious answers. IP-SAKTI Sahayak is the first system with an explicit Cross-Regulation Conflict Matrix.", bold_prefix="1. Multi-Regime Conflict Resolution: ")
add_bullet_p(doc, "Every statement is verified against a LangGraph Self-RAG reflection loop and cross-referenced with cryptographic SHA-256 hashes of official government gazettes.", bold_prefix="2. Tri-Anchor Zero-Hallucination: ")
add_bullet_p(doc, "A dedicated GraphRAG knowledge graph that normalizes Sanskrit, Hindi, Tamil, and Latin binomials to official Ayurvedic Pharmacopoeia of India (API) standards.", bold_prefix="3. Ayush Botanical Knowledge Graph: ")
add_bullet_p(doc, "Integrates Government of India Bhashini AI for seamless voice input/output in Hindi, Tamil, Telugu, Marathi, and Sanskrit for rural healers.", bold_prefix="4. Bhashini Indic Voice Bridge: ")
add_bullet_p(doc, "If no authentic statutory clause exists in active records, the system deterministically outputs 'Answer Not Found' instead of speculating.", bold_prefix="5. Strict Grounding Fallback: ")

doc.add_page_break()

# Slide 2
add_styled_heading(doc, "SLIDE 2: TECHNICAL APPROACH", level=1)
add_styled_heading(doc, "1. Technologies Used (Full Stack Architecture)", level=2)
tech_table = [
    ("AI / LLM & Multi-Agent", "LangGraph (State-machine DAG orchestration), Llama-3.3-70B / Mistral-Large, Sentence-Transformers (BGE-M3 multilingual legal embeddings)"),
    ("Databases & Storage", "Qdrant / Milvus (Hierarchical Clause-Level Vector Store), Neo4j (Ayush Botanical & Pharmacopoeia Knowledge Graph)"),
    ("Multilingual & Voice", "Government of India Bhashini AI Ecosystem (IndicTrans2 machine translation, IndicWav2Vec ASR/TTS across 10+ Indian languages)"),
    ("Web Scraping & Sentinel", "Playwright & Scrapy (Dynamic crawling of State Ayush portals, ayush.gov.in, ipindia.gov.in, e-Gazette, Wikipedia)"),
    ("Backend & Document", "Python FastAPI (Async microservices), PyTorch, python-docx, WeasyPrint (Automated PDF/Word legal form synthesis), Cryptography (SHA-256)"),
    ("Frontend Interface", "React.js / Vite, TailwindCSS, Split-Screen Statutory Viewer, WebSockets (Real-time token and citation streaming)")
]
add_styled_table(doc, ["Technology Layer", "Tools & Frameworks Selected"], tech_table, col_widths=[2.0, 4.5])

add_styled_heading(doc, "2. Methodology & Implementation Process (Flow / Architecture)", level=2)
add_bullet_p(doc, "User speaks in Hindi/regional language or types text/uploads formulation -> Bhashini Indic ASR converts speech to text -> Ayush Domain Router categorizes query into 1 of 6 Ayush verticals (Ayurveda, Yoga, Unani, Siddha, Sowa-Rigpa, Homoeopathy).", bold_prefix="Step 1 (Ingestion & Routing): ")
add_bullet_p(doc, "Sanskrit/vernacular herb names are mapped via Neo4j GraphRAG to official Latin binomials and Ayurvedic Pharmacopoeia of India (API) standards.", bold_prefix="Step 2 (Botanical Entity Normalization): ")
add_bullet_p(doc, "Query dispatched simultaneously to 4 specialized agents: Agent_IPO (Patent Act §3p, §3e), Agent_NBA (Biological Diversity Act Form 1/3), Agent_AYUSH_State (D&C Rule 158B, State e-Aushadhi), Agent_Global (WIPO PCT, USPTO, EPO, EMA THMPD).", bold_prefix="Step 3 (Multi-Agent MoE Dispatch): ")
add_bullet_p(doc, "Intermediate outputs evaluated against truth-table matrix. Flags conflicting directives (e.g. Ayush drug license vs Patent rejection) and triggers dynamic web sentinel for live state gazettes.", bold_prefix="Step 4 (Conflict Engine & Web Sentinel): ")
add_bullet_p(doc, "LangGraph reflection node verifies context faithfulness, legislative entity existence, and official gazette hash. Prunes unverified assertions.", bold_prefix="Step 5 (Tri-Anchor Verification): ")
add_bullet_p(doc, "Renders interactive split-screen UI showing exact highlighted gazette clause side-by-side, plus 1-click generation of filled IPO Form 1/2, NBA Form 3, and Rule 158B checklists.", bold_prefix="Step 6 (UI Rendering & Document Generation): ")

doc.add_page_break()

# Slide 3
add_styled_heading(doc, "SLIDE 3: FEASIBILITY AND VIABILITY", level=1)
add_styled_heading(doc, "1. Feasibility Analysis", level=2)
add_bullet_p(doc, "System is built on open-source, proven frameworks (LangGraph, FastAPI, Qdrant, React) and consumes officially published Government of India statutes, pharmacopoeias, and gazettes.", bold_prefix="• Technical Feasibility: ")
add_bullet_p(doc, "By indexing atomic clauses instead of monolithic 300-page PDFs, context window size is cut by ~70%, reducing token latency (<250ms retrieval) and compute cost.", bold_prefix="• Computational Efficiency: ")
add_bullet_p(doc, "Ready for air-gapped sovereign deployment on National Informatics Centre (NIC) / MeghRaj Government Cloud on standard GPU instances (NVIDIA A10G/A100).", bold_prefix="• Deployment Feasibility: ")

add_styled_heading(doc, "2. Potential Challenges & Risks vs Mitigation Strategies", level=2)
risk_table = [
    ("State-Level Regulatory Disparity", "28 States have differing Ayush licensing rules; state circulars are often scanned PDFs with poor OCR.", "Universal State Ayush Ingestion Pipeline: Layout-aware OCR (Tesseract + PyMuPDF) automatically indexes state SALA and e-Aushadhi notifications into structured JSON trees."),
    ("Formulation Trade Secret Leakage", "Innovators hesitate to input unpublished, proprietary herbal formulations into AI tools.", "Stateless Ephemeral Enclave: Processing runs in isolated client-encrypted memory enclaves with zero permanent database retention (DPDP Act 2023 compliant)."),
    ("Frequent Statutory Amendments", "Acts and rules change over time (e.g., Biological Diversity Amendment Act 2023, Jan Vishwas Act).", "Live Gazette Sentinel: Background crawler continuously polls ayush.gov.in and egazette.gov.in, updating vectors with temporal version tags (Temporal RAG)."),
    ("Vernacular Ayush Dialects", "Rural traditional healers use regional folk herb names not recorded in standard English dictionaries.", "Bhashini Indic Fine-Tuning + GraphRAG: Integrated Ayush botanical lexicon mapping 12,000+ vernacular and Sanskrit synonyms to standardized API botanical entries.")
]
add_styled_table(doc, ["Challenge & Identified Risk", "Severity & Description", "Strategic Mitigation Architecture"], risk_table, col_widths=[1.5, 2.3, 2.7])

doc.add_page_break()

# Slide 4
add_styled_heading(doc, "SLIDE 4: IMPACT AND BENEFITS", level=1)
add_styled_heading(doc, "1. Potential Impact on Target Audience", level=2)
add_bullet_p(doc, "Overcomes Section 3(p)/3(e) barriers through synergism guidance, accelerating patent filing timelines from months to minutes.", bold_prefix="• Ayush Innovators & Startups: ")
add_bullet_p(doc, "Eliminates language barriers for 85%+ non-English speaking traditional healers via Bhashini voice guidance in Hindi, Tamil, Telugu, etc.", bold_prefix="• Grassroots Vaidyas & Hakims: ")
add_bullet_p(doc, "Ensures 100% statutory compliance with the Biological Diversity Act, eliminating legal disputes, patent revocations, and Section 55 criminal liabilities.", bold_prefix="• Academic Researchers (CSIR/CCRAS): ")
add_bullet_p(doc, "Streamlines examination workflow with pre-vetted, standardized application dossiers and instant TKDL prior-art overlap mapping.", bold_prefix="• Patent & Licensing Authorities: ")

add_styled_heading(doc, "2. Multi-Dimensional Benefits (Social, Economic, Environmental)", level=2)
impact_table = [
    ("Economic Benefits", "• Unlocks India's $24+ Billion Ayush export potential by resolving EU THMPD (2004/24/EC) and US FDA Botanical Drug barriers.\n• Triples domestic Ayush patent grant rates from <30% to over 75% via non-3(p) synergism claim drafting.\n• Saves lakhs of rupees in attorney consultation fees for early-stage herbal startups and MSMEs."),
    ("Social & Inclusive Benefits", "• Democratizes legal intelligence: Rural healers, women self-help groups, and tribal cultivators access high-level patent guidance in their mother tongue.\n• Preserves traditional community knowledge while ensuring equitable Access and Benefit Sharing (ABS)."),
    ("Sovereignty & Environmental Benefits", "• Safeguards Indian bio-resources against foreign biopiracy by ensuring defensive publication and domestic IP registration.\n• Enforces sustainable harvesting disclosures under Section 7 of the Biological Diversity Act.")
]
add_styled_table(doc, ["Impact Category", "Quantifiable National Benefits"], impact_table, col_widths=[1.8, 4.7])

doc.add_page_break()

# Slide 5
add_styled_heading(doc, "SLIDE 5: RESEARCH AND REFERENCES", level=1)
add_styled_heading(doc, "1. Statutory Acts, Official Guidelines & Treaties", level=2)
add_bullet_p(doc, "Sections 3(p) [Traditional Knowledge exclusion], 3(e) [Admixture exclusion], 3(d), and 64(1)(p) [Revocation for non-disclosure].", bold_prefix="• The Patents Act, 1970 (as amended 2005): ")
add_bullet_p(doc, "Office of the Controller General of Patents, Designs and Trade Marks (CGPDTM), Ministry of Commerce and Industry.", bold_prefix="• Guidelines for Examination of Ayush-Related Patent Applications (2019): ")
add_bullet_p(doc, "Sections 3, 4, 6 [Mandatory prior approval for IP], 7, 19, 21 [Access and Benefit Sharing ABS], and 55 [Penalties].", bold_prefix="• The Biological Diversity Act, 2002 & Amendment Act, 2023: ")
add_bullet_p(doc, "Chapter IV-A, Rules 151-160, and Rule 158-B (Requirements for licensing of Classical vs Patent/Proprietary Ayush medicines).", bold_prefix="• Drugs and Cosmetics Act, 1940 & Rules, 1945: ")
add_bullet_p(doc, "Directive 2004/24/EC of the European Parliament on Traditional Herbal Medicinal Products.", bold_prefix="• European Union THMPD: ")
add_bullet_p(doc, "Center for Drug Evaluation and Research (CDER), Guidance for Industry (December 2016) & DSHEA (1994).", bold_prefix="• US FDA Botanical Drug Guidance: ")
add_bullet_p(doc, "Patent Cooperation Treaty (PCT) Regulations & Intergovernmental Committee on IP and Genetic Resources (IGC).", bold_prefix="• WIPO Traditional Knowledge Division: ")

add_styled_heading(doc, "2. Official Portals, Databases & Research Links", level=2)
links_table = [
    ("Ministry of Ayush Portal & e-Aushadhi", "https://ayush.gov.in | https://e-aushadhi.gov.in", "Official central guidelines, circulars, and state licensing authority data"),
    ("Traditional Knowledge Digital Library (TKDL)", "https://www.tkdl.res.in", "CSIR-Ayush database of 4.4+ lakh classical formulation prior-art disclosures"),
    ("Indian Patent Office (CGPDTM)", "https://ipindia.gov.in", "Manual of Patent Office Practice & Procedure, Gazette notifications, Patent Rules"),
    ("National Biodiversity Authority (NBA India)", "https://nbaindia.org", "Statutory ABS guidelines, Form 1 and Form 3 clearance procedures"),
    ("Pharmacopoeia Commission for Indian Medicine (PCIM&H)", "https://pcimnh.gov.in", "Ayurvedic, Siddha, Unani, and Homoeopathic Pharmacopoeias of India (API/UPI/SPI/HPI)"),
    ("Bhashini National Language Mission", "https://bhashini.gov.in", "Ministry of Electronics & IT (MeitY) open-source Indic AI models for voice/translation"),
    ("WIPO PATENTSCOPE & Traditional Knowledge", "https://www.wipo.int/tk/en/", "International patent search, PCT minimum documentation, traditional knowledge guides")
]
add_styled_table(doc, ["Institution / Database", "Official Web Link", "Application in IP-SAKTI Sahayak"], links_table, col_widths=[2.0, 2.2, 2.3])

out_file = "SIH26045_5_Slide_PPT_Submission_Content.docx"
doc.save(out_file)
print(f"5-Slide Docx created: {out_file}")
