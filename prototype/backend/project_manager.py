"""
Project Manager & Dedicated Workspace Engine for IP-SAKTI Sahayak (Pro / Enterprise Tier)
Handles:
1. Dedicated Project Dossiers (ChatGPT Projects Style)
2. 6-Stage Dynamic Milestone Roadmap Graphs
3. Official Ministry of Ayush Mentor Gateway & Token Verification
"""

import time
import uuid
from typing import Dict, Any, List, Optional

# Verified Ministry of Ayush Mentor Tokens & Profiles
AYUSH_MENTOR_REGISTRY = {
    "AYUSH-MENTOR-2026-X89": {
        "mentor_id": "mentor_01",
        "name": "Dr. Rajesh K. Sharma, MD (Ayu), PhD",
        "designation": "Former Joint Advisor (Ayurveda), Ministry of Ayush & Technical Member (IPAB)",
        "department": "Department of Traditional Medicine & Statutory IPR Cell",
        "specialization": "Patent Act Section 3(p) Defensibility & TKDL Prior Art Neutralization",
        "location": "Ayush Bhawan, GPO Complex, INA, New Delhi",
        "badge": "🏛️ Verified Ministry of Ayush Mentor",
        "available_slots": ["Tomorrow 11:30 AM IST", "Thursday 03:00 PM IST", "Friday 04:30 PM IST"],
        "token_tier": "VIP Official Ayush Ministry Advisory"
    },
    "AYUSH-SIDDHA-2026-M42": {
        "mentor_id": "mentor_02",
        "name": "Dr. S. Meenakshi Sundaram, MD (Siddha)",
        "designation": "Senior Member, Siddha Pharmacopoeia Committee (PCIM&H)",
        "department": "Pharmacopoeia Commission for Indian Medicine & Homoeopathy",
        "specialization": "SPI Standardization, Rule 158-B Proprietary ASU Licensing & Heavy Metal Safety",
        "location": "National Institute of Siddha, Chennai / New Delhi",
        "badge": "🏛️ Verified PCIM&H Pharmacopoeial Mentor",
        "available_slots": ["Wednesday 02:00 PM IST", "Friday 11:00 AM IST"],
        "token_tier": "Statutory Pharmacopoeia Advisory"
    },
    "AYUSH-GOV-PRO-99": {
        "mentor_id": "mentor_03",
        "name": "Dr. Ananya Sengupta, LLM (IPR), PhD (Phytochem)",
        "designation": "Director of Biodiversity Legal Cell & Former NBA Legal Counsel",
        "department": "National Biodiversity Authority Advisory Panel",
        "specialization": "Biological Diversity Act Section 6 Form 3 Approvals & ABS Benefit Sharing",
        "location": "TICEL Bio Park, Taramani, Chennai",
        "badge": "🌿 Verified NBA Statutory Advisor",
        "available_slots": ["Thursday 10:30 AM IST", "Monday 04:00 PM IST"],
        "token_tier": "National Biodiversity Legal Advisory"
    }
}

# Standard 6-Stage Regulatory Milestone Framework
DEFAULT_MILESTONE_STAGES = [
    {
        "id": "stage_1",
        "order": 1,
        "name": "Formulation Ideation & TKDL Pre-Screening",
        "authority": "Indian Patent Office (IPO) / CSIR-TKDL",
        "statute": "Patents Act Section 3(p)",
        "status": "completed",
        "completion_pct": 100,
        "deliverable": "TKDL Prior Art Clearance & Botanical NER Normalization Report",
        "notes": "Verified against 250,000+ formulations. Crude mixture tagged for non-obvious delivery reform."
    },
    {
        "id": "stage_2",
        "order": 2,
        "name": "Synergy Assay & Nanocarrier Design",
        "authority": "Ayush R&D / Analytical Phyto-Lab",
        "statute": "Patents Act Section 3(e) Synergism",
        "status": "completed",
        "completion_pct": 100,
        "deliverable": "Chou-Talalay Assay Dossier (CI < 0.72) & Phospholipid Nanocarrier Spec",
        "notes": "Demonstrated 4.8x transdermal bioavailability overcoming mere admixture objection."
    },
    {
        "id": "stage_3",
        "order": 3,
        "name": "NBA Form 3 Prior Approval Filing",
        "authority": "National Biodiversity Authority (NBA)",
        "statute": "BD Act, 2002 Section 6(1)",
        "status": "in_progress",
        "completion_pct": 60,
        "deliverable": "Form III Application Draft & ABS Ex-Factory Royalty Undertaking",
        "notes": "Filed prior to patent grant to avoid Section 55 criminal liabilities (imprisonment up to 5 yrs)."
    },
    {
        "id": "stage_4",
        "order": 4,
        "name": "State Ayush Rule 158-B Dossier",
        "authority": "State Ayush Licensing Authority (SALA)",
        "statute": "D&C Rules, 1945 Rule 158-B",
        "status": "in_progress",
        "completion_pct": 40,
        "deliverable": "Proprietary ASU Medicine Manufacturing License (Form 24-D)",
        "notes": "Schedule T 1,200 sq. ft. cleanroom inspection dossier & active marker batch certificates."
    },
    {
        "id": "stage_5",
        "order": 5,
        "name": "1-on-1 Ayush Ministry Mentor Checkpoint",
        "authority": "Ministry of Ayush Advisory Cell",
        "statute": "Official Statutory Review",
        "status": "pending",
        "completion_pct": 0,
        "deliverable": "Dossier Review & Pre-Filing Recommendation Certificate",
        "notes": "Requires token verification: Direct consultation with designated Ministry of Ayush Mentor."
    },
    {
        "id": "stage_6",
        "order": 6,
        "name": "Commercial Launch & Global Export",
        "authority": "WIPO / EU EMA / US FDA",
        "statute": "EU THMPD Directive / FDA DSHEA",
        "status": "pending",
        "completion_pct": 0,
        "deliverable": "International Harmonization Package & WIPO PCT Filing",
        "notes": "Preparation of 15-year European safety dossier and US DSHEA Structure-Function labeling."
    }
]

