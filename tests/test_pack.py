"""No-dependency package checks: python3 -m unittest discover -s tests -v"""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "skills/ask-farouk-creative-thinking/references"

class TestPackage(unittest.TestCase):
    def test_manifest_identity(self):
        meta = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["name"], "ask-farouk-about-creative-thinking")
        self.assertTrue((ROOT / "skills/ask-farouk-creative-thinking/SKILL.md").exists())

    def test_23_method_cards(self):
        notes = (REF / "lecture-notes.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^### \d+\.", notes, re.M)), 23)
        index = (REF / "methods-index.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^\| \d+ \|", index, re.M)), 23)

    def test_grounding_contract(self):
        policy = (ROOT / "skills/ask-farouk-creative-thinking/SKILL.md").read_text(encoding="utf-8")
        for phrase in ["Observation", "Slogan", "not", "source", "23"]:
            self.assertIn(phrase, policy)
        self.assertGreaterEqual(len(json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))), 10)

    def test_transcript_if_bundled(self):
        src = REF / "transcript.md"
        if not src.exists():
            return
        text = src.read_text(encoding="utf-8")
        self.assertIn("### بناء الكونسبت", text)
        self.assertEqual(len(re.findall(r"^#### الطريقة \d+:", text, re.M)), 23)

    def test_slogan_and_attribution(self):
        meta = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        interface = meta["extensions"]["com.openai"]["interface"]
        self.assertIn("صنعة الإعلان", interface["displayName"])
        self.assertIn("Ad Craftness", interface["displayName"])
        self.assertEqual(interface["developerName"], "Mamdouh Aboammar")
        self.assertIn("Farouk Elkady", interface["longDescription"])

        skill_md = (ROOT / "skills/ask-farouk-creative-thinking/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("صنعة الإعلان", skill_md)
        self.assertIn("Ad Craftness", skill_md)
        self.assertIn("Mamdouh Aboammar", skill_md)
        self.assertIn("Farouk", skill_md)

        source_policy = (REF / "source-policy.md").read_text(encoding="utf-8")
        self.assertIn("صنعة الإعلان", source_policy)
        self.assertIn("Ad Craftness", source_policy)
        self.assertIn("Mamdouh Aboammar", source_policy)
        self.assertIn("Farouk Elkady", source_policy)

    def test_manifest_directory_limits(self):
        meta = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        interface = meta["extensions"]["com.openai"]["interface"]
        self.assertLessEqual(len(interface["displayName"]), 30)
        self.assertLessEqual(len(interface["shortDescription"]), 30)
        self.assertLessEqual(len(interface["developerName"]), 80)
        self.assertLessEqual(len(interface["longDescription"]), 4000)

    def test_assets_validity(self):
        for asset_name in ["logo.svg", "icon.svg", "logo-dark.svg", "logo-light.svg"]:
            asset_path = ROOT / "assets" / asset_name
            self.assertTrue(asset_path.exists(), f"Asset {asset_name} missing")
            tree = ET.parse(str(asset_path))
            root = tree.getroot()
            self.assertTrue(root.tag.endswith("svg"))
            viewbox = root.attrib.get("viewBox", "")
            vals = [float(x) for x in re.split(r"[\s,]+", viewbox.strip()) if x]
            self.assertEqual(len(vals), 4)
            self.assertEqual(vals[2], vals[3], f"{asset_name} is not square")
            self.assertGreaterEqual(vals[2], 48)

if __name__ == "__main__":
    unittest.main()
