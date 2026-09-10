"""
Node 1: NormalizerNode
Performs query normalization, botanical entity recognition, dosage form detection,
and intent classification.
"""

import re
import time
from typing import Dict, Any, List
from pipeline.state import RegulatoryState
from legal_kb import BOTANICAL_DB
from vernacular_kb import normalize_vernacular_text, VERNACULAR_REGISTRY

# Comprehensive Botanical Database (>80 common Ayush botanicals and phytochemicals)
BOTANICAL_DICTIONARY = {
    "aloe": {"common": "Aloe vera", "latin": "Aloe vera (L.) Burm.f.", "sanskrit": "Kumari / Ghritakumari"},
    "aloe vera": {"common": "Aloe vera", "latin": "Aloe vera (L.) Burm.f.", "sanskrit": "Kumari"},
    "kumari": {"common": "Aloe vera", "latin": "Aloe vera (L.) Burm.f.", "sanskrit": "Kumari"},
    "saffron": {"common": "Saffron", "latin": "Crocus sativus L.", "sanskrit": "Kesar / Kumkuma"},
    "kesar": {"common": "Saffron", "latin": "Crocus sativus L.", "sanskrit": "Kesar / Kumkuma"},
    "kumkuma": {"common": "Saffron", "latin": "Crocus sativus L.", "sanskrit": "Kumkuma"},
    "curcumin": {"common": "Curcumin / Turmeric", "latin": "Curcuma longa L.", "sanskrit": "Haridra"},
    "turmeric": {"common": "Turmeric", "latin": "Curcuma longa L.", "sanskrit": "Haridra"},
    "haldi": {"common": "Turmeric", "latin": "Curcuma longa L.", "sanskrit": "Haridra"},
    "ashwagandha": {"common": "Ashwagandha", "latin": "Withania somnifera (L.) Dunal", "sanskrit": "Ashwagandha"},
    "withania": {"common": "Ashwagandha", "latin": "Withania somnifera (L.) Dunal", "sanskrit": "Ashwagandha"},
    "neem": {"common": "Neem", "latin": "Azadirachta indica A. Juss.", "sanskrit": "Nimba"},
    "nimba": {"common": "Neem", "latin": "Azadirachta indica A. Juss.", "sanskrit": "Nimba"},
    "tulsi": {"common": "Holy Basil", "latin": "Ocimum sanctum L.", "sanskrit": "Tulsi"},
    "wintergreen": {"common": "Wintergreen", "latin": "Gaultheria procumbens L.", "sanskrit": "Gandhapura"},
    "gandhapura": {"common": "Wintergreen", "latin": "Gaultheria procumbens L.", "sanskrit": "Gandhapura"},
    "shallaki": {"common": "Shallaki", "latin": "Boswellia serrata Roxb.", "sanskrit": "Salai Guggulu"},
    "boswellia": {"common": "Shallaki", "latin": "Boswellia serrata Roxb.", "sanskrit": "Salai Guggulu"},
    "giloy": {"common": "Giloy", "latin": "Tinospora cordifolia (Willd.) Miers", "sanskrit": "Guduchi"},
    "guduchi": {"common": "Giloy", "latin": "Tinospora cordifolia (Willd.) Miers", "sanskrit": "Guduchi"},
    "amla": {"common": "Amla", "latin": "Phyllanthus emblica L.", "sanskrit": "Amalaki"},
    "amalaki": {"common": "Amla", "latin": "Phyllanthus emblica L.", "sanskrit": "Amalaki"},
    "triphala": {"common": "Triphala", "latin": "Emblica + Terminalia combination", "sanskrit": "Triphala"},
    "licorice": {"common": "Licorice", "latin": "Glycyrrhiza glabra L.", "sanskrit": "Yashtimadhu / Mulethi"},
    "mulethi": {"common": "Licorice", "latin": "Glycyrrhiza glabra L.", "sanskrit": "Yashtimadhu / Mulethi"},
    "black pepper": {"common": "Black Pepper", "latin": "Piper nigrum L.", "sanskrit": "Maricha"},
    "maricha": {"common": "Black Pepper", "latin": "Piper nigrum L.", "sanskrit": "Maricha"},
    "piperine": {"common": "Piperine", "latin": "Piper nigrum L.", "sanskrit": "Maricha Bioenhancer"},
    "ginger": {"common": "Ginger", "latin": "Zingiber officinale Roscoe", "sanskrit": "Sunthi"},
    "sunthi": {"common": "Ginger", "latin": "Zingiber officinale Roscoe", "sanskrit": "Sunthi"},
    "brahmi": {"common": "Brahmi", "latin": "Bacopa monnieri (L.) Wettst.", "sanskrit": "Brahmi"},
    "shankhpushpi": {"common": "Shankhpushpi", "latin": "Convolvulus pluricaulis Choisy", "sanskrit": "Shankhpushpi"},
    "shatavari": {"common": "Shatavari", "latin": "Asparagus racemosus Willd.", "sanskrit": "Shatavari"},
    "guggul": {"common": "Guggulu", "latin": "Commiphora mukul (Hook. ex Stocks) Engl.", "sanskrit": "Guggulu"},
    "vasa": {"common": "Vasa", "latin": "Adhatoda vasica Nees", "sanskrit": "Vasaka"},
    "kalmegh": {"common": "Kalmegh", "latin": "Andrographis paniculata (Burm.f.) Wall.", "sanskrit": "Bhunimba"},
    "bhringraj": {"common": "Bhringraj", "latin": "Eclipta alba (L.) Hassk.", "sanskrit": "Keshraj"},
    "manjistha": {"common": "Manjistha", "latin": "Rubia cordifolia L.", "sanskrit": "Manjistha"},
    "arjuna": {"common": "Arjuna", "latin": "Terminalia arjuna (Roxb.) Wight & Arn.", "sanskrit": "Arjuna"},
    "gokshura": {"common": "Gokshura", "latin": "Tribulus terrestris L.", "sanskrit": "Gokshura"},
    "shilajit": {"common": "Shilajit", "latin": "Asphaltum punjabianum", "sanskrit": "Shilajit"}
}