# Dedicated Projects In-Memory Store with Rich Pre-Loaded Datasets
PROJECTS_STORE: Dict[str, Dict[str, Any]] = {
    "proj_ayur_rheuma": {
        "id": "proj_ayur_rheuma",
        "name": "Project AyurRheuma-Gel",
        "applicant": "BioAyur Innovations Pvt. Ltd.",
        "description": "Standardized Liposomal Phytopharmaceutical Nanocarrier for Topical Osteoarthritis Relief",
        "botanicals": ["Curcuma longa (Curcumin)", "Gaultheria procumbens (Gandhapura)", "Boswellia serrata (Shallaki)"],
        "dosage_form": "Liposomal / Phospholipid Nanocarrier (Particle Size < 120 nm)",
        "domain": "Ayurveda & Phytopharmaceuticals",
        "target_markets": ["India (Domestic)", "European Union (Germany)", "United States"],
        "tier": "pro",
        "current_stage": 3,
        "overall_progress_pct": 68,
        "assigned_mentor": None,
        "mentor_session_active": False,
        "milestones": [
            dict(DEFAULT_MILESTONE_STAGES[0], status="completed", completion_pct=100),
            dict(DEFAULT_MILESTONE_STAGES[1], status="completed", completion_pct=100),
            dict(DEFAULT_MILESTONE_STAGES[2], status="in_progress", completion_pct=75),
            dict(DEFAULT_MILESTONE_STAGES[3], status="in_progress", completion_pct=45),
            dict(DEFAULT_MILESTONE_STAGES[4], status="pending", completion_pct=0),
            dict(DEFAULT_MILESTONE_STAGES[5], status="pending", completion_pct=0)
        ],
        "created_at": "2026-08-20T10:00:00Z",
        "updated_at": "2026-09-09T08:30:00Z"
    },
    "proj_immuno_boost": {
        "id": "proj_immuno_boost",
        "name": "Project ImmunoVeda-Pro",
        "applicant": "Vedic Phytoceuticals Ltd.",
        "description": "Standardized Supercritical CO2 Fraction of Asgandh & Kalmegh for Immunomodulation",
        "botanicals": ["Withania somnifera (Asgandh / Ashwagandha)", "Andrographis paniculata (Kalmegh / Nilavembu)", "Piper nigrum (Filfil Siyah)"],
        "dosage_form": "Standardized Supercritical CO2 Extract with Bioavailability Enhancer",
        "domain": "Integrated AYUSH (Ayurveda + Unani + Siddha)",
        "target_markets": ["India", "UAE (MoHAP)", "United Kingdom"],
        "tier": "pro",
        "current_stage": 4,
        "overall_progress_pct": 82,
        "assigned_mentor": "Dr. Rajesh K. Sharma, MD (Ayu), PhD",
        "mentor_session_active": True,
        "milestones": [
            dict(DEFAULT_MILESTONE_STAGES[0], status="completed", completion_pct=100),
            dict(DEFAULT_MILESTONE_STAGES[1], status="completed", completion_pct=100),
            dict(DEFAULT_MILESTONE_STAGES[2], status="completed", completion_pct=100),
            dict(DEFAULT_MILESTONE_STAGES[3], status="completed", completion_pct=100),
            dict(DEFAULT_MILESTONE_STAGES[4], status="in_progress", completion_pct=80),
            dict(DEFAULT_MILESTONE_STAGES[5], status="pending", completion_pct=10)
        ],
        "created_at": "2026-07-15T14:30:00Z",
        "updated_at": "2026-09-09T09:15:00Z"
    }
}

