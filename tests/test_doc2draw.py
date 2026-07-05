"""
Unit Tests for Doc2Draw.
Verifies Excalidraw schema validation, parsers, and layout compilation.
"""
import os
import json
import tempfile
import unittest
from doc2draw.schemas.diagram_schema import DiagramItem, DiagramStructure
from doc2draw.layout.grid_engine import GridEngine
from doc2draw.compiler.excalidraw_compiler import compile_to_excalidraw_json, save_excalidraw_file
from doc2draw.ai.extractor import rule_based_extract
from doc2draw.parsers.docx_parser import parse_docx

class TestDoc2Draw(unittest.TestCase):
    def setUp(self):
        self.sample_item_1 = DiagramItem(
            id="item_1",
            title="Introduction to AI",
            bullet_points=[
                "Understanding neural networks",
                "History of machine learning",
                "Applications in modern software"
            ],
            category_color="purple",
            connected_to=["item_2"]
        )
        self.sample_item_2 = DiagramItem(
            id="item_2",
            title="Deep Learning Architectures",
            bullet_points=[
                "Transformers and attention mechanisms",
                "Convolutional networks for vision",
                "Recurrent networks for sequential data"
            ],
            category_color="blue",
            connected_to=[]
        )
        self.sample_structure = DiagramStructure(
            title="AI Masterclass",
            subtitle="Complete Guide to Modern AI",
            layout_style="multi_column_grid",
            items=[self.sample_item_1, self.sample_item_2]
        )

    def test_schema_validation(self):
        """Test that Pydantic models instantiate and serialize correctly."""
        self.assertEqual(self.sample_structure.title, "AI Masterclass")
        self.assertEqual(len(self.sample_structure.items), 2)
        self.assertEqual(self.sample_item_1.connected_to, ["item_2"])

    def test_grid_engine_layout(self):
        """Test that GridEngine calculates positions and generates valid elements."""
        engine = GridEngine(max_cols=2)
        elements, files = engine.generate_layout(self.sample_structure)
        
        # We expect: 1 header rect + 1 header text + 2 card rects + 2 card texts + 1 arrow = 7 elements
        self.assertEqual(len(elements), 7)
        
        # Verify arrow connection exists
        arrows = [el for el in elements if el["type"] == "arrow"]
        self.assertEqual(len(arrows), 1)
        self.assertEqual(arrows[0]["id"], "arrow_item_1_item_2")

    def test_excalidraw_json_compiler(self):
        """Test that compiled JSON complies with Excalidraw format requirements."""
        json_str = compile_to_excalidraw_json(self.sample_structure)
        data = json.loads(json_str)
        
        self.assertEqual(data["type"], "excalidraw")
        self.assertEqual(data["version"], 2)
        self.assertIn("elements", data)
        self.assertIn("appState", data)
        self.assertIn("files", data)
        
        # Verify every element has required Excalidraw attributes
        required_attrs = ["id", "type", "x", "y", "width", "height", "strokeColor", "backgroundColor"]
        for el in data["elements"]:
            for attr in required_attrs:
                self.assertIn(attr, el, f"Element {el.get('id')} missing required attribute '{attr}'")

    def test_rule_based_extractor(self):
        """Test rule-based markdown extraction fallback."""
        md_text = """
# Chapter 1: Foundations
- First key concept explained
- Second important takeaway
- Third critical rule

# Chapter 2: Advanced Applications
- How to deploy in production
- Scaling strategies
"""
        structure = rule_based_extract(md_text, title="Test Doc")
        self.assertEqual(structure.title, "Test Doc")
        self.assertEqual(len(structure.items), 2)
        self.assertEqual(structure.items[0].title, "Chapter 1: Foundations")
        self.assertEqual(len(structure.items[0].bullet_points), 3)

    def test_file_saving(self):
        """Test saving compiled excalidraw file to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_map.excalidraw")
            save_excalidraw_file(self.sample_structure, out_path)
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            self.assertEqual(content["type"], "excalidraw")

if __name__ == "__main__":
    unittest.main()
