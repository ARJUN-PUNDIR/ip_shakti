#!/usr/bin/env python3
"""
Generates the Comprehensive Revenue & Monetization Model for IP-SAKTI Sahayak (SIH26045).
Saves both an executive Word (.docx) document and a Markdown (.md) document to /Users/arjunsinghpundir/Downloads.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from docx_builder_base import (
    NAVY_PRIMARY, GOLD_ACCENT, SLATE_TEXT, MUTED_GRAY, ALERT_RED, SUCCESS_GREEN,
    HEX_NAVY, HEX_GOLD, HEX_LIGHT_BG, HEX_WARM_BG, HEX_ALERT_BG, HEX_SUCCESS_BG, HEX_BORDER,
    set_cell_background, set_cell_margins, set_table_borders,
    add_styled_heading, add_body_p, add_bullet_p, add_callout_box
)

DOWNLOADS_DIR = "/Users/arjunsinghpundir/Downloads"
DOCX_PATH = os.path.join(DOWNLOADS_DIR, "IP_SAKTI_Sahayak_Comprehensive_Revenue_Model.docx")
MD_PATH = os.path.join(DOWNLOADS_DIR, "IP_SAKTI_Sahayak_Comprehensive_Revenue_Model.md")

def add_stat_callout(doc, stats_list):
    table = doc.add_table(rows=1, cols=len(stats_list))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w = Inches(6.5 / len(stats_list))
    set_table_borders(table)

    for i, (val, label) in enumerate(stats_list):
        cell = table.cell(0, i)
        set_cell_background(cell, HEX_WARM_BG)
        set_cell_margins(cell, top=120, bottom=120, left=100, right=100)
        cell.width = col_w

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(val)
        r1.bold = True
        r1.font.name = "Calibri"
        r1.font.size = Pt(14)
        r1.font.color.rgb = GOLD_ACCENT

        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run(label)
        r2.font.name = "Calibri"
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = SLATE_TEXT

def build_docx():
    doc = docx.Document()
    
    # Page setup - 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Header / Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("IP-SAKTI Sahayak (SIH26045) | Ministry of Ayush — Commercialization & Revenue Model")
        hr.font.name = "Calibri"
        hr.font.size = Pt(8.5)
        hr.font.color.rgb = MUTED_GRAY

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run("Confidential — Smart India Hackathon 2026 Commercialization Blueprint")
        fr.font.name = "Calibri"
        fr.font.size = Pt(8.5)
        fr.font.color.rgb = MUTED_GRAY

    # Document Header Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(10)
    title_p.paragraph_format.space_after = Pt(2)
    run_badge = title_p.add_run("SMART INDIA HACKATHON 2026 | PROBLEM STATEMENT SIH26045\n")
    run_badge.font.name = "Calibri"
    run_badge.font.size = Pt(10)
    run_badge.font.bold = True
    run_badge.font.color.rgb = GOLD_ACCENT

    run_title = title_p.add_run("IP-SAKTI Sahayak: Comprehensive Revenue, Commercialization & Financial Model")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(2)
    sub_p.paragraph_format.space_after = Pt(14)
    run_sub = sub_p.add_run("Sustainable Business Architecture for India's ₹1.8 Lakh Crore Ayush Regulatory Ecosystem")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = MUTED_GRAY

    # Executive Overview Callout
    add_callout_box(
        doc,
        "IP-SAKTI Sahayak transforms herbal regulatory compliance from a slow, opaque, multi-lakh rupee barrier into an instant, deterministic, zero-hallucination workflow. By charging 85-95% less than conventional patent attorney billing while slashing processing times from months to sub-second verification, the platform unlocks high-velocity B2B SaaS subscriptions, pay-per-dossier transactional drafting, Model Context Protocol (MCP) developer APIs, an expert legal advisory marketplace, and G2G State Licensing Authority deployments.",
        title="Executive Summary & Business Proposition",
        alert_type="gold"
    )

    # Key Metrics Grid
    metrics = [
        ("₹1.8 Lakh Cr", "Target Ayush Market"),
        ("11,000+", "Licensed MSMEs"),
        ("85%+", "Cost Reduction"),
        ("₹19.4 Cr", "Year 3 ARR")
    ]
    add_stat_callout(doc, metrics)

    # SECTION 1: MARKET OPPORTUNITY & PROBLEM SOLVED
    add_styled_heading(doc, "1. Market Opportunity & Strategic Value Proposition", 1)
    
    add_body_p(doc, "India's traditional medicine sector (Ayurveda, Yoga, Naturopathy, Unani, Siddha, Sowa-Rigpa, and Homoeopathy) is undergoing rapid domestic expansion and global export growth. However, innovators face severe statutory roadblocks that prevent commercialization:", "The Ayush Patent Paradox: ")
    
    add_bullet_p(doc, "Over 70% of herbal patent applications are rejected under Section 3(p) (traditional knowledge) and Section 3(e) (mere admixture aggregation) of the Indian Patents Act, 1970.", "High Rejection Rates: ")
    add_bullet_p(doc, "Section 6 of the Biological Diversity Act, 2002 mandates prior National Biodiversity Authority (NBA) approval (Form 3) before patent filing. Non-compliance triggers criminal prosecution and up to 5 years imprisonment under Section 55.", "Criminal Liability Risk: ")
    add_bullet_p(doc, "Traditional patent law firms charge ₹40,000 to ₹1,50,000 per drafting assignment with 3 to 6-month turnaround times, pricing out 85%+ of MSMEs, grassroots Vaidyas, and academic researchers.", "Exorbitant Attorney Fees: ")
    add_bullet_p(doc, "Conflicting mandates between State Drug Licensing (Rule 158-B classical manufacturing) and Patent Office admissibility leave applicants in perpetual regulatory limbo.", "Cross-Regulatory Friction: ")

    add_body_p(doc, "IP-SAKTI Sahayak captures this massive value pool by providing deterministic, atomic clause-level legal intelligence and 1-click statutory dossier generation at a fraction of traditional costs, maintaining 76% to 85% gross margins typical of enterprise AI platforms.", "Solution & Capture: ")

    # SECTION 2: THE 5 REVENUE STREAMS
    add_styled_heading(doc, "2. Multi-Pillar Revenue Architecture (5 Streams)", 1)
    
    add_styled_heading(doc, "Stream 1: Tiered B2B SaaS Subscriptions (Recurring Revenue)", 2)
    add_body_p(doc, "Subscription tiers target the distinct needs of rural practitioners, emerging biotech startups, established corporate manufacturers, and specialized intellectual property law firms.")

    # Table: SaaS Tiers
    table1 = doc.add_table(rows=5, cols=4)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table1)

    headers1 = ["Subscription Tier", "Target Demographic", "Pricing (INR)", "Key Included Capabilities"]
    col_widths1 = [Inches(1.5), Inches(1.5), Inches(1.4), Inches(2.6)]

    hdr_cells1 = table1.rows[0].cells
    for i, title in enumerate(headers1):
        hdr_cells1[i].text = title
        set_cell_background(hdr_cells1[i], HEX_NAVY)
        set_cell_margins(hdr_cells1[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells1[i].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(9.5)
        hdr_cells1[i].width = col_widths1[i]

    tier_data = [
        ("Jan-Sahayak (Freemium)", "Rural Vaidyas, Hakims, Students, Ayush Scholars", "₹0 / month\n(Free Forever)", "Unlimited vernacular inquiries, basic TKDL Section 3(p) checks, Latin binomial translation, and official gazette citations. Cross-subsidized via CSR and government grants."),
        ("Assist Plus Tier", "Ayush Startups, R&D Labs, MSMEs, Formulation Chemists", "₹4,999 / month\n(₹49,999 / year)", "Full StateGraph multi-agent reasoning, 6-stage milestone tracker, 5 attorney-grade dossier exports/mo, global export screening (EU THMPD / FDA), priority queue."),
        ("Corporate Pharma Suite", "Established Brands (Dabur, Himalaya, Baidyanath, Charak)", "₹49,000 – ₹1,25,000 / mo\n(Custom Contract)", "Bulk formulation batch screening (50+ SKUs/run), ERP & LIMS API integrations, custom compliance dashboards, multi-seat licenses, dedicated account manager, 99.9% uptime SLA."),
        ("IP Law Firm License", "Patent Attorneys, Regulatory Consultancies", "₹19,999 / month\n(₹1,99,999 / year)", "Multi-client dossier management, prior art collision matrix exports, comparative claim drafting assistant, client-ready branded white-label compliance reports.")
    ]

    for row_idx, row_data in enumerate(tier_data, start=1):
        row_cells = table1.rows[row_idx].cells
        bg_color = HEX_LIGHT_BG if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=120, right=120)
            p = row_cells[col_idx].paragraphs[0]
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9)
            p.runs[0].font.color.rgb = SLATE_TEXT
            row_cells[col_idx].width = col_widths1[col_idx]

    add_body_p(doc, "", space_after=6)

    # Stream 2: Pay-Per-Use
    add_styled_heading(doc, "Stream 2: Transactional Pay-Per-Dossier Synthesis (A La Carte)", 2)
    add_body_p(doc, "Designed for micro-entrepreneurs and episodic filers who require formal statutory filings without committing to a recurring monthly subscription.")

    table2 = doc.add_table(rows=5, cols=4)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table2)

    headers2 = ["Statutory Filing Dossier", "Typical Legal Market Fee", "IP-SAKTI Fee", "Customer Cost Savings"]
    col_widths2 = [Inches(2.5), Inches(1.5), Inches(1.3), Inches(1.7)]

    for i, title in enumerate(headers2):
        cell = table2.rows[0].cells[i]
        cell.text = title
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(9.5)
        cell.width = col_widths2[i]

    dossier_data = [
        ("Complete Patent Draft (IPO Form 1 & 2 + Claims + Synergism Brief)", "₹40,000 – ₹75,000", "₹2,499", "95% Savings"),
        ("NBA Form 3 Biodiversity Prior Approval Dossier Package", "₹20,000 – ₹35,000", "₹1,499", "94% Savings"),
        ("Rule 158-B State Ayush Drug Licensing Dossier (GMP Schedule T)", "₹25,000 – ₹50,000", "₹2,999", "92% Savings"),
        ("Global Export Dossier (EU THMPD 15-Yr Evidence / US FDA DSHEA)", "₹50,000 – ₹1,00,000", "₹4,999", "93% Savings")
    ]

    for row_idx, row_data in enumerate(dossier_data, start=1):
        row_cells = table2.rows[row_idx].cells
        bg_color = HEX_LIGHT_BG if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=120, right=120)
            p = row_cells[col_idx].paragraphs[0]
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9)
            p.runs[0].font.color.rgb = SUCCESS_GREEN if col_idx == 3 else SLATE_TEXT
            if col_idx in [2, 3]:
                p.runs[0].font.bold = True
            row_cells[col_idx].width = col_widths2[col_idx]

    add_body_p(doc, "", space_after=6)

    # Stream 3: MCP API
    add_styled_heading(doc, "Stream 3: Model Context Protocol (MCP) API & Developer Infrastructure", 2)
    add_body_p(doc, "IP-SAKTI Sahayak exposes its 6 atomic legal verification tools as an open Model Context Protocol (MCP) server. External developer agents, enterprise legal tools, and pharma analytics suites can call atomic tools programmatically:", "API Monetization: ")
    add_bullet_p(doc, "Third-party agents (Claude Desktop, Cursor, Custom LLMs) connect via stdio or HTTP to run botanical entity recognition and pharmacopoeial cross-checks at ₹2.50 per tool execution.", "Micro-Transactions (Usage-Based): ")
    add_bullet_p(doc, "₹9,999/month includes 5,000 API calls, sandbox testing environment, and dedicated API key management. Extra calls at ₹1.50/call.", "Developer Growth Bundle: ")
    add_bullet_p(doc, "₹45,000/month for high-volume enterprise users (IP search engines like PatSnap, Clarivate Derwent) requiring direct access to Indian Gazette hashes and traditional knowledge indices.", "Enterprise Data Pipeline: ")

    # Stream 4: Marketplace
    add_styled_heading(doc, "Stream 4: Accredited Statutory Mentorship Marketplace (Commission Take-Rate)", 2)
    add_body_p(doc, "While AI automates 90% of drafting and statutory cross-checks, users frequently require final human verification and strategic representation before the Controller General of Patents or NBA Committees.")
    add_bullet_p(doc, "Former CGPDTM Patent Controllers, Senior Ayush IP Attorneys, and National Biodiversity Authority committee members are empaneled.", "Empaneled Registry: ")
    add_bullet_p(doc, "Inventors book 30 to 60-minute video consultations directly through the integrated calendar system at ₹5,000 to ₹15,000 per consultation.", "Session Fee Structure: ")
    add_bullet_p(doc, "IP-SAKTI Sahayak retains a 20% platform commission on all completed sessions and legal document reviews, generating ₹1,000 to ₹3,000 in pure margin per booking.", "Platform Take-Rate (20%): ")

    # Stream 5: B2G
    add_styled_heading(doc, "Stream 5: B2G Institutional Licensing & State Government Deployment", 2)
    add_body_p(doc, "State Ayush Licensing Authorities (SALA) across 28 states and 8 UTs are overwhelmed with paper and e-Aushadhi licensing applications under Rule 158-B, creating massive 6 to 12-month backlogs.")
    add_bullet_p(doc, "Automated pre-screening of classical vs. patent/proprietary ASU drug applications for state drug inspectors.", "SALA Ingestion Triage Engine: ")
    add_bullet_p(doc, "₹15 Lakh to ₹25 Lakh annual maintenance contract (AMC) per state authority, including sovereign on-premise or NIC MeghRaj deployment.", "Annual License Fee: ")
    add_bullet_p(doc, "Central dashboard for the Ministry of Ayush and National Biodiversity Authority to monitor commercialization compliance and benefit-sharing compliance across all registered manufacturers.", "Central Ministry Governance Portal: ")

    # SECTION 3: UNIT ECONOMICS
    add_styled_heading(doc, "3. Unit Economics & Customer Lifetime Value (LTV / CAC)", 1)
    
    add_body_p(doc, "The software-driven architecture exhibits best-in-class unit economics due to low inference costs, reusable atomic clause indices, and high customer retention in a mandatory regulatory compliance domain.")

    table3 = doc.add_table(rows=6, cols=3)
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table3)

    headers3 = ["Financial & Unit Metric", "Assist Plus Tier (MSME / Startup)", "Corporate Pharma Suite (Enterprise)"]
    col_widths3 = [Inches(2.5), Inches(2.2), Inches(2.3)]

    for i, title in enumerate(headers3):
        cell = table3.rows[0].cells[i]
        cell.text = title
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(9.5)
        cell.width = col_widths3[i]

    econ_data = [
        ("Customer Acquisition Cost (CAC)", "₹4,200 (Digital Ayush webinars & incubators)", "₹38,000 (Direct B2B account executives)"),
        ("Average Revenue Per User (ARPU)", "₹4,999 / month", "₹65,000 / month"),
        ("Customer Lifetime (Average)", "18 Months (Continuous R&D lifecycle)", "24 Months (Annual enterprise commitments)"),
        ("Lifetime Value (LTV)", "₹74,990 (Net of hosting)", "₹9,50,000 (Net of support & SLA)"),
        ("LTV : CAC Ratio", "17.8 : 1 (Exceptional SaaS Health)", "25 : 1 (Enterprise Category Leader)")
    ]

    for row_idx, row_data in enumerate(econ_data, start=1):
        row_cells = table3.rows[row_idx].cells
        bg_color = HEX_LIGHT_BG if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=120, right=120)
            p = row_cells[col_idx].paragraphs[0]
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9)
            p.runs[0].font.color.rgb = SLATE_TEXT
            if col_idx == 0:
                p.runs[0].font.bold = True
            row_cells[col_idx].width = col_widths3[col_idx]

    add_body_p(doc, "", space_after=6)

    # SECTION 4: 3-YEAR FINANCIAL PROJECTIONS
    add_styled_heading(doc, "4. 3-Year Financial Forecast & P&L Snapshot", 1)
    add_body_p(doc, "Conservative financial projections based on capturing less than 3% of India's 11,000+ registered Ayush manufacturing units and 5,000+ herbal research scholars by Year 3:")

    table4 = doc.add_table(rows=9, cols=4)
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table4)

    headers4 = ["Financial Performance Line", "Year 1 (Launch & Pilot)", "Year 2 (National Scale)", "Year 3 (Market Leader)"]
    col_widths4 = [Inches(2.5), Inches(1.5), Inches(1.5), Inches(1.5)]

    for i, title in enumerate(headers4):
        cell = table4.rows[0].cells[i]
        cell.text = title
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(9.5)
        cell.width = col_widths4[i]

    pnl_data = [
        ("Registered Free Users", "15,000 Practitioners", "65,000 Practitioners", "2,00,000+ Practitioners"),
        ("Assist Plus Subscribers", "350 Accounts", "1,400 Accounts", "4,500 Accounts"),
        ("Enterprise Pharma Clients", "12 Manufacturers", "45 Manufacturers", "120 Manufacturers"),
        ("State Licensing Authorities (SALA)", "1 Pilot State", "4 State Authorities", "12 State Authorities"),
        ("Gross Revenue (ARR)", "₹ 1.62 Crore", "₹ 6.85 Crore", "₹ 19.40 Crore"),
        ("Hosting & LLM Inference (COGS)", "₹ 38.8 Lakh (24%)", "₹ 1.23 Crore (18%)", "₹ 2.91 Crore (15%)"),
        ("Gross Profit Margin", "76% Margin", "82% Margin", "85% Margin"),
        ("Net Operating Profit (EBITDA)", "₹ 48.6 Lakh (30%)", "₹ 2.87 Crore (42%)", "₹ 9.31 Crore (48%)")
    ]

    for row_idx, row_data in enumerate(pnl_data, start=1):
        row_cells = table4.rows[row_idx].cells
        bg_color = HEX_WARM_BG if row_idx in [5, 8] else (HEX_LIGHT_BG if row_idx % 2 == 1 else "FFFFFF")
        for col_idx, text in enumerate(row_data):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=90, bottom=90, left=110, right=110)
            p = row_cells[col_idx].paragraphs[0]
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9)
            p.runs[0].font.color.rgb = NAVY_PRIMARY if row_idx in [5, 8] else SLATE_TEXT
            if row_idx in [5, 8] or col_idx == 0:
                p.runs[0].font.bold = True
            row_cells[col_idx].width = col_widths4[col_idx]

    add_body_p(doc, "", space_after=6)

    # SECTION 5: COST STRUCTURE & BREAK-EVEN
    add_styled_heading(doc, "5. Cost Structure (OpEx) & Break-Even Analysis", 1)
    
    add_bullet_p(doc, "MeghRaj Government Cloud / sovereign GPU clusters (NVIDIA A10G/A100 instances), Qdrant vector database, and high-availability endpoints represent ~18-24% of operational expenses.", "Cloud Compute & Model Hosting (22%): ")
    add_bullet_p(doc, "Continuous automated web crawlers and sentinel nodes scraping central and state gazettes, PCIM&H pharmacopoeias, and WIPO treaties represent ~18% of OpEx.", "Legal Grounding & Gazette Verification (18%): ")
    add_bullet_p(doc, "Core engineering team developing StateGraph pipelines, vernacular normalizers, and security compliance protocols represents ~30% of OpEx.", "Software Engineering & AI R&D (30%): ")
    add_bullet_p(doc, "Sponsorship of flagship events (World Ayurveda Congress, Global Ayush Investment Summit) and direct partnership with Ayush incubation centers (AIIA, NIPER, CCRAS) represents ~20% of OpEx.", "Marketing, Industry Partnerships & Conferences (20%): ")
    add_bullet_p(doc, "The business achieves monthly cash-flow break-even at approximately 180 Assist Plus Tier subscribers and 4 Enterprise clients (estimated Month 7 post-launch).", "Break-Even Milestone: ")

    # SECTION 6: GO-TO-MARKET ROADMAP
    add_styled_heading(doc, "6. Go-To-Market (GTM) & Adoption Strategy", 1)
    
    add_body_p(doc, "The commercialization strategy leverages a low-friction institutional land-and-expand motion:", "Three-Stage GTM Roadmap: ")
    add_bullet_p(doc, "Distribute the free Jan-Sahayak tier across 15+ premier Ayush institutions (All India Institute of Ayurveda, National Institute of Unani Medicine, National Institute of Siddha, ITRA Jamnagar) to establish immediate credibility and viral adoption among 25,000+ researchers and students.", "Phase 1 (Month 1 – 6): Institutional Seed & Academic Moat: ")
    add_bullet_p(doc, "Partner with regional Ayush manufacturing associations (ADMA, PHARMEXCIL) and MSME clusters in Gujarat, Kerala, Maharashtra, and Uttarakhand to convert high-volume manufacturers to the Assist Plus and Corporate tiers.", "Phase 2 (Month 7 – 18): MSME & Corporate Conversion: ")
    add_bullet_p(doc, "Deploy white-labeled SALA modules in 4 progressive state governments (e.g. Kerala, Gujarat, Karnataka) and license MCP tools to global herbal export syndicates navigating European THMPD and US FDA regulations.", "Phase 3 (Month 19 – 36): State Licensing (SALA) & Global Export Hub: ")

    # Strategic Conclusion Callout
    add_callout_box(
        doc,
        "IP-SAKTI Sahayak is not merely an advisory AI chatbot; it is a foundational Regulatory Operating System for India's ₹1.8 Lakh Crore traditional medicine economy. By disintermediating exorbitant legal costs and automating compliance through verifiable gazette grounding, it achieves high SaaS profitability (80%+ gross margins) while driving immense national impact — democratizing intellectual property protection for grassroots innovators across India.",
        title="Strategic Takeaway for SIH Jury & Investors",
        alert_type="gold"
    )

    doc.save(DOCX_PATH)
    print(f"✅ Executive Word document saved successfully to: {DOCX_PATH}")

def build_markdown():
    content = """# IP-SAKTI Sahayak: Comprehensive Revenue, Commercialization & Financial Model