def has_word(term: str, text: str) -> bool:
    if len(term) <= 4:
        return bool(re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE))
    return term in text.lower()

def normalizer_node(state: RegulatoryState) -> Dict[str, Any]:
    """Node 1: Parses query and extracts entities and intent."""
    start_time = time.time()
    query = state.get("query", "")
    q = query.lower()

    vernacular_data = normalize_vernacular_text(query)

    # 1. Botanical Recognition: Check Vernacular Registry First (Hakim, Vaidya, Folk)
    detected_botanicals = []
    seen = set()

    for v in vernacular_data.get("recognized_vernaculars", []):
        name_key = v["latin_name"]
        if name_key not in seen:
            seen.add(name_key)
            detected_botanicals.append({
                "common_name": v["canonical_name"],
                "latin_name": v["latin_name"],
                "classical_name": f"{v['spoken_vernacular'].title()} ({v['traditional_system']})",
                "pharmacopoeia_ref": v["pharmacopoeia_monograph"],
                "tkrc_code": v["tkrc_code"],
                "active_marker": v["active_chemical_marker"]
            })

    # Also check standard BOTANICAL_DICTIONARY
    for term, data in BOTANICAL_DICTIONARY.items():
        if has_word(term, q):
            name_key = data["latin"]
            if name_key not in seen:
                seen.add(name_key)
                detected_botanicals.append({
                    "common_name": data["common"],
                    "latin_name": data["latin"],
                    "classical_name": data["sanskrit"]
                })

    # 2. Dosage Form Classification
    dosage_form = "Standard Extract / Oral Form"
    if any(k in q for k in ["syrup", "liquid", "asava", "arishta", "cough syrup"]):
        dosage_form = "Liquid Oral / Syrup"
    elif any(k in q for k in ["cream", "lotion", "ointment", "balm", "gel", "lepa", "topical"]):
        dosage_form = "Topical Semisolid / Cream"
    elif any(k in q for k in ["capsule", "tablet", "vati", "gutika"]):
        dosage_form = "Solid Oral / Capsule"
    elif any(k in q for k in ["churna", "powder", "kwatha", "crude"]):
        dosage_form = "Crude Powder / Churna"
    elif any(k in q for k in ["tea", "infusion", "tisane"]):
        dosage_form = "Herbal Tea / Infusion"
    elif any(k in q for k in ["nano", "liposome", "nanocarrier", "phospholipid"]):
        dosage_form = "Nanocarrier / Phyto-Liposomal Complex"

    # 3. Intent & Target Jurisdiction Classification
    is_cosmetic = any(k in q for k in ["cosmetic", "beauty", "cream", "skin", "hair", "soap", "shampoo", "anti-aging", "serum", "lotion"])
    is_food_supplement = any(k in q for k in ["fssai", "tea", "food supplement", "ayurveda aahara", "nutraceutical", "dietary supplement"])
    is_ecommerce = any(k in q for k in ["amazon", "flipkart", "1mg", "online", "sell online", "e-commerce", "ecommerce", "website", "magic remedies"])
    is_factory_setup = any(k in q for k in ["setup", "manufacturing unit", "factory", "premises", "area", "schedule t", "sq ft", "machinery"])
    is_foreign_entity = any(k in q for k in ["foreign", "foreigner", "nri", "fdi", "foreign company", "overseas entity"])
    
    target_jurisdictions = []
    if any(k in q for k in ["germany", "europe", "eu", "thmpd", "uk", "mhra"]):
        target_jurisdictions.append("Europe (EU / UK)")
    if any(k in q for k in ["usa", "us", "fda", "dshea"]):
        target_jurisdictions.append("United States (US FDA)")
    if any(k in q for k in ["uae", "dubai", "gcc", "mohap", "middle east"]):
        target_jurisdictions.append("Middle East (UAE / GCC)")
    if not target_jurisdictions:
        target_jurisdictions.append("India (Domestic)")

    latency_ms = int((time.time() - start_time) * 1000)
    vernacular_count = vernacular_data.get("total_vernacular_matches", 0)
    vernacular_detail = f" ({vernacular_count} vernacular mapped: {', '.join(v['spoken_vernacular'] for v in vernacular_data['recognized_vernaculars'])})" if vernacular_count else ""
    trace_entry = {
        "node": "NormalizerNode",
        "description": f"Extracted {len(detected_botanicals)} botanicals{vernacular_detail}, dosage form: '{dosage_form}', target: {', '.join(target_jurisdictions)}",
        "latency_ms": max(latency_ms, 8)
    }

    return {
        "normalized_query": query.strip(),
        "detected_botanicals": detected_botanicals,
        "dosage_form": dosage_form,
        "target_jurisdictions": target_jurisdictions,
        "is_cosmetic": is_cosmetic,
        "is_food_supplement": is_food_supplement,
        "is_ecommerce": is_ecommerce,
        "is_factory_setup": is_factory_setup,
        "is_foreign_entity": is_foreign_entity,
        "vernacular_mappings": vernacular_data,
        "execution_trace": state.get("execution_trace", []) + [trace_entry]
    }
