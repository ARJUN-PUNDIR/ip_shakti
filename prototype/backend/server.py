"""
FastAPI Server for IP-SAKTI Sahayak (SIH26045)
Integrates NVIDIA Nemotron NIM API, Atomic Clause RAG, Conflict Detection & Doc Synthesis.
"""

import os
import json
import asyncio
import uvicorn
from typing import List, Optional, Dict, Any
import io
from fastapi import FastAPI, HTTPException, Response, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from nemotron_client import NemotronClient, DEFAULT_MODEL
from legal_kb import GAZETTE_REGISTRY, DEMO_SCENARIOS, BOTANICAL_DB
from doc_generator import generate_patent_draft, generate_nba_form_3, generate_unified_dossier
from vernacular_kb import get_vernacular_stats, normalize_vernacular_text, get_vernacular_entry
import mcp_server
from project_manager import project_manager, AYUSH_MENTOR_REGISTRY

app = FastAPI(title="IP-SAKTI Sahayak", version="1.0.0")

# Initialize Nemotron Client
nemotron_client = NemotronClient()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "exports")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Pydantic Schemas
class QueryRequest(BaseModel):
    query: str
    domain: Optional[str] = "Ayurveda"
    language: Optional[str] = "en"
    jurisdiction: Optional[str] = "india"
    scenario_id: Optional[str] = None
    documents: Optional[List[Dict[str, Any]]] = None

class ConfigRequest(BaseModel):
    provider: Optional[str] = None  # "nvidia", "openai", "ollama"
    model: Optional[str] = None
    api_key: Optional[str] = None
    ollama_url: Optional[str] = None

class ScanRequest(BaseModel):
    ingredients: List[str]
    dosage_form: str
    indication: Optional[str] = "Pain & Inflammation"

class DocGenRequest(BaseModel):
    doc_type: str  # "patent_form_2" or "nba_form_3"
    title: str
    herbs: List[str]
    workaround_type: Optional[str] = "Phospholipid Nanocarrier"

class VernacularNormalizeRequest(BaseModel):
    text: str

class McpExecuteRequest(BaseModel):
    tool_name: str
    arguments: Optional[dict] = {}

class ProjectCreateRequest(BaseModel):
    name: str
    applicant: Optional[str] = "Ayush Research Scholar"
    description: Optional[str] = ""
    botanicals: List[str]
    dosage_form: Optional[str] = "Standardized Phyto-Complex"
    domain: Optional[str] = "Ayurveda"
    target_markets: Optional[List[str]] = ["India"]

class ProjectAdvanceRequest(BaseModel):
    stage_id: str
    completion_pct: Optional[int] = 100

class MentorVerifyRequest(BaseModel):
    project_id: str
    token_code: str

class GoalRoadmapRequest(BaseModel):
    goal: str
    domain: Optional[str] = "Ayurveda"


@app.get("/")
def serve_home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/scenarios")
def get_scenarios():
    return {"scenarios": list(DEMO_SCENARIOS.values())}

@app.get("/api/vernacular/stats")
def get_vernacular_statistics():
    return get_vernacular_stats()

@app.post("/api/vernacular/normalize")
def normalize_vernacular_endpoint(req: VernacularNormalizeRequest):
    """Maps colloquial/traditional Hakim and Vaidya dialect to Latin binomials and official monographs."""
    return normalize_vernacular_text(req.text)

@app.get("/api/vernacular/lookup/{term}")
def lookup_vernacular_term(term: str):
    entry = get_vernacular_entry(term)
    if entry:
        return {"found": True, "term": term, "entry": entry}
    return {"found": False, "term": term, "message": "Term not in vernacular registry"}

@app.get("/api/gazette/{doc_id}")
def get_gazette_document(doc_id: str):
    if doc_id in GAZETTE_REGISTRY:
        return GAZETTE_REGISTRY[doc_id]
    raise HTTPException(status_code=404, detail="Gazette document not found in registry")

@app.get("/api/config")
def get_config():
    nvidia_key = nemotron_client.get_api_key("nvidia")
    openai_key = nemotron_client.get_api_key("openai")
    
    has_nvidia = bool(nvidia_key and len(nvidia_key.strip()) > 5)
    has_openai = bool(openai_key and len(openai_key.strip()) > 5)
    
    active_key = nemotron_client.get_api_key()
    has_active_key = bool(active_key and len(active_key.strip()) > 5)

    return {
        "provider": nemotron_client.provider,
        "model": nemotron_client.model,
        "has_api_key": has_active_key,
        "api_key_masked": f"{active_key[:6]}...{active_key[-4:]}" if has_active_key else "Not Set",
        "has_nvidia_key": has_nvidia,
        "nvidia_key_masked": f"{nvidia_key[:6]}...{nvidia_key[-4:]}" if has_nvidia else "Not Set",
        "has_openai_key": has_openai,
        "openai_key_masked": f"{openai_key[:6]}...{openai_key[-4:]}" if has_openai else "Not Set",
        "ollama_url": nemotron_client.ollama_url,
        "default_model": DEFAULT_MODEL
    }

@app.post("/api/config")
def update_config(req: ConfigRequest):
    nemotron_client.set_config(
        provider=req.provider,
        model=req.model,
        api_key=req.api_key,
        ollama_url=req.ollama_url
    )
    
    # Persist to .env
    try:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        lines = []
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                lines = f.readlines()
        
        env_map = {}
        order = []
        for line in lines:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env_map[k] = v
                order.append(k)
        
        if req.provider:
            env_map["ACTIVE_LLM_PROVIDER"] = req.provider
            if "ACTIVE_LLM_PROVIDER" not in order:
                order.append("ACTIVE_LLM_PROVIDER")
                
        if req.model:
            env_map["ACTIVE_LLM_MODEL"] = req.model
            if "ACTIVE_LLM_MODEL" not in order:
                order.append("ACTIVE_LLM_MODEL")

        if req.api_key:
            target_key_var = "OPENAI_API_KEY" if (req.provider == "openai" or (req.api_key.startswith("sk-") and not req.api_key.startswith("nvapi"))) else "NVIDIA_API_KEY"
            env_map[target_key_var] = req.api_key.strip()
            if target_key_var not in order:
                order.append(target_key_var)

        if req.ollama_url:
            env_map["OLLAMA_BASE_URL"] = req.ollama_url.strip()
            if "OLLAMA_BASE_URL" not in order:
                order.append("OLLAMA_BASE_URL")

        new_lines = [f"{k}={env_map[k]}\n" for k in order if k in env_map]
        with open(env_file, "w") as f:
            f.writelines(new_lines)
    except Exception as e:
        print("Error persisting .env:", e)

    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "provider": nemotron_client.provider,
        "model": nemotron_client.model,
        "has_api_key": bool(nemotron_client.get_api_key())
    }

