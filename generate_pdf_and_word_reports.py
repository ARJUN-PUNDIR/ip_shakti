#!/usr/bin/env python3
"""
IP-SAKTI Sahayak (SIH26045) - Dual PDF & Word Report Generator
Saves both official .pdf and .docx documents directly into ~/Downloads.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml

from docx_builder_base import (
    NAVY_PRIMARY, GOLD_ACCENT, SLATE_TEXT, MUTED_GRAY, ALERT_RED, SUCCESS_GREEN,
    HEX_NAVY, HEX_GOLD, HEX_LIGHT_BG, HEX_WARM_BG, HEX_ALERT_BG, HEX_SUCCESS_BG,
    add_styled_heading, add_body_p, add_bullet_p, add_callout_box, add_styled_table,
    set_cell_background, set_cell_margins
)

DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DOCX_PATH = os.path.join(DOWNLOADS_DIR, "IP_SAKTI_Sahayak_Full_Project_Report.docx")
PDF_PATH = os.path.join(DOWNLOADS_DIR, "IP_SAKTI_Sahayak_Full_Project_Report.pdf")


# ==============================================================================
# REPORTLAB NUMBERED CANVAS (Header & Footer with Page X of Y)
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawRightString(612 - 54, 792 - 36, "IP-SAKTI Sahayak | SIH26045 — Ministry of Ayush")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 792 - 42, 612 - 54, 792 - 42)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_str)
        self.drawString(54, 36, "Smart India Hackathon 2026 — Statutory Technical Project Report")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 612 - 54, 46)

        self.restoreState()


# ==============================================================================
# 1. BUILD PDF REPORT
# ==============================================================================
def build_pdf_report():
    print(f"Generating PDF at: {PDF_PATH}")
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_navy = colors.HexColor("#0F2942")
    c_gold = colors.HexColor("#B45309")
    c_slate = colors.HexColor("#1E293B")
    c_light_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")
    c_alert_border = colors.HexColor("#DC2626")
    c_alert_bg = colors.HexColor("#FEF2F2")

    # Typography Styles
    style_cover_tag = ParagraphStyle(
        "CoverTag",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=c_gold,
        spaceAfter=6
    )
    style_title = ParagraphStyle(
        "ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_navy,
        spaceAfter=8
    )
    style_subtitle = ParagraphStyle(
        "ReportSubtitle",
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=c_slate,
        spaceAfter=18
    )
    style_h1 = ParagraphStyle(
        "Heading1_Custom",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_navy,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        "Heading2_Custom",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_gold,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        "Body_Custom",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=c_slate,
        spaceAfter=6
    )
    style_bullet = ParagraphStyle(
        "Bullet_Custom",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=c_slate,
        leftIndent=14,
        spaceAfter=4
    )
    style_th = ParagraphStyle(
        "TableHead",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )
    style_td = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_slate
    )
    style_td_bold = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=c_navy
    )
    style_alert = ParagraphStyle(
        "AlertBox",
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#7F1D1D")
    )

    story = []

    # Title Block
    story.append(Paragraph("SMART INDIA HACKATHON 2026 | TECHNICAL SPECIFICATION REPORT", style_cover_tag))
    story.append(Paragraph("IP-SAKTI Sahayak: Master Technical Report", style_title))
    story.append(Paragraph(
        "<b>Multilingual, Citation-Grounded RAG Assistant & Cross-Regulatory Conflict Intelligence Engine</b><br/>"
        "Sponsoring Ministry: Ministry of Ayush, Government of India | Problem Statement ID: SIH26045",
        style_subtitle
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=c_gold, spaceBefore=2, spaceAfter=14))

    # Metadata Card Table
    meta_rows = [
        [Paragraph("Problem Statement ID:", style_td_bold), Paragraph("SIH26045 (Software Track)", style_td)],
        [Paragraph("Sponsoring Ministry:", style_td_bold), Paragraph("Ministry of Ayush, Government of India", style_td)],
        [Paragraph("Category / Domain:", style_td_bold), Paragraph("Ayush / Intellectual Property / Regulatory Regimes", style_td)],
        [Paragraph("System Architecture:", style_td_bold), Paragraph("Multi-Agent LangGraph StateGraph, NVIDIA Nemotron, MCP Server", style_td)],
        [Paragraph("Target Beneficiaries:", style_td_bold), Paragraph("Ayush Innovators, Vaidyas, Hakims, Researchers, MSMEs, Patent Examiners", style_td)]
    ]
    t_meta = Table(meta_rows, colWidths=[140, 364])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # Executive Summary
    story.append(Paragraph("Executive Summary (In Plain Words)", style_h1))
    story.append(Paragraph(
        "India's traditional knowledge heritage spans over 5,000 years and 4.4 lakh formulations recorded in the Traditional Knowledge Digital Library (TKDL). "
        "However, when grassroots researchers, doctors, and startups file patent applications, <b>over 70% are summarily rejected</b> at the Indian Patent Office under Sections 3(p) and 3(e) of the Patents Act, 1970. "
        "Simultaneously, applicants face criminal prosecution under Section 55 of the Biological Diversity Act, 2002 for failing to obtain mandatory prior approval from the National Biodiversity Authority (NBA). "
        "Exporting formulations abroad runs into the European Union's 15-year European use rule (THMPD) and US FDA dietary supplement restrictions.",
        style_body
    ))
    story.append(Paragraph(
        "<b>IP-SAKTI Sahayak</b> is an evidence-first, multi-agent AI co-pilot that resolves this crisis. "
        "It maps natural language and regional dialects (Hindi, Sanskrit, Urdu, Tamil) to Latin binomials and official pharmacopoeial monographs, executes parallel statutory evaluations across 4 jurisdictions in sub-80ms, "
        "flags cross-regulatory legal collisions, synthesizes defensible scientific workarounds (nano-carriers, synergism assays), and auto-drafts complete Patent Form 2 specifications and NBA Form 3 applications with SHA-256 Gazette integrity verification.",
        style_body
    ))
    story.append(Spacer(1, 10))

    # Section 1: Problem Statement
    story.append(Paragraph("1. The Regulatory & Technological Crisis (Problem Landscape)", style_h1))
    story.append(Paragraph(
        "Innovators in the Ayush domain face the 'Ayush Patent Paradox' across four key statutory fronts:",
        style_body
    ))
    
    table_barriers = [
        [Paragraph("Statutory Clause", style_th), Paragraph("Legal Barrier & Impact", style_th), Paragraph("Consequence If Ignored", style_th)],
        [
            Paragraph("Patents Act 1970 § 3(p)", style_td_bold),
            Paragraph("Bars patents on traditional knowledge or aggregations of known properties.", style_td),
            Paragraph("Over 70% of Ayush patent filings summarily rejected.", style_td)
        ],
        [
            Paragraph("Patents Act 1970 § 3(e)", style_td_bold),
            Paragraph("Bars 'mere admixtures' of known herbs without proven therapeutic synergism.", style_td),
            Paragraph("Instant refusal unless Combination Index CI < 0.75 is established.", style_td)
        ],
        [
            Paragraph("BD Act 2002 § 6(1) & § 55", style_td_bold),
            Paragraph("Mandatory prior approval from NBA (Form 3) before applying for any IPR.", style_td),
            Paragraph("Criminal liability: up to 5 yrs imprisonment and patent revocation.", style_td)
        ],
        [
            Paragraph("D&C Rules 1945 Rule 158-B", style_td_bold),
            Paragraph("Classifies Classical ASU (54 texts) vs Proprietary ASU (safety & trials required).", style_td),
            Paragraph("Unapproved drugs seized; manufacturing license revoked.", style_td)
        ],
        [
            Paragraph("EU THMPD 2004/24/EC", style_td_bold),
            Paragraph("Requires proof of 15 years of continuous medicinal use inside the European Union.", style_td),
            Paragraph("Direct market lockout for authentic classical Ayush medicines in Europe.", style_td)
        ]
    ]
    t_bar = Table(table_barriers, colWidths=[110, 240, 154])
    t_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
    ]))
    story.append(t_bar)
    story.append(Spacer(1, 12))

    # Section 2: Technical Pipeline Nodes
    story.append(Paragraph("2. Technical Pipeline Architecture: Node Breakdown", style_h1))
    story.append(Paragraph(
        "IP-SAKTI Sahayak implements an explicit Directed Acyclic Graph (DAG) state-machine engine across 8 specialized nodes:",
        style_body
    ))

    node_rows = [
        [Paragraph("Node ID & Name", style_th), Paragraph("Core Statutory Responsibilities", style_th), Paragraph("Technical Topics & Keywords", style_th)],
        [
            Paragraph("Node 1: Normalizer<br/><code>normalizer_node</code>", style_td_bold),
            Paragraph("Botanical entity recognition, intent extraction, dosage classification, and dialect normalization.", style_td),
            Paragraph("Vernacular Registry (80+ herbs), Regex word boundaries, API/UPI/SPI monographs, TKRC codes.", style_td)
        ],
        [
            Paragraph("Node 2: IPO Agent<br/><code>ipr_agent_node</code>", style_td_bold),
            Paragraph("Screens prior art under Patents Act Sections 3(p), 3(e), 3(d) against CSIR-TKDL.", style_td),
            Paragraph("CSIR-TKDL prior art overlap, patentability scoring, defensible claim drafting (<180 nm vesicles).", style_td)
        ],
        [
            Paragraph("Node 3: NBA Agent<br/><code>biodiversity_agent</code>", style_td_bold),
            Paragraph("Evaluates Biological Diversity Act compliance, foreign scrutiny, and ABS royalties.", style_td),
            Paragraph("Section 6(1) Form 3 mandate, Section 3 foreign scrutiny, Form 1 access, Section 55 penalties.", style_td)
        ],
        [
            Paragraph("Node 4: Ayush Agent<br/><code>ayush_node</code>", style_td_bold),
            Paragraph("Classifies drug licensing under Rule 158-B and Schedule T GMP factory standards.", style_td),
            Paragraph("Rule 158-B Cat I vs Cat II, Schedule T 1200 sq.ft cleanroom, Form 25-D, Form 24-D, Loan License 24-E.", style_td)
        ],
        [
            Paragraph("Node 5: Global Agent<br/><code>global_node</code>", style_td_bold),
            Paragraph("Evaluates export compliance, foreign trade hurdles, and WIPO PCT international treaties.", style_td),
            Paragraph("EU THMPD 15-yr rule workaround, EU Food Supplement 2002/46/EC, US FDA DSHEA 1994, WIPO PCT.", style_td)
        ],
        [
            Paragraph("Node 6: Conflict Node<br/><code>conflict_node</code>", style_td_bold),
            Paragraph("Fan-in node aggregating all 4 agents into a Cross-Regulatory Collision Matrix.", style_td),
            Paragraph("Truth-table collision logic (IPO refusal vs SALA approval; NBA prior clearance vs IPO grant).", style_td)
        ],
        [
            Paragraph("Node 7: Workaround<br/><code>workaround_node</code>", style_td_bold),
            Paragraph("Synthesizes formulation re-engineering and sequential filing roadmaps.", style_td),
            Paragraph("Chou-Talalay Theorem (CI < 0.75), Phyto-phospholipid nanocarriers, CO2 extraction, Form 24-E.", style_td)
        ],
        [
            Paragraph("Node 8: Verifier<br/><code>verifier_node</code>", style_td_bold),
            Paragraph("Verifies citations against authentic Government of India Gazettes via SHA-256.", style_td),
            Paragraph("SHA-256 cryptographic hashes, WIPO Lex, CDSCO, NBA portal deep links, Tri-Anchor verification.", style_td)
        ]
    ]
    t_nodes = Table(node_rows, colWidths=[120, 200, 184])
    t_nodes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
    ]))
    story.append(t_nodes)
    story.append(Spacer(1, 12))

    # Section 3: Technical Stack & Roadmap Topics
    story.append(Paragraph("3. Full Technical Stack & Roadmap Topic Directory", style_h1))
    story.append(Paragraph(
        "Key engineering concepts and software layers implemented across the platform:",
        style_body
    ))
    tech_items = [
        ("LangGraph StateGraph Engine", "Explicit Directed Acyclic Graph (DAG) with parallel fan-out across 4 agents and fan-in collision detection."),
        ("NVIDIA Nemotron 70B NIM API", "Hosted high-performance LLM inference with structured JSON schemas for roadmap and synthesis."),
        ("Ollama Local LLM Fallback", "Allows complete air-gapped sovereign deployment on government servers without internet connectivity."),
        ("Server-Sent Events (SSE) Streaming", "/api/query/stream provides sub-80ms initial statutory metadata and token-by-token synthesis."),
        ("Model Context Protocol (MCP) Server", "JSON-RPC 2.0 compliant server exposing 7 modular regulatory tools for Claude Desktop, Cursor, and agentic IDEs."),
        ("Chou-Talalay Synergism Theorem", "Mathematical proof of non-obvious therapeutic synergy (Combination Index CI < 0.75) to satisfy Section 3(e)."),
        ("Automated Document Assembly", "python-docx engine generates filled Indian Patent Form 2, NBA Form 3, and unified dossiers with professional styles."),
        ("FastAPI & Uvicorn ASGI Backend", "High-concurrency async Python framework with Pydantic validation and microsecond routing."),
        ("Cryptographic SHA-256 Gazette Registry", "Zero-hallucination guarantee linking citations to Government of India Gazette publication hashes."),
        ("Assist Plus Suite & Mentors", "6-stage milestone tracker with verified Ministry of Ayush mentor token validation.")
    ]
    for title, desc in tech_items:
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", style_bullet))
    story.append(Spacer(1, 12))

    # Section 4: Pitching Strategy
    story.append(Paragraph("4. How to Present Our Project (Hackathon Pitch Blueprint)", style_h1))
    story.append(Paragraph("<b>The 5-Minute Winning Pitch Sequence:</b>", style_h2))
    story.append(Paragraph("• <b>Minute 1 (The Hook):</b> Highlight that 70%+ Ayush patent applications fail under Sections 3(p)/3(e) and researchers face up to 5 years in prison under Section 55 of the Biodiversity Act. Generic AI hallucinates fake laws.", style_bullet))
    story.append(Paragraph("• <b>Minute 2 (The Solution):</b> Explain how IP-SAKTI Sahayak runs 4 regulatory agents in parallel in <80ms, catches contradictions, and suggests scientific workarounds.", style_bullet))
    story.append(Paragraph("• <b>Minute 3 (Live Demo):</b> Trigger Scenario 1 (Anti-arthritic Nanogel with Haldi, Shallaki, Gandhapura). Show the 4 status badges, the detected collision, the workaround (CI < 0.75), and click 'Draft Patent Form 2' to download the complete Word document.", style_bullet))
    story.append(Paragraph("• <b>Minute 4 (Enterprise Feasibility):</b> Emphasize zero hallucinations (SHA-256 Gazette hashes), the standard MCP tool server, and NIC MeghRaj air-gapped readiness.", style_bullet))
    story.append(Paragraph("• <b>Minute 5 (Q&A Defense):</b> Defend against questions on legal hallucination, Vaidya vernacular support, data security, and government portal integration.", style_bullet))
    story.append(Spacer(1, 10))

    # Section 5: Resources
    story.append(Paragraph("5. Official Resources & References Used", style_h1))
    story.append(Paragraph("• <b>Statutory Acts:</b> The Patents Act 1970 (§ 3p, § 3e, § 3d), Biological Diversity Act 2002/2023 (§ 3, § 6, § 55), Drugs & Cosmetics Rules 1945 (Rule 158-B, Schedule T), FSSAI Regulations 2022.", style_bullet))
    story.append(Paragraph("• <b>International Treaties:</b> EU Directive 2004/24/EC (THMPD), EU Directive 2002/46/EC, US FDA DSHEA 1994, WIPO Patent Cooperation Treaty (PCT).", style_bullet))
    story.append(Paragraph("• <b>Pharmacopoeias & Databases:</b> Ayurvedic Pharmacopoeia of India (API), Unani Pharmacopoeia (UPI), Siddha Pharmacopoeia (SPI), CSIR-TKDL, and TKRC taxonomies.", style_bullet))
    story.append(Paragraph("• <b>Software & Libraries:</b> FastAPI, Uvicorn, LangGraph StateGraph, NVIDIA Nemotron NIM, Ollama, python-docx, ReportLab, Model Context Protocol (MCP).", style_bullet))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build complete!")


# ==============================================================================
# 2. BUILD WORD (.DOCX) REPORT
# ==============================================================================
def build_docx_report():
    print(f"Generating DOCX at: {DOCX_PATH}")
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("IP-SAKTI Sahayak | SIH26045 — Ministry of Ayush")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = MUTED_GRAY
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Confidential — Smart India Hackathon 2026 Technical Project Report & Presentation Guide")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = MUTED_GRAY

    # Title
    title_p = doc.add_paragraph()
    sub_tag = title_p.add_run("SMART INDIA HACKATHON 2026 | MASTER TECHNICAL REPORT\n")
    sub_tag.bold = True
    sub_tag.font.name = "Calibri"
    sub_tag.font.size = Pt(11)
    sub_tag.font.color.rgb = GOLD_ACCENT

    r_main = title_p.add_run("IP-SAKTI Sahayak\n")
    r_main.bold = True
    r_main.font.name = "Calibri"
    r_main.font.size = Pt(26)
    r_main.font.color.rgb = NAVY_PRIMARY

    r_sub = title_p.add_run("Multilingual, Citation-Grounded RAG Assistant & Cross-Regulatory Conflict Intelligence Engine for Ayush, Indian (IPO, NBA, CDSCO) & Global (WIPO, USPTO, EPO) IP Regimes")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = SLATE_TEXT

    # Line
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_after = Pt(16)
    pBdr = parse_xml(f'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:bottom w:val="single" w:sz="18" w:space="6" w:color="{HEX_GOLD}"/></w:pBdr>')
    p_line._p.get_or_add_pPr().append(pBdr)

    # Metadata Table
    meta_data = [
        ("Problem Statement ID:", "SIH26045 (Software Track)"),
        ("Sponsoring Ministry:", "Ministry of Ayush, Government of India"),
        ("Theme / Domain:", "Ayush / Intellectual Property / Regulatory Regimes"),
        ("Architecture:", "LangGraph-Style StateGraph DAG, NVIDIA Nemotron NIM, MCP Server"),
        ("Target Users:", "Ayush Innovators, Researchers, Vaidyas, Hakims, MSMEs, Patent Examiners")
    ]
    add_styled_table(doc, ["Attribute", "Specification Details"], meta_data, col_widths=[2.0, 4.5])

    add_callout_box(
        doc,
        "\"Over 70% of herbal patent applications are summarily rejected at the Indian Patent Office under Sections 3(p) and 3(e), while innovators face criminal prosecution under Section 55 of the Biological Diversity Act for failing to secure prior NBA approval. IP-SAKTI Sahayak eliminates this friction through multi-agent statutory reasoning grounded in SHA-256 Gazette citations.\"",
        title="CORE EXECUTIVE THESIS",
        alert_type="gold"
    )

    # Section 1
    add_styled_heading(doc, "1. Executive Summary & Problem Breakdown", level=1)
    add_body_p(doc, "Traditional Indian medicine represents over 5,000 years of medicinal knowledge and 4.4 lakh formulations in the Traditional Knowledge Digital Library (TKDL). However, the Ayush bio-economy faces structural hurdles: patent law bars traditional knowledge and admixtures without proven synergy, biodiversity law mandates prior NBA approval under threat of prison, drug licensing separates classical from proprietary formulas, and export markets impose strict local usage or dietary guidelines.")
    add_body_p(doc, "Generic LLMs (ChatGPT, Claude) fail because they hallucinate fake statutory clauses, smooth over regulatory conflicts, have zero awareness of NBA Form 3 requirements, and fail to ground vernacular herbal terms in pharmacopoeial monographs.")

    # Section 2
    add_styled_heading(doc, "2. What Our Project Actually Does", level=1)
    add_bullet_p(doc, "Translates colloquial and traditional names (Haldi, Shallaki, Asgandh) into Latin binomials and official Ayurvedic Pharmacopoeia of India (API) monographs.", bold_prefix="1. Dialect & Botanical Recognition: ")
    add_bullet_p(doc, "Evaluates Patent Law (IPO), Biodiversity Law (NBA), Drug Licensing (SALA), and Global Export (EMA/FDA) simultaneously in under 80ms.", bold_prefix="2. Parallel Multi-Agent Screening: ")
    add_bullet_p(doc, "Detects statutory contradictions between drug licensing approvals and patent law traditional knowledge exclusions.", bold_prefix="3. Collision Detection Matrix: ")
    add_bullet_p(doc, "Provides actionable scientific strategies: nano-carriers (<180 nm), Chou-Talalay synergism assays (CI < 0.75), and Form 24-E loan licensing.", bold_prefix="4. Strategic Workarounds: ")
    add_bullet_p(doc, "Produces attorney-ready Word documents for Indian Patent Form 2 and NBA Form 3 with one click.", bold_prefix="5. Automated Legal Drafting: ")
    add_bullet_p(doc, "Verifies all citations against authentic Government of India Gazettes using cryptographic SHA-256 hashes.", bold_prefix="6. Zero-Hallucination Integrity: ")

    # Section 3: Nodes
    add_styled_heading(doc, "3. Technical Pipeline Architecture: Every Node's Responsibilities", level=1)
    nodes_info = [
        ("Node 1: NormalizerNode", "Botanical Named Entity Recognition (NER), vernacular dialect mapping, API/UPI/SPI monograph cross-referencing, TKRC codes, and dosage form classification."),
        ("Node 2: IPRAgentNode", "Statutory patentability screening under Patents Act Sections 3(p), 3(e), 3(d), CSIR-TKDL prior art overlap, and defensible vesicular claim formulation."),
        ("Node 3: BiodiversityAgentNode", "Biological Diversity Act compliance, Section 6(1) Form 3 mandatory prior approval, Section 3 foreign entity scrutiny, Form 1 access, Section 55 criminal liabilities, and ABS royalties."),
        ("Node 4: AyushAgentNode", "Drug licensing under D&C Rules 1945 Rule 158-B (Classical Cat I vs Proprietary Cat II), Schedule T 1,200 sq. ft. cleanroom validation, Form 25-D, Form 24-D, and Form 24-E loan licensing."),
        ("Node 5: GlobalExportAgentNode", "Export market entry: EU THMPD Directive 2004/24/EC 15-year usage rule workaround, EU Food Supplement Directive 2002/46/EC, US FDA DSHEA 1994 (21 CFR Part 111 cGMP), and WIPO PCT."),
        ("Node 6: ConflictDetectorNode", "Fan-in node evaluating the Cross-Regulatory Collision Matrix to catch statutory contradictions across patent, biodiversity, drug licensing, and trade laws."),
        ("Node 7: WorkaroundSynthesizerNode", "Converts legal hurdles into actionable scientific re-engineering: Chou-Talalay synergism theorem (CI < 0.75), phospholipid nanocarriers, supercritical CO2 extraction, and 5-stage roadmap."),
        ("Node 8: VerifierNode", "Cryptographic Gazette verification checking SHA-256 integrity hashes against official Government of India Gazettes, WIPO Lex, and CDSCO/NBA endpoints.")
    ]
    add_styled_table(doc, ["Pipeline Node", "Statutory Responsibilities & Technical Topics"], nodes_info, col_widths=[2.2, 4.3])

    # Section 4: Full Roadmap Topic Directory
    add_styled_heading(doc, "4. Full Technical Stack & Roadmap Topic Directory", level=1)
    tech_data = [
        ("LangGraph StateGraph Engine", "Explicit Directed Acyclic Graph (DAG) state-machine with parallel fan-out to 4 agents and fan-in collision evaluation."),
        ("NVIDIA Nemotron 70B NIM API", "Hosted enterprise LLM inference with structured JSON schemas for roadmap synthesis and grounded Q&A."),
        ("Ollama Local LLM Fallback", "Offline fallback allowing sovereign, air-gapped deployment on National Informatics Centre (NIC) servers."),
        ("Server-Sent Events (SSE)", "/api/query/stream provides sub-80ms initial statutory metadata and token-by-token streaming to the frontend."),
        ("Model Context Protocol (MCP)", "Standardized JSON-RPC 2.0 tool server exposing 7 modular regulatory tools for Claude Desktop, Cursor, and IDE agents."),
        ("Chou-Talalay Synergism", "Mathematical theorem proving non-obvious therapeutic synergy (CI < 0.75) to satisfy Section 3(e)."),
        ("Automated Document Assembly", "python-docx engine generates ready-to-file Indian Patent Form 2 specifications and NBA Form 3 applications."),
        ("FastAPI & Uvicorn ASGI", "High-concurrency async Python framework with microsecond routing and static asset serving."),
        ("SHA-256 Gazette Hashes", "Cryptographic integrity hashes of Government of India Gazettes to eliminate legal hallucination."),
        ("Assist Plus Suite & Mentors", "6-stage milestone tracker with verified Ministry of Ayush mentor token validation.")
    ]
    add_styled_table(doc, ["Technology / Topic Name", "Implementation Details"], tech_data, col_widths=[2.3, 4.2])

    # Section 5: Pitching Guide
    add_styled_heading(doc, "5. Hackathon Pitching Blueprint (5-Minute Sequence)", level=1)
    add_bullet_p(doc, "70%+ Ayush patent applications fail under Sections 3(p)/3(e), innovators face 5 yrs prison under Section 55 of BD Act, and generic AI hallucinates fake laws.", bold_prefix="Minute 1 (The Hook): ")
    add_bullet_p(doc, "IP-SAKTI Sahayak runs 4 regulatory agents in parallel in <80ms, catches contradictions, and synthesizes scientific workarounds.", bold_prefix="Minute 2 (The Solution): ")
    add_bullet_p(doc, "Trigger Scenario 1 (Anti-arthritic Nanogel). Show the 4 badges, the collision warning, the workaround, and click 'Draft Patent Form 2' to download the Word doc.", bold_prefix="Minute 3 (Live Demo): ")
    add_bullet_p(doc, "Zero hallucinations (SHA-256 hashes), standard MCP tool server, and NIC MeghRaj air-gapped readiness.", bold_prefix="Minute 4 (Technical Feasibility): ")
    add_bullet_p(doc, "Address judge questions on legal hallucination, vernacular support, formulation secrecy, and API integration.", bold_prefix="Minute 5 (Q&A Defense): ")

    # Section 6: Resources
    add_styled_heading(doc, "6. Official Resources & References Used", level=1)
    add_bullet_p(doc, "Patents Act 1970 (§ 3p, § 3e, § 3d), Biological Diversity Act 2002/2023 (§ 3, § 6, § 55), Drugs & Cosmetics Rules 1945 (Rule 158-B, Schedule T), FSSAI 2022.", bold_prefix="Statutes: ")
    add_bullet_p(doc, "EU Directive 2004/24/EC (THMPD), EU Directive 2002/46/EC, US FDA DSHEA 1994, WIPO Patent Cooperation Treaty (PCT).", bold_prefix="International Treaties: ")
    add_bullet_p(doc, "Ayurvedic Pharmacopoeia of India (API), Unani Pharmacopoeia (UPI), Siddha Pharmacopoeia (SPI), CSIR-TKDL, and TKRC taxonomies.", bold_prefix="Pharmacopoeias: ")
    add_bullet_p(doc, "FastAPI, LangGraph StateGraph, NVIDIA Nemotron NIM, Ollama, python-docx, ReportLab, Model Context Protocol (MCP).", bold_prefix="Software: ")

    doc.save(DOCX_PATH)
    print("DOCX build complete!")


if __name__ == "__main__":
    build_pdf_report()
    build_docx_report()
    print("All downloads successfully generated and saved to ~/Downloads!")