class ProjectManager:
    """Manages dedicated projects, milestone graphs, and mentor verification."""

    @staticmethod
    def list_projects() -> List[Dict[str, Any]]:
        return list(PROJECTS_STORE.values())

    @staticmethod
    def get_project(project_id: str) -> Optional[Dict[str, Any]]:
        return PROJECTS_STORE.get(project_id)

    @staticmethod
    def create_project(data: Dict[str, Any]) -> Dict[str, Any]:
        proj_id = f"proj_{uuid.uuid4().hex[:8]}"
        name = data.get("name", "Untitled Regulatory Project")
        applicant = data.get("applicant", "Ayush Research Scholar")
        botanicals = data.get("botanicals", ["Curcuma longa"])
        dosage = data.get("dosage_form", "Standardized Supercritical Extract")
        domain = data.get("domain", "Ayurveda")
        markets = data.get("target_markets", ["India"])

        new_proj = {
            "id": proj_id,
            "name": name,
            "applicant": applicant,
            "description": data.get("description", f"Dossier for {name} with {len(botanicals)} botanicals."),
            "botanicals": botanicals,
            "dosage_form": dosage,
            "domain": domain,
            "target_markets": markets,
            "tier": "pro",
            "current_stage": 1,
            "overall_progress_pct": 20,
            "assigned_mentor": None,
            "mentor_session_active": False,
            "milestones": [
                dict(DEFAULT_MILESTONE_STAGES[0], status="in_progress", completion_pct=60),
                dict(DEFAULT_MILESTONE_STAGES[1], status="pending", completion_pct=0),
                dict(DEFAULT_MILESTONE_STAGES[2], status="pending", completion_pct=0),
                dict(DEFAULT_MILESTONE_STAGES[3], status="pending", completion_pct=0),
                dict(DEFAULT_MILESTONE_STAGES[4], status="pending", completion_pct=0),
                dict(DEFAULT_MILESTONE_STAGES[5], status="pending", completion_pct=0)
            ],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        PROJECTS_STORE[proj_id] = new_proj
        return new_proj

    @staticmethod
    def advance_stage(project_id: str, stage_id: str, new_pct: int = 100) -> Optional[Dict[str, Any]]:
        proj = PROJECTS_STORE.get(project_id)
        if not proj:
            return None

        total_pct = 0
        found = False
        for i, m in enumerate(proj["milestones"]):
            if m["id"] == stage_id:
                found = True
                m["completion_pct"] = new_pct
                if new_pct >= 100:
                    m["status"] = "completed"
                    # Unlock next stage if exists
                    if i + 1 < len(proj["milestones"]):
                        proj["milestones"][i + 1]["status"] = "in_progress"
                        proj["current_stage"] = i + 2
                else:
                    m["status"] = "in_progress"
            total_pct += m["completion_pct"]

        proj["overall_progress_pct"] = round(total_pct / len(proj["milestones"]))
        proj["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return proj

    @staticmethod
    def verify_mentor_token(project_id: str, token_code: str) -> Dict[str, Any]:
        token_clean = token_code.strip().upper()
        mentor_info = AYUSH_MENTOR_REGISTRY.get(token_clean)

        if not mentor_info:
            return {
                "status": "error",
                "message": "Invalid Ministry of Ayush Mentor Token. Please check official authorization credentials."
            }

        proj = PROJECTS_STORE.get(project_id)
        if proj:
            proj["assigned_mentor"] = mentor_info["name"]
            proj["mentor_session_active"] = True
            # Unlock stage 5
            for m in proj["milestones"]:
                if m["id"] == "stage_5":
                    m["status"] = "in_progress"
                    m["completion_pct"] = 50
                    m["notes"] = f"Official Ayush Mentor {mentor_info['name']} assigned via Token {token_clean}."

        return {
            "status": "success",
            "message": "✓ Official Ministry of Ayush Mentor Successfully Verified & Assigned",
            "mentor": mentor_info,
            "project_id": project_id
        }

project_manager = ProjectManager()