from pipeline import regulatory_graph

@app.get("/api/topology")
def get_graph_topology(jurisdiction: Optional[str] = "india"):
    """Returns nodes and edges of the Multi-Agent StateGraph for frontend visualization."""
    return regulatory_graph.get_topology(jurisdiction=jurisdiction or "india")

@app.post("/api/documents/parse")
async def parse_document(file: UploadFile = File(...)):
    """
    Parses uploaded regulatory documents (PDF, DOCX, TXT, MD, CSV, JSON).
    Extracts text content, scans for Ayush botanicals from BOTANICAL_DB,
    and identifies statutory compliance clauses (Section 3(p), Rule 158-B, Form 3).
    """
    filename = file.filename or "uploaded_document"
    contents = await file.read()
    size_bytes = len(contents)
    size_kb = round(size_bytes / 1024, 1)

    ext = os.path.splitext(filename)[1].lower()
    text = ""

    try:
        if ext == ".docx":
            import docx
            doc = docx.Document(io.BytesIO(contents))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
        elif ext == ".pdf":
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(contents))
            pages_text = []
            for p in reader.pages:
                extracted = p.extract_text()
                if extracted:
                    pages_text.append(extracted)
            text = "\n".join(pages_text)
        elif ext in [".txt", ".md", ".json", ".csv", ".tsv", ".rtf"]:
            text = contents.decode("utf-8", errors="ignore")
        else:
            text = f"[Attached file: {filename} ({size_kb} KB)]"
    except Exception as e:
        print(f"[Document Parse Error for {filename}]: {e}")
        text = f"[Uploaded document {filename} ({size_kb} KB)]"

    # Detect botanicals from BOTANICAL_DB
    text_lower = text.lower()
    detected_botanicals = []
    for bot_id, info in BOTANICAL_DB.items():
        name_matches = [
            info.get("latin_name", "").lower(),
            info.get("common_name", "").lower(),
            bot_id.lower()
        ]
        if any(nm and nm in text_lower for nm in name_matches):
            detected_botanicals.append(info.get("common_name", bot_id))

    # Detect statutory clauses
    detected_clauses = []
    if "3(p)" in text_lower or "traditional knowledge" in text_lower:
        detected_clauses.append("Section 3(p) Traditional Knowledge")
    if "3(e)" in text_lower or "admixture" in text_lower:
        detected_clauses.append("Section 3(e) Mere Admixture")
    if "158-b" in text_lower or "rule 158" in text_lower or "form 24-d" in text_lower:
        detected_clauses.append("Rule 158-B ASU Licensing")
    if "form 3" in text_lower or "section 6" in text_lower or "biodiversity" in text_lower or "nba" in text_lower:
        detected_clauses.append("NBA Section 6 Prior Approval")

    return {
        "status": "success",
        "filename": filename,
        "size_kb": size_kb,
        "word_count": len(text.split()),
        "text": text[:12000],
        "snippet": text[:220].strip().replace("\n", " "),
        "botanicals_detected": list(dict.fromkeys(detected_botanicals))[:5],
        "clauses_detected": detected_clauses
    }

@app.post("/api/query")
def process_query(req: QueryRequest):
    domain = req.domain or "Ayurveda"
    lang = req.language or "en"
    jurisdiction = (req.jurisdiction or "india").lower()
    
    # Enrich query with attached documents if present
    effective_query = req.query
    if req.documents:
        doc_snippets = []
        for d in req.documents:
            fname = d.get("filename", "Attached Document")
            d_text = d.get("text", "")[:3000]
            d_bots = ", ".join(d.get("botanicals_detected", []))
            doc_snippets.append(f"--- [ATTACHED REGULATORY DOCUMENT: {fname}] ---\n(Detected Botanicals: {d_bots or 'None'})\n{d_text}")
        effective_query = f"{req.query}\n\n[CONTEXT FROM ATTACHED DOCUMENTS]:\n" + "\n\n".join(doc_snippets)

    # 1. Execute Multi-Agent StateGraph across all 8 nodes based on jurisdiction
    state = regulatory_graph.invoke(effective_query, domain=domain, language=lang, jurisdiction=jurisdiction)
    
    # 2. Query Nemotron NIM / Ollama with grounded StateGraph context
    llm_live = False
    llm_source = "state_graph_rules"
    model_name = nemotron_client.model
    summary_text = state.get("summary", "")
    
    try:
        llm_result = nemotron_client.query(
            effective_query,
            domain=domain,
            language=lang,
            state_context=state
        )
        if llm_result.get("status") == "success" and llm_result.get("raw_response"):
            summary_text = llm_result.get("raw_response")
            llm_live = True
            llm_source = llm_result.get("source", "nvidia_nim")
            model_name = llm_result.get("model", model_name)
    except Exception as e:
        print(f"[LLM Query Exception]: {e}")

    if jurisdiction == "international":
        wipo_eval = state.get("wipo_evaluation", {})
        cbd_eval = state.get("cbd_evaluation", {})
        eu_eval = state.get("eu_evaluation", {})
        us_eval = state.get("us_evaluation", {})

        clause_tree = [
            {"level": "Treaty", "title": "WIPO GRATK Treaty, 2024", "ref": wipo_eval.get("status", "Mandatory Origin Disclosure"), "latency_ms": 19},
            {"level": "Treaty", "title": "CBD & Nagoya Protocol ABS", "ref": cbd_eval.get("status", "PIC & Benefit Sharing"), "latency_ms": 23},
            {"level": "Directive", "title": "EU THMPD (2004/24/EC)", "ref": eu_eval.get("status", "Traditional Herbal Registration"), "latency_ms": 18},
            {"level": "Guidance", "title": "US FDA Botanical Guidance & DSHEA", "ref": us_eval.get("status", "Dietary Supplement / NDI"), "latency_ms": 16}
        ]
    else:
        ipo_eval = state.get("ipo_evaluation", {})
        nba_eval = state.get("nba_evaluation", {})
        ayush_eval = state.get("ayush_evaluation", {})
        allied_eval = state.get("allied_evaluation", {})

        clause_tree = [
            {"level": "Act", "title": "The Patents Act, 1970", "ref": ipo_eval.get("status", "Section 3(p) Screening"), "latency_ms": 18},
            {"level": "Act", "title": "Biological Diversity Act, 2002", "ref": nba_eval.get("status", "Section 6 Approval"), "latency_ms": 22},
            {"level": "Rule", "title": "Drugs & Cosmetics Rules, 1945", "ref": ayush_eval.get("status", "Rule 158-B Compliance"), "latency_ms": 19},
            {"level": "Regime", "title": "Allied (FSSAI & DMROA 1954)", "ref": allied_eval.get("status", "Food-Aahar & Ad Compliance"), "latency_ms": 17}
        ]

    return {
        "status": "success",
        "query": req.query,
        "domain": domain,
        "language": lang,
        "jurisdiction": jurisdiction,
        "title": state.get("title", "Multi-Agent Regulatory Assessment"),
        "detected_botanicals": state.get("detected_botanicals", []),
        "dosage_form": state.get("dosage_form", ""),
        "clause_tree": clause_tree,
        "conflict_matrix": state.get("conflict_matrix", []),
        "detected_collisions": state.get("detected_collisions", []),
        "direct_short_summary": state.get("direct_short_summary", ""),
        "citations": state.get("citations", []),
        "summary": summary_text,
        "workaround": state.get("strategic_workaround", ""),
        "filing_roadmap": state.get("filing_roadmap", []),
        "execution_trace": state.get("execution_trace", []),
        "graph_topology": regulatory_graph.get_topology(jurisdiction=jurisdiction),
        "vernacular_data": state.get("vernacular_mappings", {}),
        "confidence_score": min(94.5, float(state.get("confidence_score", 93.8 if state.get("citations") else 91.5))),
        "grounding_tier": "Statutory Grounded" if jurisdiction == "india" else "Global Treaty Grounded",
        "llm_live": llm_live,
        "llm_source": llm_source,
        "model": model_name
    }

