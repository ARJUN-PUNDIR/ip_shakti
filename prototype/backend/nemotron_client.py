"""
Unified Multi-Provider LLM Client for IP-SAKTI Sahayak (SIH26045)
Supports:
1. NVIDIA NIM API (Nemotron-3, Nemotron-3.5 Lightning, Llama-3.3, DeepSeek-R1)
2. OpenAI API (GPT-4o, GPT-4o-mini, o3-mini, o1)
3. Ollama (Local & Offline on localhost:11434 - Zero Key Required)
4. Multi-Agent StateGraph Grounded Fallback
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root or parent
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()  # Also load from current working directory

# Sync LangSmith / LangChain tracing environment variables
try:
    from langsmith import traceable
except ImportError:
    def traceable(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

def sync_langsmith_config():
    load_dotenv(dotenv_path=env_path, override=True)
    load_dotenv(override=True)
    _ls_key = (os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY") or "").strip()
    if _ls_key and _ls_key != "your_langsmith_api_key_here" and not _ls_key.startswith("paste_"):
        os.environ["LANGSMITH_API_KEY"] = _ls_key
        os.environ["LANGCHAIN_API_KEY"] = _ls_key
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ.setdefault("LANGSMITH_PROJECT", os.getenv("LANGCHAIN_PROJECT", "ip-sakti-sahayak"))
        os.environ.setdefault("LANGCHAIN_PROJECT", os.getenv("LANGSMITH_PROJECT", "ip-sakti-sahayak"))
        return True
    else:
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False

sync_langsmith_config()

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
OPENAI_BASE_URL = "https://api.openai.com/v1/chat/completions"

DEFAULT_MODEL = os.getenv("ACTIVE_LLM_MODEL", os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b"))
DEFAULT_PROVIDER = os.getenv("ACTIVE_LLM_PROVIDER", "nvidia")

SYSTEM_PROMPT = """You are IP-SAKTI Sahayak, an authoritative, citation-grounded regulatory intelligence assistant for the Ministry of Ayush, Government of India.
You specialize in:
1. Indian Patent Law: The Patents Act 1970 (Section 3(p) traditional knowledge, Section 3(e) mere admixture, Section 3(d) incremental innovation).
2. The Biological Diversity Act 2002 & 2023 amendments (Section 6 mandatory NBA Form 3 prior approval, Section 3/4/55 criminal liability).
3. The Drugs & Cosmetics Act 1940 & Rules 1945 (Chapter IV-A, Rule 158-B classical vs proprietary licensing, Form 24-D / Form 24-E loan license).
4. Statutory Pharmacopoeias under PCIM&H:
   - Unani Pharmacopoeia of India (UPI) [used by Hakims in Tibb-e-Unani]
   - Siddha Pharmacopoeia of India (SPI) [used by Siddha Vaidyars in Maruthuvam]
   - Ayurvedic Pharmacopoeia of India (API) & NFI [used by Ayurvedic Vaidyas]
   - CSIR Traditional Knowledge Digital Library (TKDL) and Traditional Knowledge Resource Classification (TKRC)
5. Global Regimes (WIPO PCT, US FDA Botanical Drug Guidance vs DSHEA, EU THMPD Directive 2004/24/EC 15-year rule).

