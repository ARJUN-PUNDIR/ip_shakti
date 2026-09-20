"""
Unit & Integration Tests for Gap 1: Dual Jurisdiction Switch (India vs International)
Verifies:
1. Indian Jurisdiction: IPO, NBA, SALA, Allied Regimes (FSSAI / DMROA 1954 / GI)
2. International Jurisdiction: WIPO GRATK Treaty 2024, CBD Nagoya ABS, EU EMA THMPD, US FDA DSHEA
3. Collision Matrix Adaptation across both National and International jurisdictions
4. Dynamic Topology Resolution
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from pipeline.graph import regulatory_graph
from pipeline.nodes.allied_node import allied_agent_node
from pipeline.nodes.international_nodes import (
    wipo_gratk_agent_node,
    cbd_nagoya_agent_node,
    eu_thmpd_agent_node,
    us_fda_agent_node
)

class TestGap1DualJurisdiction(unittest.TestCase):

    def test_allied_node_fssai_and_dmroa(self):
        """Tests Allied Agent FSSAI and DMROA 1954 evaluation."""
        # Query with food supplement intent
        state_food = {
            "query": "Ayurveda Aahar nutritional churnam food supplement",
            "botanicals_detected": ["amla"],
            "detected_botanicals": [{"common_name": "Amla", "latin_name": "Phyllanthus emblica"}],
            "is_food_supplement": True,
            "target_jurisdictions": ["india"]
        }
        res_food = allied_agent_node(state_food)
        self.assertIn("allied_evaluation", res_food)
        self.assertIn("FSSAI Ayurveda-Aahar", res_food["allied_evaluation"]["status"])

        # Query with DMROA prohibited claim
        state_dmroa = {
            "query": "Permanent Ayurvedic cure for diabetes and cancer",
            "botanicals_detected": ["jamun"],
            "detected_botanicals": [{"common_name": "Jamun", "latin_name": "Syzygium cumini"}],
            "target_jurisdictions": ["india"]
        }
        res_dmroa = allied_agent_node(state_dmroa)
        self.assertIn("DMROA 1954", res_dmroa["allied_evaluation"]["status"])

    def test_international_nodes(self):
        """Tests the 4 International Treaty & Foreign Market nodes."""
        state = {
            "query": "Ashwagandha KSM-66 extract for memory enhancement in USA and Germany",
            "botanicals_detected": ["ashwagandha"],
            "detected_botanicals": [{"common_name": "Ashwagandha", "latin_name": "Withania somnifera"}],
            "target_jurisdictions": ["us", "eu"]
        }
        
        # 1. WIPO GRATK Treaty 2024
        wipo = wipo_gratk_agent_node(state)
        self.assertIn("wipo_evaluation", wipo)
        self.assertIn("WIPO GRATK 2024", wipo["wipo_evaluation"]["status"])

        # 2. CBD & Nagoya ABS
        cbd = cbd_nagoya_agent_node(state)
        self.assertIn("cbd_evaluation", cbd)
        self.assertIn("Nagoya Protocol", cbd["cbd_evaluation"]["status"])

        # 3. EU EMA THMPD
        eu = eu_thmpd_agent_node(state)
        self.assertIn("eu_evaluation", eu)
        self.assertIn("THMPD", eu["eu_evaluation"]["status"])

        # 4. US FDA & DSHEA
        us = us_fda_agent_node(state)
        self.assertIn("us_evaluation", us)
        self.assertIn("DSHEA", us["us_evaluation"]["status"])

    def test_state_graph_india_regime(self):
        """Tests that India regime runs Allied Agent and generates India-specific pills and summary."""
        res = regulatory_graph.invoke("Turmeric curcuminoid formulation for pain relief", jurisdiction="india")
        self.assertEqual(res.get("jurisdiction"), "india")
        self.assertIn("allied_evaluation", res)
        self.assertTrue(len(res.get("conflict_matrix", [])) >= 4)
        
        # Check that Allied Regimes is represented in the conflict matrix
        allied_pill = any(
            "Allied" in c.get("jurisdiction", "") or "FSSAI" in c.get("jurisdiction", "")
            for c in res.get("conflict_matrix", [])
        )
        self.assertTrue(allied_pill, "Allied Regimes must be present in conflict matrix in India mode")

    def test_state_graph_international_regime(self):
        """Tests that International regime runs the 4 international agents."""
        res = regulatory_graph.invoke("Turmeric curcuminoid formulation for pain relief", jurisdiction="international")
        self.assertEqual(res.get("jurisdiction"), "international")
        self.assertIn("wipo_evaluation", res)
        self.assertIn("cbd_evaluation", res)
        self.assertIn("eu_evaluation", res)
        self.assertIn("us_evaluation", res)
        self.assertTrue(len(res.get("conflict_matrix", [])) >= 4)

        # Check that WIPO and CBD are in conflict matrix
        wipo_pill = any("WIPO" in c.get("jurisdiction", "") for c in res.get("conflict_matrix", []))
        cbd_pill = any("CBD" in c.get("jurisdiction", "") or "Nagoya" in c.get("jurisdiction", "") for c in res.get("conflict_matrix", []))
        self.assertTrue(wipo_pill, "WIPO GRATK Treaty must be in international conflict matrix")
        self.assertTrue(cbd_pill, "CBD / Nagoya ABS must be in international conflict matrix")

    def test_topology_jurisdiction_filtering(self):
        """Tests that graph topology dynamically swaps nodes based on jurisdiction."""
        top_in = regulatory_graph.get_topology(jurisdiction="india")
        node_ids_in = [n["id"] for n in top_in["nodes"]]
        self.assertIn("allied_agent", node_ids_in)
        self.assertNotIn("wipo_gratk_agent", node_ids_in)

        top_intl = regulatory_graph.get_topology(jurisdiction="international")
        node_ids_intl = [n["id"] for n in top_intl["nodes"]]
        self.assertIn("wipo_gratk_agent", node_ids_intl)
        self.assertIn("cbd_nagoya_agent", node_ids_intl)
        self.assertIn("eu_thmpd_agent", node_ids_intl)
        self.assertIn("us_fda_agent", node_ids_intl)
        self.assertNotIn("allied_agent", node_ids_intl)

    def test_confidence_and_escalation_readiness(self):
        """Tests that both India and International regimes yield high-grounding confidence data and citations."""
        res_in = regulatory_graph.invoke("Turmeric Curcumin topical balm Section 3p", jurisdiction="india")
        self.assertTrue(len(res_in.get("citations", [])) >= 2)
        
        res_intl = regulatory_graph.invoke("Ashwagandha export to Germany under EU THMPD", jurisdiction="international")
        self.assertTrue(len(res_intl.get("citations", [])) >= 2)

if __name__ == "__main__":
    unittest.main()