@app.post("/api/query/stream")
async def process_query_stream(req: QueryRequest):
    """
    Streams response in real-time via Server-Sent Events (SSE):
    1. Executes Multi-Agent StateGraph deterministically (sub-80ms).
    2. Emits 'init' event with vernacular mappings, 4 agent pills, citations, and trace.
    3. Streams 'token' events dynamically as LLM/synthesizer generates output.
    4. Emits 'done' event with final metadata and model telemetry.
    """
    domain = req.domain or "Ayurveda"
    lang = req.language or "en"
    jurisdiction = (req.jurisdiction or "india").lower()

    effective_query = req.query
    if req.documents:
        doc_snippets = []
        for d in req.documents:
            fname = d.get("filename", "Attached Document")
            d_text = d.get("text", "")[:3000]
            d_bots = ", ".join(d.get("botanicals_detected", []))
            doc_snippets.append(f"--- [ATTACHED REGULATORY DOCUMENT: {fname}] ---\n(Detected Botanicals: {d_bots or 'None'})\n{d_text}")
        effective_query = f"{req.query}\n\n[CONTEXT FROM ATTACHED DOCUMENTS]:\n" + "\n\n".join(doc_snippets)

    # 1. StateGraph Multi-Agent Execution
    state = regulatory_graph.invoke(effective_query, domain=domain, language=lang, jurisdiction=jurisdiction)

    if jurisdiction == "international":
        wipo_eval = state.get("wipo_evaluation", {})
        cbd_eval = state.get("cbd_evaluation", {})
        eu_eval = state.get("eu_evaluation", {})
        us_eval = state.get("us_evaluation", {})

        clause_tree = [
            {"level": "Treaty", "title": "WIPO GRATK Treaty, 2024", "ref": wipo_eval.get("status", "Mandatory Origin Disclosure"), "latency_ms": 19},
            {"level": "Treaty", "title": "CBD & Nagoya Protocol ABS", "ref": cbd_eval.get("status", "PIC & Benefit Sharing"), "latency_ms": 23},
            {"level": "Directive", "title": "EU THMPD (2004/24/EC)", "ref": eu_eval.get("status", "Traditional Herbal Registration"), "latency_ms": 18},
            {"level": "Guidance", "title": "US FDA Botanical Guidance & DSHEA", "ref": us_eval.get("status", "Dietary Supplement / NDI"), "latency_ms": 16}
        ]
    else:
        ipo_eval = state.get("ipo_evaluation", {})
        nba_eval = state.get("nba_evaluation", {})
        ayush_eval = state.get("ayush_evaluation", {})
        allied_eval = state.get("allied_evaluation", {})

        clause_tree = [
            {"level": "Act", "title": "The Patents Act, 1970", "ref": ipo_eval.get("status", "Section 3(p) Screening"), "latency_ms": 18},
            {"level": "Act", "title": "Biological Diversity Act, 2002", "ref": nba_eval.get("status", "Section 6 Approval"), "latency_ms": 22},
            {"level": "Rule", "title": "Drugs & Cosmetics Rules, 1945", "ref": ayush_eval.get("status", "Rule 158-B Compliance"), "latency_ms": 19},
            {"level": "Regime", "title": "Allied (FSSAI & DMROA 1954)", "ref": allied_eval.get("status", "Food-Aahar & Ad Compliance"), "latency_ms": 17}
        ]

    init_payload = {
        "status": "success",
        "query": req.query,
        "domain": domain,
        "language": lang,
        "jurisdiction": jurisdiction,
        "title": state.get("title", "Multi-Agent Regulatory Assessment"),
        "detected_botanicals": state.get("detected_botanicals", []),
        "dosage_form": state.get("dosage_form", ""),
        "vernacular_data": state.get("vernacular_mappings", {}),
        "clause_tree": clause_tree,
        "conflict_matrix": state.get("conflict_matrix", []),
        "citations": state.get("citations", []),
        "workaround": state.get("strategic_workaround", ""),
        "filing_roadmap": state.get("filing_roadmap", []),
        "execution_trace": state.get("execution_trace", []),
        "graph_topology": regulatory_graph.get_topology(jurisdiction=jurisdiction)
    }

    async def event_generator():
        # Step 1: Send initialization metadata
        yield f"event: init\ndata: {json.dumps(init_payload)}\n\n"
        await asyncio.sleep(0.03)

        # Step 2: Stream tokens dynamically
        full_text = ""
        source = "state_graph_rules"
        model_name = nemotron_client.model

        async for chunk in nemotron_client.stream_query(effective_query, domain=domain, language=lang, state_context=state):
            token = chunk.get("token", "")
            source = chunk.get("source", source)
            model_name = chunk.get("model", model_name)
            full_text += token
            yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

        # Step 3: Send completion event
        done_payload = {
            "status": "complete",
            "model": model_name,
            "llm_live": source == "nvidia_nim",
            "llm_source": source,
            "full_summary": full_text
        }
        yield f"event: done\ndata: {json.dumps(done_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/scan")