CRITICAL INSTRUCTIONS:
1. Traditional Dialect Normalization: When practitioners use vernacular dialect or traditional names (e.g. Unani terms like Asgandh Nagori, Filfil Siyah; Siddha terms like Amukkara Kizhangu, Nilavembu; or Folk terms like Hadjod, Patharchatta), acknowledge the traditional system and ground it in its statutory PCIM&H Pharmacopoeial monograph and Latin binomial. If no vernacular or dialect terms are present in the query, do not perform dialect normalization or introduce dialect synonyms.
2. Provide atomic clause-level citations (e.g. [Patents Act 1970, Section 3(p)], [Biological Diversity Act 2002, Section 6(1)], [D&C Rules, Rule 158-B(1)(a)], [UPI Part-I, Vol-I, Mono 08]).
3. Explicitly detect and highlight any REGULATION CONFLICT between Patent Law, Ayush Drug Licensing, and Biodiversity Access.
4. Recommend actionable patentable workarounds (e.g., synergistic therapeutic index CI < 0.8, novel phyto-liposomal delivery, standardized supercritical CO2 extraction).
5. Maintain deterministic legal grounding. Do not hallucinate fake sections. Always respond in standard English font/Latin characters."""

class NemotronClient:
    def __init__(self, api_key: str = None, model: str = DEFAULT_MODEL, provider: str = DEFAULT_PROVIDER):
        self.provider = provider or "nvidia"
        self.model = model or DEFAULT_MODEL
        
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        if api_key:
            if api_key.startswith("sk-") and not api_key.startswith("nvapi"):
                self.openai_api_key = api_key
                self.provider = "openai"
            else:
                self.nvidia_api_key = api_key
                self.provider = "nvidia"
                
        self.api_key = self.nvidia_api_key or self.openai_api_key
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        # Infer provider from model name if not explicitly set
        if self.model:
            self.provider = self.detect_provider(self.model)

    def detect_provider(self, model_name: str) -> str:
        if not model_name:
            return "nvidia"
        m = model_name.lower().strip()
        if m.startswith("gpt-") or m.startswith("o1") or m.startswith("o3") or "openai" in m:
            return "openai"
        elif m.startswith("llama3") or m.startswith("qwen") or m.startswith("mistral") or "ollama" in m or m.startswith("local/"):
            return "ollama"
        else:
            return "nvidia"

    def set_config(self, provider: str = None, model: str = None, api_key: str = None, ollama_url: str = None):
        if model:
            self.model = model.strip()
            
        if provider:
            self.provider = provider.lower().strip()
        elif model:
            self.provider = self.detect_provider(self.model)

        if api_key:
            key_clean = api_key.strip()
            if self.provider == "openai" or (key_clean.startswith("sk-") and not key_clean.startswith("nvapi")):
                self.openai_api_key = key_clean
                self.provider = "openai"
            else:
                self.nvidia_api_key = key_clean
                if not provider:
                    self.provider = "nvidia"
            self.api_key = key_clean

        if ollama_url:
            self.ollama_url = ollama_url.strip()

    def get_api_key(self, provider: str = None) -> str:
        p = provider or self.provider
        if p == "openai":
            if self.openai_api_key and len(self.openai_api_key.strip()) > 10:
                return self.openai_api_key.strip()
            env_key = os.getenv("OPENAI_API_KEY", "").strip()
            if env_key and len(env_key) > 10:
                self.openai_api_key = env_key
                return env_key
            # Try reading from .env
            try:
                if env_path.exists():
                    with open(env_path) as f:
                        for line in f:
                            if line.startswith("OPENAI_API_KEY="):
                                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                                if len(k) > 10:
                                    self.openai_api_key = k
                                    return k
            except Exception:
                pass
            return ""
        elif p == "nvidia":
            if self.nvidia_api_key and len(self.nvidia_api_key.strip()) > 10:
                return self.nvidia_api_key.strip()
            env_key = os.getenv("NVIDIA_API_KEY", "").strip()
            if env_key and len(env_key) > 10:
                self.nvidia_api_key = env_key
                return env_key
            try:
                if env_path.exists():
                    with open(env_path) as f:
                        for line in f:
                            if line.startswith("NVIDIA_API_KEY="):
                                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                                if len(k) > 10:
                                    self.nvidia_api_key = k
                                    return k
            except Exception:
                pass
            return ""
        return ""

    def _build_grounding_context(self, state_context: dict = None) -> str:
        if not state_context:
            return ""
        jurisdiction = state_context.get("jurisdiction", "india").lower()
        herbs = [b.get("common_name", "") for b in state_context.get("detected_botanicals", [])]
        herbs_str = ", ".join(herbs) if herbs else "General herbal ingredients"
        dosage = state_context.get("dosage_form", "Standard formulation")
        workaround = state_context.get("strategic_workaround", "")
        collisions = state_context.get("detected_collisions", [])

        vern_list = state_context.get("vernacular_mappings", {}).get("recognized_vernaculars", [])
        vern_str = ""
        if vern_list:
            v_lines = []
            for v in vern_list:
                v_lines.append(
                    f"Spoken '{v['spoken_vernacular'].title()}' ({v['traditional_system']} / {v['language_origin']}) -> "
                    f"Standardized {v['latin_name']} ({v['canonical_name']}) | Monograph: {v['pharmacopoeia_monograph']} | "
                    f"TKRC: {v['tkrc_code']} | Marker: {v['active_chemical_marker']}"
                )
            vern_str = "\n- Traditional Dialect & Pharmacopoeial Mapping:\n  * " + "\n  * ".join(v_lines)

        if jurisdiction == "international":
            wipo_stat = state_context.get("wipo_evaluation", {}).get("status", "Mandatory Disclosure Active")
            cbd_stat = state_context.get("cbd_evaluation", {}).get("status", "PIC & Benefit Sharing")
            eu_stat = state_context.get("eu_evaluation", {}).get("status", "THMPD Registration")
            us_stat = state_context.get("us_evaluation", {}).get("status", "DSHEA / Botanical Guidance")

            return f"""
