import unittest
from nemotron_client import NemotronClient

class TestMultiProviderLLM(unittest.TestCase):
    def setUp(self):
        self.client = NemotronClient()

    def test_provider_detection(self):
        # OpenAI Models
        self.assertEqual(self.client.detect_provider("gpt-4o"), "openai")
        self.assertEqual(self.client.detect_provider("gpt-4o-mini"), "openai")
        self.assertEqual(self.client.detect_provider("o3-mini"), "openai")
        self.assertEqual(self.client.detect_provider("o1"), "openai")

        # NVIDIA Models
        self.assertEqual(self.client.detect_provider("nvidia/nemotron-3-ultra-550b-a55b"), "nvidia")
        self.assertEqual(self.client.detect_provider("nvidia/nemotron-3.5-lightning-30b-a3b"), "nvidia")
        self.assertEqual(self.client.detect_provider("meta/llama-3.3-70b-instruct"), "nvidia")
        self.assertEqual(self.client.detect_provider("deepseek-ai/deepseek-r1"), "nvidia")

        # Ollama Local Models
        self.assertEqual(self.client.detect_provider("llama3.2"), "ollama")
        self.assertEqual(self.client.detect_provider("llama3:8b"), "ollama")
        self.assertEqual(self.client.detect_provider("qwen2.5:7b"), "ollama")
        self.assertEqual(self.client.detect_provider("mistral:7b"), "ollama")

    def test_set_config_openai(self):
        self.client.set_config(provider="openai", model="gpt-4o", api_key="sk-test-openai-key-1234567890")
        self.assertEqual(self.client.provider, "openai")
        self.assertEqual(self.client.model, "gpt-4o")
        self.assertEqual(self.client.get_api_key("openai"), "sk-test-openai-key-1234567890")

    def test_set_config_nvidia(self):
        self.client.set_config(provider="nvidia", model="nvidia/nemotron-3-ultra-550b-a55b", api_key="nvapi-test-nvidia-key-1234567890")
        self.assertEqual(self.client.provider, "nvidia")
        self.assertEqual(self.client.model, "nvidia/nemotron-3-ultra-550b-a55b")
        self.assertEqual(self.client.get_api_key("nvidia"), "nvapi-test-nvidia-key-1234567890")

    def test_set_config_ollama_zero_key(self):
        self.client.set_config(provider="ollama", model="llama3.2", ollama_url="http://localhost:11434")
        self.assertEqual(self.client.provider, "ollama")
        self.assertEqual(self.client.model, "llama3.2")
        self.assertEqual(self.client.ollama_url, "http://localhost:11434")

    def test_fallback_when_offline(self):
        # Query with dummy key when API offline must return verified StateGraph legal fallback
        self.client.set_config(provider="openai", model="gpt-4o", api_key="sk-dummy")
        result = self.client.query("Can I patent Curcumin?", state_context={"summary": "Section 3(p) Barred"})
        self.assertIn("status", result)
        self.assertTrue(result["status"] in ["success", "fallback"])

if __name__ == "__main__":
    unittest.main()