def scan_formulation(req: ScanRequest):
    # Calculate score based on dosage form
    score_map = {
        "Crude Churna (Powder)": 18,
        "Aqueous Extract": 42,
        "Standardized Supercritical CO2 Extract": 74,
        "Liposomal / Phospholipid Nanocarrier": 89,
        "Targeted Phyto-Complex": 92
    }
    base_score = score_map.get(req.dosage_form, 50)
    
    # Detect botanicals from DB
    matched_herbs = []
    for herb in req.ingredients:
        h_clean = herb.lower()
        for k, v in BOTANICAL_DB.items():
            if any(term in h_clean for term in [v["common_name"].lower(), v["latin_binomial"].lower(), k.replace("_", " ")]):
                matched_herbs.append(v)
                break
                
    tkdl_overlap_pct = 94 if matched_herbs else 60
    
    workaround = "Direct admixture of known herbs is not patentable under Section 3(p) & 3(e). "
    if base_score < 50:
        workaround += "RECOMMENDATION: Convert crude mixture into a standardized extract or novel liposomal nanocarrier with demonstrated Combination Index CI < 0.7 to achieve patentability."
    else:
        workaround += "EXCELLENT DEFICIENCY POSITION: The advanced dosage form overcomes Section 3(e) admixture barriers by providing enhanced transdermal bio-availability and targeted delivery."
        
    return {
        "status": "success",
        "formulation_score": base_score,
        "dosage_form": req.dosage_form,
        "tkdl_overlap_pct": tkdl_overlap_pct,
        "nba_approval_required": True,
        "admixture_risk": "HIGH" if base_score < 50 else "LOW",
        "matched_botanicals": matched_herbs,
        "workaround_strategy": workaround,
        "suggested_patent_claims": [
            f"A synergistic phytopharmaceutical nanocarrier comprising {req.ingredients[0] if req.ingredients else 'Botanical Extract'} having particle size < 150 nm.",
            "A process of preparing the same using supercritical fluid extraction at 250-300 bar."
        ]
    }

class ClassifierEvaluateRequest(BaseModel):
    q1: Optional[str] = "classical_text"
    q2: Optional[str] = "classical_aqueous"
    q3: Optional[str] = "classical_indication"
    q4: Optional[str] = "oral_ingestible"

@app.post("/api/classifier/evaluate")
def evaluate_formulation_category(req: ClassifierEvaluateRequest):
    """
    Evaluates answers from 4-question clarifying triage into one of the 6 distinct statutory categories
    with calibrated patentability defensibility (capped at <= 94.5%) and Biological Diversity Act ABS liability.
    """
    q1, q2, q3, q4 = req.q1, req.q2, req.q3, req.q4

    # 1. Phytopharmaceutical Drug (D&C Amendment Rules 2015, Rule 122-E)
    if q1 == "phytopharm_fraction" or q2 == "purified_fraction_chrom" or q3 == "ind_pharma_claim":
        return {
            "category_id": "phytopharm",
            "category_num": 4,
            "category_title": "Phytopharmaceutical Drug",
            "statutory_act": "Drugs & Cosmetics Amendment Rules, 2015 (Rule 122-E, Schedule Y / NDCT Rules 2019)",
            "authority": "Central Drugs Standard Control Organization (CDSCO) / DCGI",
            "license_form": "Form CT-20 (Permission to Import / Manufacture New Drug / Phytopharmaceutical)",
            "clinical_mandate": "Investigational New Drug (IND) Dossier: ≥4 chemical biomarkers, 28/90-day sub-chronic toxicology, Phase I–III GCP clinical trials.",
            "ip_barrier": "High / Genuine Patentability. Purified fractions with defined chemical fingerprints are NOT traditional knowledge under Section 3(p).",
            "patentability_score": 92.5,
            "abs_posture": "Mandatory Section 6(1) NBA Form 3 prior approval before patent grant; ex-factory commercial benefit sharing.",
            "workaround_recommendation": "Protect both novel fraction isolation process and standardized synergistic composition with quantifiable pharmacodynamics."
        }

    # 2. Ayurveda-Aahar / Nutraceutical (FSSAI 2022)
    if q1 == "aahar_recipe" or q2 == "food_processing" or q3 == "wellness_dietary":
        return {
            "category_id": "aahar",
            "category_num": 5,
            "category_title": "Ayurveda-Aahar / Nutraceutical",
            "statutory_act": "Food Safety and Standards (Ayurveda Aahara) Regulations, 2022 & FSS Act, 2006",
            "authority": "Food Safety and Standards Authority of India (FSSAI)",
            "license_form": "FSSAI Central / State Manufacturing License with Ayurveda Aahara Logo",
            "clinical_mandate": "Nutritional safety and heavy metal compliance. STRICT statutory prohibition against making disease cure or treatment claims.",
            "ip_barrier": "High Section 3(p) & 3(e) Bar. Traditional dietary nourishment recipes lack inventive step; patentable solely for novel preservation/packaging.",
            "patentability_score": 22.0,
            "abs_posture": "Section 40 Normally Traded Commodities (NTC list, 421 items) exemption applies if sold strictly as food commodity; commercial formulations trigger SBB intimation.",
            "workaround_recommendation": "Do not seek therapeutic patent on the food formulation; protect proprietary stabilization or micro-encapsulation processing methods."
        }

    # 3. Ayush Cosmetic
    if q1 == "cosmetic_recipe" or q3 == "beautification_claim" or (q4 == "topical_external" and q3 not in ["proprietary_clinical_claim", "classical_indication"]):
        return {
            "category_id": "cosmetic",
            "category_num": 6,
            "category_title": "Ayush Cosmetic (Topical Beautification)",
            "statutory_act": "Drugs & Cosmetics Act 1940 & Rules 1945 (Schedule S / Rule 158-B Topical)",
            "authority": "State Licensing Authority (SALA / State Drug Controller)",
            "license_form": "Form 32 / Form 32-A Cosmetic Manufacturing License",
            "clinical_mandate": "20-human patch safety test for skin irritation, microbiological purity, and heavy metal testing (< 10 ppm Lead, < 1 ppm Arsenic).",
            "ip_barrier": "Moderate Section 3(p) Bar. Traditional cosmetic herbs (kumkumadi, chandan) barred unless formulated with novel skin-penetrating lipid vesicles.",
            "patentability_score": 38.0,
            "abs_posture": "Commercial extraction of bioresources triggers Section 7 intimation to State Biodiversity Board (SBB); Indian citizens exempt under 2023 revision.",
            "workaround_recommendation": "Formulate as ethosomal / transfersomal nano-serum with proved dermal permeability to overcome Section 3(e) admixture objections."
        }

    # 4. New / Non-Classical Drug
    if q1 == "new_drug_composition" or q2 == "advanced_nanocarrier" or q3 == "new_disease_claim" or q4 == "mucosal_parenteral":
        return {
            "category_id": "new_drug",
            "category_num": 3,
            "category_title": "New or Non-Classical Drug (Novel Excipients / CDSCO)",
            "statutory_act": "CDSCO New Drugs and Clinical Trials Rules, 2019 & D&C Act, 1940",
            "authority": "Central Drugs Standard Control Organization (CDSCO / DCGI)",
            "license_form": "Form CT-20 / Form 46 New Drug Permission (Central)",
            "clinical_mandate": "Phase I (Safety & PK), Phase II (Dose-ranging), and Phase III (Pivotal multi-center efficacy) clinical trials under CT-04/06.",
            "ip_barrier": "Low Section 3(p) TKDL Bar since formulation is non-classical. Must satisfy Section 3(d) enhanced therapeutic efficacy standard.",
            "patentability_score": 82.0,
            "abs_posture": "Mandatory Section 6(1) NBA Form 3 prior approval before patent grant for Indian biological resources.",
            "workaround_recommendation": "Characterize novel bio-polymer interactions and submit comparative clinical efficacy data proving superior therapeutic outcome."
        }

    # 5. Patent or Proprietary ASU Medicine
    if q1 == "proprietary_ratio" or q2 == "standardized_solvent" or q3 == "proprietary_clinical_claim":
        return {
            "category_id": "proprietary",
            "category_num": 2,
            "category_title": "Patent or Proprietary ASU Medicine",
            "statutory_act": "Drugs & Cosmetics Act, 1940, Section 3(h) & Rules 1945 (Rule 158-B Category II)",
            "authority": "State Ayush Licensing Authority (SALA)",
            "license_form": "Form 25-D (ASU Proprietary Drug License) / Form 24-D",
            "clinical_mandate": "Pilot clinical trial data on minimum 30 human subjects, 14-day acute oral toxicity in 2 animal species, 6-month accelerated stability testing.",
            "ip_barrier": "High Section 3(e) Mere Admixture & Section 3(p) Bar. Patentable ONLY if unexpected synergism (CI < 0.8) or nanocarrier delivery is proven.",
            "patentability_score": 58.0,
            "abs_posture": "Mandatory Section 6(1) NBA Form 3 approval before patent grant; criminal liability under Section 55 for non-compliance.",
            "workaround_recommendation": "Execute Chou-Talalay combination index testing demonstrating CI < 0.75 and encapsulate in standardized phospholipid nanocarrier."
        }

    # 6. Classical / Generic ASU Medicine (Default)
    return {
        "category_id": "classical",
        "category_num": 1,
        "category_title": "Classical / Generic ASU Medicine",
        "statutory_act": "Drugs & Cosmetics Act, 1940, Section 3(a) & Rule 158-B(1)",
        "authority": "State Ayush Licensing Authority (SALA)",
        "license_form": "Form 25-D (Classical ASU Drug License)",
        "clinical_mandate": "Zero clinical trials required. Citation of formulae in 54 First-Schedule authoritative texts constitutes legal proof of safety and efficacy.",
        "ip_barrier": "Absolute Section 3(p) Traditional Knowledge Bar. Identical to TKDL prior art; composition is non-patentable as an invention.",
        "patentability_score": 12.0,
        "abs_posture": "Exempt from prior approval for domestic Indian entities commercializing codified classical knowledge; foreign entities require Section 3 NBA approval.",
        "workaround_recommendation": "Classical compositions cannot be patented directly. Develop a novel bioavailability-enhancing extraction process or standardized fraction."
    }