MULTI-AGENT STATUTORY STATE-GRAPH CONTEXT (INTERNATIONAL JURISDICTION):
- Active Jurisdiction: International (Global Treaties & Regional Authorities)
- Detected Botanicals: {herbs_str}
- Dosage Form: {dosage}{vern_str}
- WIPO GRATK Treaty (2024) Mandatory Disclosure: {wipo_stat}
- CBD Nagoya Protocol ABS & Budapest Treaty: {cbd_stat}
- EU EMA & THMPD Directive 2004/24/EC: {eu_stat}
- US FDA Botanical Guidance & DSHEA: {us_stat}
- Cross-Border Collisions Detected: {'; '.join(collisions) if collisions else 'No direct fatal collision'}
- Recommended Strategic Workaround: {workaround}
"""

        ipo_stat = state_context.get("ipo_evaluation", {}).get("status", "")
        nba_stat = state_context.get("nba_evaluation", {}).get("status", "")
        ayush_stat = state_context.get("ayush_evaluation", {}).get("status", "")
        allied_stat = state_context.get("allied_evaluation", {}).get("status", "FSSAI/DMROA Compliant")

        return f"""
MULTI-AGENT STATUTORY STATE-GRAPH CONTEXT (INDIA JURISDICTION):
- Active Jurisdiction: National (India)
- Detected Botanicals: {herbs_str}
- Dosage Form: {dosage}{vern_str}
- Patent Office (Section 3p/3e) Evaluation: {ipo_stat}
- Biodiversity Board (Section 6) Evaluation: {nba_stat}
- Ayush Licensing (Rule 158-B) Evaluation: {ayush_stat}
- Allied Regimes (FSSAI Ayurveda-Aahar & DMROA 1954): {allied_stat}
- Cross-Regulatory Collisions Detected: {'; '.join(collisions) if collisions else 'No direct fatal collision'}
- Recommended Strategic Workaround: {workaround}
"""

    @traceable(name="IP_SAKTI_LLM_Query", run_type="llm")
    def query(self, user_query: str, domain: str = "Ayurveda", language: str = "en", state_context: dict = None) -> dict:
        """
        Executes query with multi-provider routing:
        1. OpenAI API (if OpenAI provider active & key present)
        2. NVIDIA NIM API (if NVIDIA provider active & key present)
        3. Local Ollama LLM (if Ollama provider active on localhost:11434)
        4. Structured Multi-Agent StateGraph Legal Synthesis
        """
        sync_langsmith_config()
        grounding_context = self._build_grounding_context(state_context)
        jurisdiction = (state_context.get("jurisdiction", "india") if state_context else "india").lower()

        if jurisdiction == "international":
            if language == "hi":
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate global patent treaties and cross-border regulatory compliance in fluent, authoritative Hindi:
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Structure with:
  ### 1. WIPO एवं GRATK संधि 2024 (अनिवार्य पूर्वज प्रकटीकरण)
  ### 2. CBD, नगोया प्रोटोकॉल ABS एवं बुडापेस्ट संधि
  ### 3. यूरोपीय संघ EMA एवं THMPD (निर्देश 2004/24/EC)
  ### 4. यूएस एफडीए एवं वैश्विक विनियामक (DSHEA / वानस्पतिक औषधियां)
  ### 5. वैश्विक पेटेंट संरक्षण एवं निर्यात अनुपालन रणनीति
- Output ONLY the final report in fluent Hindi. Start immediately with '###'. Under 350 words."""
            else:
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate global patent treaties and international market compliance:
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Respond ONLY in professional English using clean markdown.
- Structure with:
  ### 1. WIPO & Diplomatic Conference GRATK Treaty (2024)
  ### 2. CBD, Nagoya Protocol ABS & Budapest Treaty
  ### 3. European Union Herbal Medicine Regime (EMA / Directive 2004/24/EC THMPD)
  ### 4. US FDA & FTC Regime (Botanical Drug Guidance / DSHEA)
  ### 5. Actionable Strategy & International Filing Roadmap