**Smart India Hackathon 2026 | Problem Statement ID: SIH26045**  
**Sponsoring Ministry:** Ministry of Ayush, Government of India  
**Project Title:** Evidence-First Regulatory Intelligence & Automated Legal Co-Pilot  

---

## Executive Summary & Business Proposition

IP-SAKTI Sahayak transforms herbal regulatory compliance from a slow, opaque, multi-lakh rupee barrier into an instant, deterministic, zero-hallucination workflow. By charging **85% to 95% less** than conventional patent attorneys while slashing processing times from 3-6 months to sub-80ms verification, the platform unlocks high-velocity B2B SaaS subscriptions, pay-per-dossier transactional drafting, Model Context Protocol (MCP) developer APIs, an expert legal advisory marketplace, and G2G State Licensing Authority deployments.

### Key Business Metrics
- **Target Ayush Market Size:** ₹1.8 Lakh Crore ($24 Billion)
- **Licensed Manufacturing MSMEs:** 11,000+ registered units in India
- **Customer Cost Savings:** 85% - 95% reduction vs. traditional law firms
- **Projected Year 3 ARR:** ₹19.40 Crore with 85% gross margins

---

## 1. Market Opportunity & The Problem Solved

### The Ayush Patent Paradox
- **High Rejection Rates:** Over 70% of herbal patent applications are rejected under Section 3(p) (traditional knowledge) and Section 3(e) (mere admixture aggregation) of the Indian Patents Act, 1970.
- **Criminal Liability Risk:** Section 6 of the Biological Diversity Act, 2002 mandates prior National Biodiversity Authority (NBA) approval (Form 3) before patent filing. Non-compliance triggers criminal prosecution and up to 5 years imprisonment under Section 55.
- **Exorbitant Attorney Fees:** Traditional patent law firms charge ₹40,000 to ₹1,50,000 per drafting assignment with 3 to 6-month turnaround times, pricing out 85%+ of MSMEs, grassroots Vaidyas, and academic researchers.
- **Cross-Regulatory Contradictions:** Conflicting mandates between State Drug Licensing (Rule 158-B classical manufacturing) and Patent Office admissibility leave applicants in perpetual regulatory limbo.

