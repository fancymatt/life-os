#!/usr/bin/env python3
"""
Quickest test - just call Gemini and get a response
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tools.shared.router import LLMRouter
from ai_capabilities.specs import OutfitSpec
from dotenv import load_dotenv

load_dotenv()

print("Testing AI calls...\n")

# Basic text
router = LLMRouter(model="gemini/gemini-2.0-flash-exp")
response = router.call("What are the key elements of a professional business outfit?")
print(f"✅ TEXT GENERATION:\n{response}\n")

# Structured output
print("\n" + "="*70)
outfit_prompt = """
Analyze this: "A navy blue blazer, white dress shirt, and gray trousers."
Return JSON with: clothing_items (array of {item, fabric, color, details}),
style_genre, formality, aesthetic
"""

outfit = router.call_structured(outfit_prompt, OutfitSpec)
print(f"✅ STRUCTURED OUTPUT (Pydantic):")
print(f"   Style: {outfit.style_genre}")
print(f"   Formality: {outfit.formality}")
print(f"   Items: {len(outfit.clothing_items)}")
for item in outfit.clothing_items:
    print(f"     - {item.item} ({item.color})")

print("\n✅ Everything works!")