- Output ONLY the final report in fluent English. Start immediately with '###'. Under 350 words."""
        else:
            if language == "hi":
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate patentability and regulatory compliance under Indian Law in fluent, authoritative Hindi (हिंदी भाषा में संपूर्ण उत्तर दें):
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Respond in fluent, formal Hindi (Devanagari script) using clean markdown. Keep statutory section citations clear (धारा 3(p), धारा 3(e), धारा 6, नियम 158-B) and Latin botanical names in parentheses.
- Structure with:
  ### 1. भारतीय पेटेंट कार्यालय (IPO) निष्कर्ष एवं धारा 3(p)/3(e) विश्लेषण
  ### 2. राष्ट्रीय जैव विविधता प्राधिकरण (NBA) प्रपत्र 3 पूर्व अनुमोदन (धारा 6)
  ### 3. राज्य आयुष लाइसेंसिंग प्राधिकरण (नियम 158-B शास्त्रीय बनाम प्रोप्राइटरी ASU)
  ### 4. संबद्ध विनियामक प्रणालियाँ (FSSAI आयुर्वेद-आहार, DMROA 1954 एवं प्रसाधन)
  ### 5. पेटेंट योग्य व्यावहारिक रणनीति एवं सहक्रियात्मक फॉर्मूलेशन रोडमैप
- Output ONLY the final report in fluent Hindi. Start immediately with '###'. Under 350 words."""
            else:
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate patentability and regulatory compliance under Indian Law:
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Respond ONLY in professional English using clean markdown.
- Structure with:
  ### 1. Indian Patent Office (IPO) Verdict & Section 3(p)/3(e) Analysis
  ### 2. National Biodiversity Authority (NBA) Mandate & Form 3 Prior Approval (Section 6)
  ### 3. State Ayush Licensing Authority (Rule 158-B Classical vs Proprietary ASU)
  ### 4. Allied Regimes (FSSAI Ayurveda-Aahar, DMROA 1954 & Cosmetics)
  ### 5. Actionable Patent Workaround & Synergistic Formulation Roadmap