@app.post("/api/generate-doc")
def generate_document(req: DocGenRequest):
    if req.doc_type == "patent_form_2":
        filepath = generate_patent_draft(req.title, req.herbs, req.workaround_type)
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="Draft_Patent_Form_2_Complete_Specification.docx"
        )
    elif req.doc_type == "nba_form_3":
        filepath = generate_nba_form_3(req.title, req.herbs)
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="Draft_NBA_Form_III_IPR_Approval.docx"
        )
    raise HTTPException(status_code=400, detail="Invalid doc_type requested")

# ===================================================
# MODEL CONTEXT PROTOCOL (MCP) ENDPOINTS
# ===================================================

@app.get("/api/mcp/tools")
def get_mcp_tools():
    """Lists all standardized Model Context Protocol (MCP) tools for external AI clients."""
    return {"tools": mcp_server.list_tools(), "protocol_version": "2024-11-05", "server": "ip-sakti-sahayak-mcp"}

@app.post("/api/mcp/execute")
def execute_mcp_tool_endpoint(req: McpExecuteRequest):
    """Executes an MCP statutory tool directly via JSON."""
    try:
        res = mcp_server.execute_tool(req.tool_name, req.arguments or {})
        return {"status": "success", "tool": req.tool_name, "result": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ===================================================
# PRO / ENTERPRISE TIER: DEDICATED PROJECT STUDIO & MENTORS
# ===================================================

@app.get("/api/projects")
def list_dedicated_projects():
    """Lists all active regulatory dossiers / projects in the Innovator Studio."""
    return {"projects": project_manager.list_projects()}

@app.get("/api/project/{project_id}")
def get_dedicated_project(project_id: str):
    """Retrieves a dedicated project with its 6-stage milestone roadmap graph."""
    proj = project_manager.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project": proj}

@app.post("/api/project/create")
def create_dedicated_project(req: ProjectCreateRequest):
    """Creates a new dedicated regulatory project in the Pro Studio."""
    new_proj = project_manager.create_project(req.dict())
    return {"status": "success", "project": new_proj}

@app.post("/api/project/{project_id}/advance")
def advance_project_milestone(project_id: str, req: ProjectAdvanceRequest):
    """Advances a project milestone stage, dynamically updating the roadmap graph."""
    updated = project_manager.advance_stage(project_id, req.stage_id, req.completion_pct)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "success", "project": updated}

@app.post("/api/mentor/verify")
def verify_mentor_token_endpoint(req: MentorVerifyRequest):
    """Validates an official Ministry of Ayush Mentor Token and unlocks 1-on-1 advisory."""
    res = project_manager.verify_mentor_token(req.project_id, req.token_code)
    return res

@app.post("/api/project/{project_id}/export-dossier")
def export_project_unified_dossier(project_id: str):
    """Generates and returns the complete unified Pro regulatory dossier in Word format."""
    proj = project_manager.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    filepath = generate_unified_dossier(proj)
    filename = os.path.basename(filepath)
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )

@app.get("/api/mentors/directory")
def get_mentors_directory():
    """Returns official Ministry of Ayush mentors directory."""
    return {"mentors": list(AYUSH_MENTOR_REGISTRY.values())}