---

## 2. Multi-Pillar Revenue Architecture (5 Streams)

```
                            IP-SAKTI REVENUE ENGINE
                                      │
    ┌────────────────┬────────────────┼────────────────┬────────────────┐
    ▼                ▼                ▼                ▼                ▼
1. Tiered B2B   2. Pay-Per-Doc   3. MCP API &     4. Mentor Legal  5. B2G State
   SaaS Sub        Synthesis        Dev Tools        Marketplace      SALA Licensing
   (Assist Plus)   (A La Carte)     (Usage-Based)    (20% Take)       (Govt. AMC)
```

### Stream 1: Tiered B2B SaaS Subscriptions (Recurring Revenue)

| Subscription Tier | Target Demographic | Pricing (INR) | Key Included Capabilities |
| :--- | :--- | :--- | :--- |
| **Jan-Sahayak (Freemium)** | Rural Vaidyas, Hakims, Students, Ayush Scholars | **₹0 / month**<br>*(Free Forever)* | Unlimited vernacular inquiries, basic TKDL Section 3(p) checks, Latin binomial translation, and official gazette citations. Cross-subsidized via CSR and government grants. |
| **Assist Plus Tier** | Ayush Startups, R&D Labs, MSMEs, Formulation Chemists | **₹4,999 / month**<br>*(₹49,999 / year)* | Full StateGraph multi-agent reasoning, 6-stage milestone tracker, 5 attorney-grade dossier exports/mo, global export screening (EU THMPD / FDA), priority queue. |
| **Corporate Pharma Suite** | Established Brands (Dabur, Himalaya, Baidyanath, Charak) | **₹49,000 – ₹1,25,000 / mo**<br>*(Annual Contract)* | Bulk formulation batch screening (50+ SKUs/run), ERP & LIMS API integrations, custom compliance dashboards, multi-seat licenses, dedicated account manager, 99.9% uptime SLA. |
| **IP Law Firm License** | Patent Attorneys, Regulatory Consultancies | **₹19,999 / month**<br>*(₹1,99,999 / year)* | Multi-client dossier management, prior art collision matrix exports, comparative claim drafting assistant, client-ready branded white-label compliance reports. |