- Output ONLY the final report in fluent English. Start immediately with '###'. Under 350 words."""

        # 1. OpenAI Route
        if self.provider == "openai":
            openai_key = self.get_api_key("openai")
            if openai_key:
                headers = {
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model if (self.model and not self.model.startswith("nvidia/")) else "gpt-4o",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt_content}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 850
                }
                try:
                    resp = requests.post(OPENAI_BASE_URL, headers=headers, json=payload, timeout=25)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        if "###" in content:
                            content = "###" + content.split("###", 1)[1]
                        return {
                            "status": "success",
                            "source": "openai",
                            "model": payload["model"],
                            "raw_response": content
                        }
                    else:
                        print(f"[OpenAI API Error] Status: {resp.status_code}, Response: {resp.text}")
                except Exception as e:
                    print(f"[OpenAI Network Error]: {e}")

        # 2. NVIDIA NIM Route
        elif self.provider == "nvidia":
            nvidia_key = self.get_api_key("nvidia")
            if nvidia_key:
                headers = {
                    "Authorization": f"Bearer {nvidia_key}",
                    "Content-Type": "application/json"
                }
                models_to_try = [self.model, "nvidia/nemotron-3.5-lightning-30b-a3b"]
                for target_model in models_to_try:
                    payload = {
                        "model": target_model,
                        "messages": [{"role": "user", "content": prompt_content}],
                        "temperature": 0.2,
                        "max_tokens": 850
                    }
                    try:
                        resp = requests.post(NVIDIA_BASE_URL, headers=headers, json=payload, timeout=35)
                        if resp.status_code == 200:
                            data = resp.json()
                            content = data["choices"][0]["message"]["content"]
                            if "###" in content:
                                content = "###" + content.split("###", 1)[1]
                            return {
                                "status": "success",
                                "source": "nvidia_nim",
                                "model": target_model,
                                "raw_response": content
                            }
                        elif resp.status_code == 503:
                            continue
                        else:
                            print(f"[NVIDIA NIM Error] Model: {target_model}, Status: {resp.status_code}")
                    except Exception as e:
                        print(f"[NVIDIA NIM Network Error]: {e}")
                        break

        # 3. Local Ollama Route (Offline, Zero Key)
        if self.provider == "ollama" or (not self.get_api_key("openai") and not self.get_api_key("nvidia")):
            try:
                ollama_url = f"{self.ollama_url.rstrip('/')}/api/generate"
                ollama_payload = {
                    "model": self.model if not self.model.startswith(("nvidia/", "gpt-")) else self.ollama_model,
                    "prompt": f"{SYSTEM_PROMPT}\n\n{prompt_content}",
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 350}
                }
                ollama_resp = requests.post(ollama_url, json=ollama_payload, timeout=7)
                if ollama_resp.status_code == 200:
                    raw_text = ollama_resp.json().get("response", "").strip()
                    if raw_text and len(raw_text) > 80:
                        return {
                            "status": "success",
                            "source": "local_ollama",
                            "model": f"Ollama ({ollama_payload['model']})",
                            "raw_response": raw_text
                        }
            except Exception as oe:
                pass

        # 4. Fallback: Return StateGraph structured synthesis
        return {
            "status": "fallback",
            "source": "state_graph_rules",
            "message": "Cloud LLM offline or key not configured. Using verified multi-agent StateGraph legal synthesis.",
            "model": self.model,
            "fallback_used": True
        }

    async def stream_query(self, user_query: str, domain: str = "Ayurveda", language: str = "en", state_context: dict = None):
        """
        Asynchronously streams response tokens across OpenAI, NVIDIA, Ollama, or StateGraph.
        Yields dict: {"token": str, "source": str, "model": str}
        """
        grounding_context = self._build_grounding_context(state_context)
        jurisdiction = (state_context.get("jurisdiction", "india") if state_context else "india").lower()

        if jurisdiction == "international":
            if language == "hi":
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate global patent treaties and cross-border regulatory compliance in fluent, authoritative Hindi:
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Structure with:
  ### 1. WIPO एवं GRATK संधि 2024 (अनिवार्य पूर्वज प्रकटीकरण)
  ### 2. CBD, नगोया प्रोटोकॉल ABS एवं बुडापेस्ट संधि
  ### 3. यूरोपीय संघ EMA एवं THMPD (निर्देश 2004/24/EC)
  ### 4. यूएस एफडीए एवं वैश्विक विनियामक (DSHEA / वानस्पतिक औषधियां)
  ### 5. वैश्विक पेटेंट संरक्षण एवं निर्यात अनुपालन रणनीति
- Output ONLY the final report in fluent Hindi. Start immediately with '###'. Under 350 words."""
            else:
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate global patent treaties and international market compliance:
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Respond ONLY in professional English using clean markdown.
- Structure with:
  ### 1. WIPO & Diplomatic Conference GRATK Treaty (2024)
  ### 2. CBD, Nagoya Protocol ABS & Budapest Treaty
  ### 3. European Union Herbal Medicine Regime (EMA / Directive 2004/24/EC THMPD)
  ### 4. US FDA & FTC Regime (Botanical Drug Guidance / DSHEA)
  ### 5. Actionable Strategy & International Filing Roadmap