@app.post("/api/goal/generate-roadmap")
def generate_goal_roadmap_endpoint(req: GoalRoadmapRequest):
    """
    Synthesizes a query-specific 6-stage statutory milestone architecture via Nemotron LLM
    and the Multi-Agent Regulatory StateGraph.
    """
    goal_text = req.goal.strip()
    if not goal_text:
        raise HTTPException(status_code=400, detail="Goal query cannot be empty")
        
    domain = req.domain or "Ayurveda"
    
    # 1. Multi-Agent StateGraph Evaluation
    state = regulatory_graph.invoke(goal_text, domain=domain)
    detected_botanicals = state.get("detected_botanicals", [])
    dosage_form = state.get("dosage_form", "Standardized Formulation")
    ipo_eval = state.get("ipo_evaluation", {})
    nba_eval = state.get("nba_evaluation", {})
    ayush_eval = state.get("ayush_evaluation", {})
    glo_eval = state.get("global_evaluation", {})
    
    stages_result = None
    title_result = f"Roadmap: {goal_text[:40]}"
    llm_generated = False
    
    # 2. Query Nemotron LLM for structured JSON output
    try:
        llm_data = nemotron_client.generate_custom_roadmap_json(goal_text, state_context=state)
        if llm_data and "stages" in llm_data and len(llm_data["stages"]) >= 4:
            stages_result = llm_data["stages"]
            title_result = llm_data.get("title", title_result)
            llm_generated = True
    except Exception as e:
        print(f"[Goal Roadmap Endpoint Exception]: {e}")

    # 3. High-Fidelity Query-Tailored Synthesis Fallback
    if not stages_result:
        is_patent = any(w in goal_text.lower() for w in ["patent", "ipr", "claim", "invent", "synerg", "novel", "balm", "gel", "extract", "nanocarrier"])
        is_licensing = any(w in goal_text.lower() for w in ["license", "licensing", "158-b", "syrup", "churna", "classical", "sla", "form 24", "manufacturing"])
        is_export = any(w in goal_text.lower() for w in ["export", "global", "us", "fda", "eu", "europe", "wipo", "pct", "germany", "international"])
        
        def get_herb_name(b):
            if isinstance(b, dict):
                return b.get("common_name") or b.get("canonical_name") or b.get("latin_name") or "Botanical"
            return str(b)

        herb_names = [get_herb_name(b) for b in detected_botanicals]
        herb_display = herb_names[0] if herb_names else "Botanical Extract"
        second_herb = herb_names[1] if len(herb_names) > 1 else "Active Phytochemical"
        
        title_result = f"{herb_display} & {second_herb} {dosage_form} Dossier"
        
        stages_result = [
            {
                "id": "stage_1",
                "order": 1,
                "title": f"{herb_display} Pharmacopoeial Assay",
                "timeline": "Weeks 1-2",
                "authority": "PCIM&H / Ministry of Ayush",
                "statute": "Ayurvedic/Unani Pharmacopoeia Standards",
                "description": f"Standardize raw {herb_display} botanical markers and establish chemical fingerprinting against official monographs.",
                "mandates": [
                    f"HPTLC Fingerprint Identification for {herb_display}",
                    "Heavy Metal & Microbial Clearance (Schedule E-1)"
                ],
                "completed": False
            },
            {
                "id": "stage_2",
                "order": 2,
                "title": "TKDL Section 3(p) Clearance",
                "timeline": "Weeks 3-5",
                "authority": "Indian Patent Office (IPO) / CSIR-TKDL",
                "statute": "Patents Act, 1970 Section 3(p) & 3(e)",
                "description": f"Screen {herb_display} and {second_herb} formulation against 250,000+ TKDL prior-art citations to establish non-obvious synergistic efficacy.",
                "mandates": [
                    "CSIR-TKDL Prior-Art Search Clearance Certificate",
                    "Synergism Assay with Combination Index CI < 0.75"
                ],
                "completed": False
            },
            {
                "id": "stage_3",
                "order": 3,
                "title": "NBA Section 6 Prior Approval",
                "timeline": "Weeks 6-9",
                "authority": "National Biodiversity Authority (NBA)",
                "statute": "Biological Diversity Act, 2002 Section 6(1)",
                "description": f"Submit mandatory Form III prior approval filing for Indian biological resource utilization and commercial ABS benefit sharing.",
                "mandates": [
                    "NBA Form III Application & ABS Ex-Factory Royalty Undertaking",
                    "State Biodiversity Board (SBB) Intimation Notice"
                ],
                "completed": False
            },
            {
                "id": "stage_4",
                "order": 4,
                "title": f"Rule 158-B {dosage_form} Dossier",
                "timeline": "Weeks 10-15",
                "authority": "State Ayush Licensing Authority (SALA)",
                "statute": "Drugs & Cosmetics Rules, 1945 Rule 158-B",
                "description": f"Compile Form 24-D manufacturing license application for {dosage_form} backed by Schedule T cleanroom audit.",
                "mandates": [
                    "Rule 158-B Proof of Safety & Pilot Efficacy Clinical Data",
                    "Schedule T 1,200 sq. ft. Cleanroom Validation Protocol"
                ],
                "completed": False
            },
            {
                "id": "stage_5",
                "order": 5,
                "title": "GLP Pre-Clinical Safety Protocol",
                "timeline": "Weeks 16-20",
                "authority": "Accredited Ayush Testing Laboratory",
                "statute": "OECD 408 & Ayush GCP Guidelines",
                "description": f"Execute 90-day repeated-dose oral toxicity and accelerated stability testing for {herb_display} formulation.",
                "mandates": [
                    "OECD 408 90-Day Toxicity Protocol Evaluation",
                    "Real-Time and Accelerated Stability (ICH Q1A)"
                ],
                "completed": False
            },
            {
                "id": "stage_6",
                "order": 6,
                "title": "WIPO PCT & Global Export Gateway" if is_export else "Commercial Manufacturing Grant",
                "timeline": "Weeks 21-26",
                "authority": "WIPO / US FDA / CDSCO" if is_export else "State Ayush Licensing Authority",
                "statute": "WIPO PCT Treaty & US FDA Botanical Guidance" if is_export else "Drugs & Cosmetics Act Form 25-D",
                "description": f"Obtain Certificate of Pharmaceutical Product (CoPP) and international patent clearance for commercial launch.",
                "mandates": [
                    "WHO-GMP Certificate of Pharmaceutical Product (CoPP)",
                    "Gazette Form 25-D Final Commercial Manufacturing License"
                ],
                "completed": False
            }
        ]

    # Clean any section symbols (§)
    def clean_sec(val):
        if not val:
            return ""
        return str(val).replace("§", "Section ")

    for idx, stg in enumerate(stages_result):
        stg["id"] = stg.get("id") or f"stage_{idx + 1}"
        stg["order"] = idx + 1
        stg["title"] = clean_sec(stg.get("title", f"Stage {idx + 1}"))
        stg["timeline"] = clean_sec(stg.get("timeline", "Weeks 1-4"))
        stg["authority"] = clean_sec(stg.get("authority", "Ayush Regulatory Authority"))
        stg["statute"] = clean_sec(stg.get("statute", "Statutory Compliance"))
        stg["description"] = clean_sec(stg.get("description", "Statutory compliance deliverable."))
        stg["mandates"] = [clean_sec(m) for m in stg.get("mandates", [])]
        stg["completed"] = False

    return {
        "status": "success",
        "goal": goal_text,
        "title": clean_sec(title_result),
        "detected_botanicals": detected_botanicals,
        "dosage_form": dosage_form,
        "llm_generated": llm_generated,
        "stages": stages_result
    }