---

### Stream 2: Transactional Pay-Per-Dossier Synthesis (A La Carte)

Designed for micro-entrepreneurs and episodic filers who require formal statutory filings without committing to a recurring monthly subscription:

| Statutory Filing Dossier | Typical Legal Market Fee | IP-SAKTI Fee | Customer Cost Savings |
| :--- | :--- | :--- | :--- |
| **Complete Patent Draft (IPO Form 1 & 2 + Claims + Synergism Brief)** | ₹40,000 – ₹75,000 | **₹2,499** | **95% Savings** |
| **NBA Form 3 Biodiversity Prior Approval Dossier Package** | ₹20,000 – ₹35,000 | **₹1,499** | **94% Savings** |
| **Rule 158-B State Ayush Drug Licensing Dossier (GMP Schedule T)** | ₹25,000 – ₹50,000 | **₹2,999** | **92% Savings** |
| **Global Export Dossier (EU THMPD 15-Yr Evidence / US FDA DSHEA)** | ₹50,000 – ₹1,00,000 | **₹4,999** | **93% Savings** |

---

### Stream 3: Model Context Protocol (MCP) API & Developer Infrastructure

IP-SAKTI Sahayak exposes its 6 atomic legal verification tools as an open Model Context Protocol (MCP) server. External developer agents, enterprise legal tools, and pharma analytics suites can call atomic tools programmatically:
- **Micro-Transactions (Usage-Based):** Third-party agents (Claude Desktop, Cursor, Custom LLMs) connect via stdio or HTTP to run botanical entity recognition and pharmacopoeial cross-checks at **₹2.50 per tool execution**.
- **Developer Growth Bundle:** **₹9,999 / month** includes 5,000 API calls, sandbox testing environment, and dedicated API key management. Extra calls at ₹1.50/call.
- **Enterprise Data Pipeline:** **₹45,000 / month** for high-volume enterprise users (IP search engines like PatSnap, Clarivate Derwent) requiring direct access to Indian Gazette hashes and traditional knowledge indices.

