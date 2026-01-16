#!/usr/bin/env python3
"""
ULTRA-AGGRESSIVE Anti-AI Essay Generation
Uses completely different approach - mimics actual human imperfections
"""
import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

STUDENT_INFO = """
Economics at Oxford. 
- 2020 crash made me question markets
- Read Kahneman, disagreed with his rational actor model  
- Built a trading bot in Python
- Debate captain, won regionals
- Part-time at accountancy firm
- Parents run small business
"""

# COMPLETELY NEW APPROACH: Mimic human writing patterns
ULTRA_HUMAN_PROMPT = """
You are a 17 year old student writing a UCAS personal statement IN A HURRY.

CRITICAL: Modern AI detectors look for:
1. Perfect grammar (humans make mistakes)
2. Balanced sentence length (humans are inconsistent) 
3. Formal transitions (humans skip these)
4. "Correct" academic structure (humans ramble)

YOUR JOB: Write like an actual stressed teenager, NOT a polished essay.

REQUIREMENTS:
- Start sentences with "And" or "But" sometimes
- Use contractions (I'm, can't, didn't, won't)
- Some sentences can be incomplete
- NO formal transitions like "Furthermore" or "Moreover"
- Include at least 2 self-corrections (e.g. "I wanted to - actually no, I needed to")
- Be direct and colloquial
- Include one minor typo
- Dont use too many commas

STUDENT INFO:
""" + STUDENT_INFO + """

Write 3 paragraphs (about 800 words total). Be raw. Be imperfect. Be human.
"""

def main():
    print("Generating with ULTRA-HUMAN approach...")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=ULTRA_HUMAN_PROMPT,
        config=types.GenerateContentConfig(
            temperature=2.0,  # MAXIMUM chaos
            thinking_config=types.ThinkingConfig(
                include_thoughts=False,
                thinking_budget=8000
            )
        )
    )
    
    essay = response.text
    
    print("\n" + "="*60)
    print("ULTRA-HUMAN ESSAY:")
    print("="*60)
    print(essay)
    print("="*60)
    print(f"Characters: {len(essay)}")
    
    with open("ultra_human_output.txt", "w") as f:
        f.write(essay)
    print("\nSaved to ultra_human_output.txt")

if __name__ == "__main__":
    main()