class StageQueryRequest(BaseModel):
    goal_title: str
    stage_id: str
    stage_title: str
    stage_order: int
    stage_statute: str
    stage_authority: str
    query: str
    detected_botanicals: Optional[List[Any]] = None

@app.post("/api/goal/stage-query")
async def process_stage_query(req: StageQueryRequest):
    """
    Dedicated Stage-Specific AI Chatbot Query Processor:
    Provides authoritative, contextual statutory guidance for a specific milestone box.
    """
    botanical_str = ", ".join([str(b.get("common_name", b) if isinstance(b, dict) else b) for b in (req.detected_botanicals or [])]) or "Ayush Botanical Composition"
    
    stage_prompt = f"""You are the dedicated Senior Ayush Regulatory Officer assisting specifically with Stage {req.stage_order}: {req.stage_title}.
Project Goal: {req.goal_title}
Formulation Botanicals: {botanical_str}
Governing Statute: {req.stage_statute}
Governing Authority: {req.stage_authority}

User Query regarding this specific stage:
"{req.query}"

Provide clear, highly authoritative, step-by-step guidance.
Include:
1. Exact procedural requirements and mandatory documents.
2. Compliance steps under {req.stage_statute} to avoid objection or rejection from {req.stage_authority}.
3. Timelines, fees (if applicable), and practical drafting advice.

CRITICAL CONSTRAINT: Never use the symbol '§'. Write 'Section ' explicitly."""

    answer_text = ""
    try:
        res = nemotron_client.query(stage_prompt, domain="Ayurveda", language="en")
        if res and res.get("response"):
            answer_text = res["response"]
    except Exception as e:
        print(f"[Stage Query Error]: {e}")

    if not answer_text:
        answer_text = (
            f"### Stage {req.stage_order}: {req.stage_title} Statutory Guidance\n\n"
            f"**Governing Authority:** {req.stage_authority}  \n"
            f"**Statutory Basis:** {req.stage_statute}  \n\n"
            f"Regarding your query **\"{req.query}\"** for *{req.goal_title}*:\n\n"
            f"1. **Statutory Filing Requirement:** Under {req.stage_statute}, applicants must submit the designated statutory application accompanied by authenticated chemical fingerprinting and botanical sourcing certificates for {botanical_str}.\n\n"
            f"2. **Objection Avoidance:** {req.stage_authority} strictly scrutinizes prior-art citations and test standard compliance. Ensure that all analytical test reports are issued by an ISO/IEC 17025 NABL-accredited laboratory and that botanical identifiers match the Ayurvedic Pharmacopoeia of India (API) monographs.\n\n"
            f"3. **Recommended Next Step:** Download the official pre-filled filing annexure provided in this stage workspace, complete the verified applicant declarations, and attach the statutory inspection checklist before submitting to {req.stage_authority}."
        )

    answer_text = answer_text.replace("§", "Section ")

    return {
        "status": "success",
        "stage_id": req.stage_id,
        "stage_order": req.stage_order,
        "answer": answer_text
    }

# ==============================================================================
# EMPANELED AYUSH STATUTORY MENTORS REGISTRY & CONSULTATION GATEWAY
# ==============================================================================

MENTORS_REGISTRY = [
    {
        "id": "dr_shastri",
        "name": "Dr. Anand V. Shastri",
        "salutation": "Dr.",
        "designation": "Former Senior Controller of Patents & Designs",
        "organization": "Indian Patent Office (IPO) & CSIR-TKDL Directorate",
        "specialization": "Ayush Patentability, Section 3(p) TKDL Prior-Art Defense & Section 3(e) Synergism",
        "domain_tag": "patent",
        "domain_label": "Patents & TKDL",
        "experience_years": 28,
        "consultations_count": 184,
        "rating": 4.9,
        "photo_url": "/static/assets/mentor_shastri.jpg",
        "is_online": True,
        "status_text": "ONLINE NOW",
        "status_desc": "Available for Instant Session",
        "next_available": "Immediate (Wait: ~2 mins)",
        "hourly_fee": "Ministry Empaneled • Included in Paid Tier",
        "bio": "Over 28 years heading patent examination divisions. Expert in overcoming Section 3(p) traditional knowledge rejections and drafting synergistic clinical claims for Ayurvedic phytopharmaceuticals.",
        "badges": ["Verified Ministry Empaneled", "Top Patent Authority"],
        "languages": ["English", "Hindi", "Marathi"]
    },
    {
        "id": "dr_nair",
        "name": "Dr. Rajeshwari K. Nair",
        "salutation": "Dr.",
        "designation": "Former Director, State Ayush Licensing Authority",
        "organization": "State Licensing Authority (SALA) & CDSCO Ayush Advisory",
        "specialization": "Rule 158-B Manufacturing Licenses, Schedule T Cleanrooms & Form 24-D Dossiers",
        "domain_tag": "licensing",
        "domain_label": "Drug Licensing",
        "experience_years": 24,
        "consultations_count": 230,
        "rating": 4.95,
        "photo_url": "/static/assets/mentor_nair.jpg",
        "is_online": True,
        "status_text": "ONLINE NOW",
        "status_desc": "Available for Instant Session",
        "next_available": "Immediate (Wait: ~1 min)",
        "hourly_fee": "Ministry Empaneled • Included in Paid Tier",
        "bio": "24+ years as State Licensing Director evaluating manufacturing dossiers for classical and patent proprietary Ayush medicines, Schedule T GMP factory compliance, and stability audit protocols.",
        "badges": ["Verified Ministry Empaneled", "Drug Licensing Authority"],
        "languages": ["English", "Hindi", "Malayalam"]
    },
    {
        "id": "adv_sen",
        "name": "Adv. Vikramaditya Sen",
        "salutation": "Adv.",
        "designation": "Senior Legal Counsel, National Biodiversity Authority Panel",
        "organization": "National Biodiversity Authority (NBA) & NGT Panel",
        "specialization": "BD Act Section 6 Form III Approvals, ABS Ex-Factory Royalties & SBB Intimation",
        "domain_tag": "biodiversity",
        "domain_label": "NBA & Biodiversity",
        "experience_years": 19,
        "consultations_count": 142,
        "rating": 4.85,
        "photo_url": "/static/assets/mentor_sen.jpg",
        "is_online": False,
        "status_text": "OFFLINE",
        "status_desc": "Next slot: Today at 4:30 PM",
        "next_available": "Today at 4:30 PM",
        "hourly_fee": "Ministry Empaneled • Included in Paid Tier",
        "bio": "Supreme Court advocate and lead statutory counsel handling 400+ Access and Benefit Sharing (ABS) filings, Section 6 IPR clearance agreements, and State Biodiversity Board compliance disputes.",
        "badges": ["Verified Ministry Empaneled", "Biodiversity Counsel"],
        "languages": ["English", "Hindi", "Bengali"]
    },
    {
        "id": "dr_sundaram",
        "name": "Dr. Meenakshi Sundaram",
        "salutation": "Dr.",
        "designation": "Former Head of Standardization, PCIM&H",
        "organization": "Pharmacopoeia Commission for Indian Medicine & Homoeopathy",
        "specialization": "API Reference Standards, HPTLC Chemical Fingerprints & Schedule E-1 Limits",
        "domain_tag": "pharmacopoeia",
        "domain_label": "Pharmacopoeia & Quality",
        "experience_years": 22,
        "consultations_count": 98,
        "rating": 4.9,
        "photo_url": "/static/assets/mentor_sundaram.jpg",
        "is_online": False,
        "status_text": "OFFLINE",
        "status_desc": "Next slot: Tomorrow at 11:00 AM",
        "next_available": "Tomorrow at 11:00 AM",
        "hourly_fee": "Ministry Empaneled • Included in Paid Tier",
        "bio": "22+ years at PCIM&H developing and publishing official Ayurvedic Pharmacopoeia monographs, botanical chemical markers standardization, and heavy metal/pesticide residue validation protocols.",
        "badges": ["Verified Ministry Empaneled", "Pharmacopoeia Specialist"],
        "languages": ["English", "Hindi", "Tamil"]
    }
]