---

### Stream 4: Accredited Statutory Mentorship Marketplace (Commission Take-Rate)

While AI automates 90% of drafting and statutory cross-checks, users frequently require final human verification and strategic representation before the Controller General of Patents or NBA Committees:
- **Empaneled Registry:** Former CGPDTM Patent Controllers, Senior Ayush IP Attorneys, and National Biodiversity Authority committee members are empaneled.
- **Session Fee Structure:** Inventors book 30 to 60-minute video consultations directly through the integrated calendar system at **₹5,000 to ₹15,000 per consultation**.
- **Platform Take-Rate (20%):** IP-SAKTI Sahayak retains a **20% platform commission** on all completed sessions and legal document reviews, generating ₹1,000 to ₹3,000 in pure margin per booking.

---

### Stream 5: B2G Institutional Licensing & State Government Deployment

State Ayush Licensing Authorities (SALA) across 28 states and 8 UTs are overwhelmed with paper and e-Aushadhi licensing applications under Rule 158-B, creating massive 6 to 12-month backlogs:
- **SALA Ingestion Triage Engine:** Automated pre-screening of classical vs. patent/proprietary ASU drug applications for state drug inspectors.
- **Annual License Fee:** **₹15 Lakh to ₹25 Lakh** annual maintenance contract (AMC) per state authority, including sovereign on-premise or NIC MeghRaj deployment.
- **Central Ministry Governance Portal:** Central dashboard for the Ministry of Ayush and National Biodiversity Authority to monitor commercialization compliance and benefit-sharing compliance across all registered manufacturers.