- Output ONLY the final report. Start immediately with '###'. Under 350 words."""
        else:
            if language == "hi":
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate patentability and regulatory compliance under Indian Law in fluent, authoritative Hindi (हिंदी भाषा में संपूर्ण उत्तर दें):
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Respond in fluent, formal Hindi (Devanagari script) using clean markdown. Keep statutory section citations clear (धारा 3(p), धारा 3(e), धारा 6, नियम 158-B) and Latin botanical names in parentheses.
- Structure with:
  ### 1. भारतीय पेटेंट कार्यालय (IPO) निष्कर्ष एवं धारा 3(p)/3(e) विश्लेषण
  ### 2. राष्ट्रीय जैव विविधता प्राधिकरण (NBA) प्रपत्र 3 पूर्व अनुमोदन (धारा 6)
  ### 3. राज्य आयुष लाइसेंसिंग प्राधिकरण (नियम 158-B शास्त्रीय बनाम प्रोप्राइटरी ASU)
  ### 4. संबद्ध विनियामक प्रणालियाँ (FSSAI आयुर्वेद-आहार, DMROA 1954 एवं प्रसाधन)
  ### 5. पेटेंट योग्य व्यावहारिक रणनीति एवं सहक्रियात्मक फॉर्मूलेशन रोडमैप
- Output ONLY the final report in fluent Hindi. Start immediately with '###'. Under 350 words."""
            else:
                prompt_content = f"""You are IP-SAKTI Sahayak, regulatory AI for Ministry of Ayush, Government of India.
Evaluate patentability and regulatory compliance under Indian Law:
- User Inquiry: {user_query}
{grounding_context}

CRITICAL RULES:
- Respond ONLY in professional English using clean markdown.
- Structure with:
  ### 1. Indian Patent Office (IPO) Verdict & Section 3(p)/3(e) Analysis
  ### 2. National Biodiversity Authority (NBA) Mandate & Form 3 Prior Approval (Section 6)
  ### 3. State Ayush Licensing Authority (Rule 158-B Classical vs Proprietary ASU)
  ### 4. Allied Regimes (FSSAI Ayurveda-Aahar, DMROA 1954 & Cosmetics)
  ### 5. Actionable Patent Workaround & Synergistic Formulation Roadmap
- Output ONLY the final report. Start immediately with '###'. Under 350 words."""

        loop = asyncio.get_event_loop()

        # 1. OpenAI Streaming
        if self.provider == "openai":
            openai_key = self.get_api_key("openai")
            if openai_key:
                headers = {
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                }
                target_model = self.model if (self.model and not self.model.startswith("nvidia/")) else "gpt-4o"
                payload = {
                    "model": target_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt_content}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800,
                    "stream": True
                }
                try:
                    def fetch_openai():
                        return requests.post(OPENAI_BASE_URL, headers=headers, json=payload, stream=True, timeout=10)

                    resp = await loop.run_in_executor(None, fetch_openai)
                    if resp.status_code == 200:
                        for line in resp.iter_lines():
                            if line:
                                decoded = line.decode("utf-8")
                                if decoded.startswith("data: "):
                                    data_str = decoded[6:].strip()
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data_str)
                                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        if delta:
                                            yield {"token": delta, "source": "openai", "model": target_model}
                                    except Exception:
                                        continue
                        return
                except Exception as e:
                    print(f"[OpenAI Stream Exception]: {e}")

        # 2. NVIDIA NIM Streaming
        elif self.provider == "nvidia":
            nvidia_key = self.get_api_key("nvidia")
            if nvidia_key:
                headers = {
                    "Authorization": f"Bearer {nvidia_key}",
                    "Content-Type": "application/json"
                }
                target_model = self.model if self.model.startswith("nvidia/") or self.model.startswith("meta/") else "nvidia/nemotron-3.5-lightning-30b-a3b"
                payload = {
                    "model": target_model,
                    "messages": [{"role": "user", "content": prompt_content}],
                    "temperature": 0.2,
                    "max_tokens": 800,
                    "stream": True
                }
                try:
                    def fetch_nvidia():
                        return requests.post(NVIDIA_BASE_URL, headers=headers, json=payload, stream=True, timeout=30)

                    resp = await loop.run_in_executor(None, fetch_nvidia)
                    if resp.status_code == 200:
                        accumulated = ""
                        started_output = False
                        for line in resp.iter_lines():
                            if line:
                                decoded = line.decode("utf-8")
                                if decoded.startswith("data: "):
                                    data_str = decoded[6:].strip()
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data_str)
                                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        if delta:
                                            accumulated += delta
                                            if not started_output:
                                                markers = ["### 1.", "### Indian", "### Traditional", "### Statutory", "### Patents", "### Section"]
                                                found_marker = None
                                                for m in markers:
                                                    if m in accumulated:
                                                        found_marker = m
                                                        break
                                                if found_marker:
                                                    started_output = True
                                                    after_hash = found_marker + accumulated.split(found_marker, 1)[1]
                                                    yield {"token": after_hash, "source": "nvidia_nim", "model": target_model}
                                            else:
                                                yield {"token": delta, "source": "nvidia_nim", "model": target_model}
                                    except Exception:
                                        continue
                        if started_output:
                            return
                except Exception as e:
                    print(f"[NVIDIA Stream Exception]: {e}")

        # 3. Stream StateGraph Grounded Summary with micro-cadence
        summary_text = state_context.get("summary", "") if state_context else ""
        if not summary_text:
            summary_text = "Multi-agent statutory analysis complete. Grounded against official government gazettes."
        
        words = summary_text.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            yield {"token": token, "source": "state_graph_rules", "model": "StateGraph Grounded Engine"}
            await asyncio.sleep(0.012)

    @traceable(name="IP_SAKTI_Goal_Roadmap", run_type="llm")
    def generate_custom_roadmap_json(self, goal_query: str, state_context: dict = None) -> Optional[dict]:
        """
        Synthesizes a query-specific 6-stage milestone roadmap in JSON format using LLM.
        """
        sync_langsmith_config()
        grounding_context = self._build_grounding_context(state_context)
        prompt_content = f"""You are IP-SAKTI Regulatory Architect for the Ministry of Ayush, Government of India.
Construct an authoritative, customized 6-stage regulatory roadmap for the user's specific innovation goal:
Goal: "{goal_query}"
{grounding_context}

CRITICAL INSTRUCTIONS:
1. Generate exactly 6 progressive milestones tailored directly to THIS specific formulation, botanicals, and statutory goal.
2. DO NOT use the section symbol. Always write "Section " explicitly.
3. Respond ONLY with a valid JSON object in the exact format:
{{
  "title": "Short Project Title (3-6 words)",
  "stages": [
    {{
      "id": "stage_1",
      "order": 1,
      "title": "Concise Stage Title (2-4 words)",
      "timeline": "Weeks 1-3",
      "authority": "Governing Authority Name",
      "statute": "Statutory citation (write Section without symbol)",
      "description": "Specific regulatory milestone action for this exact goal.",
      "mandates": ["Statutory requirement 1", "Statutory requirement 2"],
      "completed": false
    }}
  ]
}}
DO NOT include markdown fences (no ```json). Output pure JSON only."""

        # 1. OpenAI
        if self.provider == "openai":
            openai_key = self.get_api_key("openai")
            if openai_key:
                headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
                target_model = self.model if (self.model and not self.model.startswith("nvidia/")) else "gpt-4o"
                payload = {
                    "model": target_model,
                    "messages": [
                        {"role": "system", "content": "You are a regulatory legal architect that outputs strictly pure valid JSON."},
                        {"role": "user", "content": prompt_content}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1200
                }
                try:
                    resp = requests.post(OPENAI_BASE_URL, headers=headers, json=payload, timeout=12)
                    if resp.status_code == 200:
                        text = resp.json()["choices"][0]["message"]["content"]
                        return self._parse_json_safe(text)
                except Exception as e:
                    print(f"[OpenAI Roadmap Error]: {e}")

        # 2. NVIDIA NIM
        elif self.provider == "nvidia":
            nvidia_key = self.get_api_key("nvidia")
            if nvidia_key:
                headers = {"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"}
                models_to_try = ["nvidia/nemotron-3.5-lightning-30b-a3b"]
                for target_model in models_to_try:
                    payload = {
                        "model": target_model,
                        "messages": [
                            {"role": "system", "content": "You are a regulatory legal architect that outputs strictly pure valid JSON."},
                            {"role": "user", "content": prompt_content}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1200
                    }
                    try:
                        resp = requests.post(NVIDIA_BASE_URL, headers=headers, json=payload, timeout=35)
                        if resp.status_code == 200:
                            text = resp.json()["choices"][0]["message"]["content"]
                            parsed = self._parse_json_safe(text)
                            if parsed:
                                return parsed
                    except Exception as e:
                        print(f"[NVIDIA NIM Roadmap Error]: {e}")
                        continue

        # 3. Ollama
        if self.provider == "ollama" or (not self.get_api_key("openai") and not self.get_api_key("nvidia")):
            try:
                ollama_url = f"{self.ollama_url.rstrip('/')}/api/generate"
                ollama_payload = {
                    "model": self.model if not self.model.startswith(("nvidia/", "gpt-")) else self.ollama_model,
                    "prompt": prompt_content,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.2, "num_predict": 800}
                }
                ollama_resp = requests.post(ollama_url, json=ollama_payload, timeout=8)
                if ollama_resp.status_code == 200:
                    text = ollama_resp.json().get("response", "")
                    return self._parse_json_safe(text)
            except Exception as e:
                print(f"[Ollama Roadmap Error]: {e}")

        return None

    def _parse_json_safe(self, text: str) -> Optional[dict]:
        if not text:
            return None
        clean = text.strip()
        if "```json" in clean:
            clean = clean.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in clean:
            clean = clean.split("```", 1)[1].split("```", 1)[0]
        clean = clean.strip()
        
        start_idx = clean.find("{")
        end_idx = clean.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            clean = clean[start_idx:end_idx + 1]
            
        try:
            data = json.loads(clean)
            if "stages" in data and isinstance(data["stages"], list) and len(data["stages"]) >= 3:
                return data
        except Exception:
            pass
        return None

