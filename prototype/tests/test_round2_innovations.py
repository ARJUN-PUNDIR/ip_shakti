"""
Automated Test Suite for Round 2 Innovations:
1. Standardized Model Context Protocol (MCP) Server (6 Tools)
2. Dedicated Regulatory Project Studio & 6-Stage Milestone Roadmap Graph
3. Official Ministry of Ayush Mentor Gateway & Token Verification
4. Official Government Gazette Hyperlinks
"""

import sys
import unittest
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import mcp_server
from project_manager import project_manager, AYUSH_MENTOR_REGISTRY
from legal_kb import GAZETTE_REGISTRY


class TestRound2Innovations(unittest.TestCase):
    """Automated test cases for MCP, Pro Studio, and Mentor Gateway."""

    def test_01_mcp_tools_registry(self):
        """Verifies all 6 standardized MCP tools are defined with JSON schemas."""
        tools = mcp_server.list_tools()
        self.assertEqual(len(tools), 6)
        tool_names = [t["name"] for t in tools]
        expected = [
            "screen_patentability",
            "check_nba_clearance",
            "get_ayush_licensing",
            "calculate_abs_royalty",
            "resolve_vernacular_botanical",
            "get_gazette_citation"
        ]
        for exp in expected:
            self.assertIn(exp, tool_names)

    def test_02_mcp_tool_execution(self):
        """Tests live execution of all 6 MCP tools."""
        # 1. screen_patentability
        res1 = mcp_server.execute_tool("screen_patentability", {
            "botanicals": ["Curcuma longa", "Wintergreen Oil"],
            "dosage_form": "Liposomal Nanocarrier"
        })
        self.assertTrue(res1["section_3p_barred"] or "Defensible" in res1["verdict"] or "Screening" in res1["verdict"])
        self.assertGreaterEqual(res1["formulation_score"], 80)

        # 2. check_nba_clearance
        res2 = mcp_server.execute_tool("check_nba_clearance", {
            "biological_resources": ["Withania somnifera"],
            "applicant_type": "Indian Citizen / Company"
        })
        self.assertIn("Section 6", res2["statutory_mandate"])
        self.assertIn("Form III", res2["applicable_form"])

        # 3. get_ayush_licensing
        res3 = mcp_server.execute_tool("get_ayush_licensing", {
            "category": "Ayurvedic Proprietary Medicine (Patent / Novel Formulation)",
            "ingredients": ["Curcumin", "Shallaki"]
        })
        self.assertIn("Rule 158-B(II)", res3["statutory_rule"])

        # 4. calculate_abs_royalty
        res4 = mcp_server.execute_tool("calculate_abs_royalty", {
            "annual_gross_ex_factory_sale_inr": 25000000
        })
        self.assertEqual(res4["calculated_abs_royalty_inr"], 50000.0)
        self.assertIn("0.2%", res4["applied_rate"])

        # 5. resolve_vernacular_botanical
        res5 = mcp_server.execute_tool("resolve_vernacular_botanical", {
            "vernacular_term": "Asgandh Nagori"
        })
        self.assertEqual(res5["status"], "matched")
        self.assertEqual(res5["canonical_name"], "Ashwagandha")

        # 6. get_gazette_citation
        res6 = mcp_server.execute_tool("get_gazette_citation", {
            "doc_id": "patent_act_3p"
        })
        self.assertIn("Section 3", res6["chapter_section"])
        self.assertTrue("wipo.int" in res6["official_url"] or "ipindia.gov.in" in res6["official_url"])

    def test_03_dedicated_projects_and_milestones(self):
        """Tests Pro Studio project store and dynamic 6-stage milestone progression."""
        projects = project_manager.list_projects()
        self.assertGreaterEqual(len(projects), 2)

        proj = project_manager.get_project("proj_ayur_rheuma")
        self.assertIsNotNone(proj)
        self.assertEqual(len(proj["milestones"]), 6)
        
        # Test advancing stage
        initial_progress = proj["overall_progress_pct"]
        updated = project_manager.advance_stage("proj_ayur_rheuma", "stage_3", 100)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["milestones"][2]["status"], "completed")

    def test_04_ayush_ministry_mentor_tokens(self):
        """Validates official Ministry of Ayush Mentor Token verification."""
        # Valid Token 1
        res1 = project_manager.verify_mentor_token("proj_ayur_rheuma", "AYUSH-MENTOR-2026-X89")
        self.assertEqual(res1["status"], "success")
        self.assertIn("Dr. Rajesh K. Sharma", res1["mentor"]["name"])

        # Valid Token 2
        res2 = project_manager.verify_mentor_token("proj_ayur_rheuma", "AYUSH-SIDDHA-2026-M42")
        self.assertEqual(res2["status"], "success")
        self.assertIn("Siddha Pharmacopoeia", res2["mentor"]["designation"])

        # Invalid Token
        res_invalid = project_manager.verify_mentor_token("proj_ayur_rheuma", "INVALID-TOKEN-999")
        self.assertEqual(res_invalid["status"], "error")

    def test_05_official_gazette_hyperlinks(self):
        """Verifies that authentic government URLs are configured for all gazette documents."""
        for doc_id, doc in GAZETTE_REGISTRY.items():
            self.assertIn("official_url", doc)
            self.assertTrue(doc["official_url"].startswith("http"))
            self.assertIn("portal_name", doc)


if __name__ == "__main__":
    unittest.main()