---

## 3. Unit Economics & Customer Lifetime Value (LTV / CAC)

| Financial & Unit Metric | Assist Plus Tier (MSME / Startup) | Corporate Pharma Suite (Enterprise) |
| :--- | :--- | :--- |
| **Customer Acquisition Cost (CAC)** | ₹4,200 *(Webinars, Ayush incubators)* | ₹38,000 *(Direct B2B account executives)* |
| **Average Revenue Per User (ARPU)** | ₹4,999 / month | ₹65,000 / month |
| **Customer Lifetime (Average)** | 18 Months *(Continuous R&D lifecycle)* | 24 Months *(Annual enterprise commitments)* |
| **Lifetime Value (LTV)** | ₹74,990 *(Net of hosting & API costs)* | ₹9,50,000 *(Net of support & SLA)* |
| **LTV : CAC Ratio** | **17.8 : 1** *(Exceptional SaaS Health)* | **25 : 1** *(Enterprise Category Leader)* |
| **Payback Period** | **< 1 Month** | **< 1 Month** |

---

## 4. 3-Year Financial Forecast & P&L Snapshot

| Financial Performance Line | Year 1 (Launch & Pilot) | Year 2 (National Scale) | Year 3 (Market Leader) |
| :--- | :--- | :--- | :--- |
| **Registered Free Users** | 15,000 Practitioners | 65,000 Practitioners | 2,00,000+ Practitioners |
| **Assist Plus Subscribers** | 350 Accounts | 1,400 Accounts | 4,500 Accounts |
| **Enterprise Pharma Clients** | 12 Manufacturers | 45 Manufacturers | 120 Manufacturers |
| **State Licensing Authorities (SALA)** | 1 Pilot State | 4 State Authorities | 12 State Authorities |
| **Gross Revenue (ARR)** | **₹ 1.62 Crore** | **₹ 6.85 Crore** | **₹ 19.40 Crore** |
| **Hosting & LLM Inference (COGS)** | ₹ 38.8 Lakh *(24%)* | ₹ 1.23 Crore *(18%)* | ₹ 2.91 Crore *(15%)* |
| **Gross Profit Margin** | **76% Margin** | **82% Margin** | **85% Margin** |
| **Net Operating Profit (EBITDA)** | **₹ 48.6 Lakh (30%)** | **₹ 2.87 Crore (42%)** | **₹ 9.31 Crore (48%)** |