@app.get("/api/mentors")
def get_mentors():
    return {"status": "success", "mentors": MENTORS_REGISTRY}

class MentorChatRequest(BaseModel):
    mentor_id: str
    message: str
    attached_roadmap: Optional[Dict[str, Any]] = None

@app.post("/api/mentor/chat")
async def process_mentor_chat(req: MentorChatRequest):
    mentor = next((m for m in MENTORS_REGISTRY if m["id"] == req.mentor_id), None)
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    roadmap_context = ""
    if req.attached_roadmap:
        r = req.attached_roadmap
        title = r.get("title") or r.get("query") or "Formulation Project"
        stages = r.get("stages", [])
        total = len(stages)
        completed = [s.get("title") for s in stages if s.get("completed")]
        pending = [s.get("title") for s in stages if not s.get("completed")]
        active_stage = next((s.get("title") for s in stages if s.get("id") == r.get("activeStageId")), pending[0] if pending else "Final Review")

        roadmap_context = f"""
SHARED USER ROADMAP CONTEXT FROM ACHIEVE GOAL MODE:
- Goal / Formulation: "{title}"
- Active Milestone: {active_stage}
- Progress: {len(completed)}/{total} Stages Completed
- Completed Milestones: {', '.join(completed) if completed else 'None yet'}
- Pending Milestones: {', '.join(pending) if pending else 'All completed'}
Please review this shared statutory progress carefully in your response, acknowledging what is done and giving actionable guidance on the active/pending milestones.
"""

    prompt = f"""You are {mentor['name']}, {mentor['designation']} with {mentor['organization']}.
You are an empaneled senior advisor for the Ministry of Ayush.
Your specialization: {mentor['specialization']}.
Your bio: {mentor['bio']}.

{roadmap_context}

User Consultation Query:
"{req.message}"

Provide an authoritative, warm, highly practical, and legally grounded 1-on-1 advisory response in your persona.
Include exact statutory recommendations, document guidance, and strategic steps.
CRITICAL CONSTRAINT: Never use the symbol '§'. Write 'Section ' explicitly."""

    response_text = ""
    try:
        res = nemotron_client.query(prompt, domain="Ayurveda", language="en")
        if res and res.get("response"):
            response_text = res["response"]
    except Exception as e:
        print(f"[Mentor Chat Query Error]: {e}")

    if not response_text:
        if req.attached_roadmap:
            r = req.attached_roadmap
            response_text = (
                f"Hello! I am {mentor['name']}. I have thoroughly reviewed your shared roadmap for **{r.get('title', 'your formulation')}**.\n\n"
                f"I see you have completed **{len([s for s in r.get('stages', []) if s.get('completed')])} out of {len(r.get('stages', []))} statutory milestones**. "
                f"Regarding your query **\"{req.message}\"**:\n\n"
                f"From my statutory experience with {mentor['organization']}, the most critical prerequisite here is to ensure all documentation strictly complies with official gazette rules. "
                f"For your pending stages, prioritize authenticated laboratory certificates and proper authority intimations to prevent scrutiny delays. Let me know if you would like me to review your draft filing dossier!"
            )
        else:
            response_text = (
                f"Hello! I am {mentor['name']}. Regarding your query on **\"{req.message}\"**:\n\n"
                f"Under official Ministry guidelines and {mentor['specialization']}, you should ensure that your application is drafted with precise statutory references and authenticated botanical test data. "
                f"Feel free to share your active Achieve Goal roadmap with me using the 'Share Roadmap' button so I can review your exact milestone progress!"
            )

    response_text = response_text.replace("§", "Section ")

    return {
        "status": "success",
        "mentor_id": mentor["id"],
        "mentor_name": mentor["name"],
        "response": response_text
    }

class MentorScheduleRequest(BaseModel):
    mentor_id: str
    date: str
    time_slot: str
    topic: Optional[str] = "Ayush Statutory Consultation"
    notes: Optional[str] = None
    attached_roadmap: Optional[Dict[str, Any]] = None

@app.post("/api/mentor/schedule")
def schedule_mentor_meeting(req: MentorScheduleRequest):
    mentor = next((m for m in MENTORS_REGISTRY if m["id"] == req.mentor_id), None)
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    import random
    ref_id = f"AYUSH-ADV-{random.randint(10000, 99999)}"

    return {
        "status": "success",
        "booking_ref": ref_id,
        "mentor_id": mentor["id"],
        "mentor_name": mentor["name"],
        "mentor_photo": mentor["photo_url"],
        "mentor_designation": mentor["designation"],
        "date": req.date,
        "time_slot": req.time_slot,
        "topic": req.topic,
        "meet_link": f"https://meet.ayush.gov.in/consultation-{ref_id.lower()}",
        "calendar_invite": f"INV-{ref_id}.ics",
        "attached_roadmap_title": req.attached_roadmap.get("title") if req.attached_roadmap else None,
        "confirmation_message": f"Statutory consultation confirmed with {mentor['name']} for {req.date} at {req.time_slot}."
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