---

## 5. Cost Structure (OpEx) & Break-Even Analysis

1. **Cloud Compute & Model Hosting (22%):** MeghRaj Government Cloud / sovereign GPU clusters (NVIDIA A10G/A100 instances), Qdrant vector database, and high-availability endpoints represent ~18-24% of operational expenses.
2. **Legal Grounding & Gazette Verification (18%):** Continuous automated web crawlers and sentinel nodes scraping central and state gazettes, PCIM&H pharmacopoeias, and WIPO treaties represent ~18% of OpEx.
3. **Software Engineering & AI R&D (30%):** Core engineering team developing StateGraph pipelines, vernacular normalizers, and security compliance protocols represents ~30% of OpEx.
4. **Marketing, Industry Partnerships & Conferences (20%):** Sponsorship of flagship events (World Ayurveda Congress, Global Ayush Investment Summit) and direct partnership with Ayush incubation centers (AIIA, NIPER, CCRAS) represents ~20% of OpEx.
5. **Break-Even Milestone:** The business achieves monthly cash-flow break-even at approximately **180 Assist Plus subscribers and 4 Enterprise clients** (estimated Month 7 post-launch).

---

## 6. Go-To-Market (GTM) & Adoption Strategy

- **Phase 1 (Month 1 – 6): Institutional Seed & Academic Moat:** Distribute the free Jan-Sahayak tier across 15+ premier Ayush institutions (All India Institute of Ayurveda, National Institute of Unani Medicine, National Institute of Siddha, ITRA Jamnagar) to establish immediate credibility and viral adoption among 25,000+ researchers and students.
- **Phase 2 (Month 7 – 18): MSME & Corporate Conversion:** Partner with regional Ayush manufacturing associations (ADMA, PHARMEXCIL) and MSME clusters in Gujarat, Kerala, Maharashtra, and Uttarakhand to convert high-volume manufacturers to the Assist Plus and Corporate tiers.
- **Phase 3 (Month 19 – 36): State Licensing (SALA) & Global Export Hub:** Deploy white-labeled SALA modules in 4 progressive state governments (e.g. Kerala, Gujarat, Karnataka) and license MCP tools to global herbal export syndicates navigating European THMPD and US FDA regulations.

---

## Strategic Takeaway for SIH Jury & Investors

> *"IP-SAKTI Sahayak is not merely an advisory AI chatbot; it is a foundational Regulatory Operating System for India's ₹1.8 Lakh Crore traditional medicine economy. By disintermediating exorbitant legal costs and automating compliance through verifiable gazette grounding, it achieves high SaaS profitability (80%+ gross margins) while driving immense national impact — democratizing intellectual property protection for grassroots innovators across India."*
"""

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ Executive Markdown document saved successfully to: {MD_PATH}")

if __name__ == "__main__":
    build_docx()
    build_markdown()
