#!/usr/bin/env python3
"""
Test essay generation script v2.
Generates a sample essay using the trained brain.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import backend

TEST_PROFILE = """
TARGET COURSE: Economics at Oxford

WHY THIS SUBJECT:
I became interested in economics after the 2020 market crash. I watched my dad lose money and wanted to understand why markets fail. I read "Thinking Fast and Slow" by Kahneman and disagreed with his rational actor model.

ACADEMIC WORK:
- Read Stiglitz on market failure
- Did an EPQ on cryptocurrency regulation
- A-levels: Maths A*, Economics A*, Further Maths A

SUPERCURRICULARS:
- Built a Python trading bot that backtests strategies
- Wrote for school economics journal
- Attended LSE summer school

EXTRACURRICULARS:
- Debate team captain - won regional finals
- Part-time job at accountancy firm
- Volunteer tutor for younger students

PERSONAL STORY:
I come from a family of small business owners. Watching my parents navigate tax policy and inflation made economics personal, not abstract.
"""

def main():
    print("Loading brain config...")
    brain_config = backend.load_brain_config()
    
    if not brain_config:
        print("ERROR: No brain config found.")
        brain_config = {"Structure_Blueprint": {"Q1_percentage": 20, "Q2_percentage": 55, "Q3_percentage": 25}}
    
    print(f"Structure: {brain_config.get('Structure_Blueprint', {})}")
    
    # Retrieve exemplars directly
    print("\nRetrieving exemplars from vectorstore...")
    vectorstore = backend.get_vectorstore()
    docs = vectorstore.similarity_search(TEST_PROFILE, k=5)
    exemplars = "\n\n---\n\n".join([doc.page_content for doc in docs])
    print(f"Retrieved {len(docs)} exemplar chunks.\n")
    
    print("=" * 60)
    print("GENERATING ESSAY...")
    print("=" * 60)
    
    result = backend.generate_separated_essay(TEST_PROFILE, exemplars, brain_config)
    
    if "error" in result:
        print(f"ERROR: {result['error']}")
        return
    
    full_essay = f"""{result.get('q1_answer', '')}

{result.get('q2_answer', '')}

{result.get('q3_answer', '')}"""
    
    print("\n" + "=" * 60)
    print("GENERATED ESSAY:")
    print("=" * 60)
    print(full_essay)
    print("\n" + "=" * 60)
    print(f"Total characters: {len(full_essay)}")
    print("=" * 60)
    
    with open("test_output.txt", "w") as f:
        f.write(full_essay)
    print("\nSaved to test_output.txt")

if __name__ == "__main__":
    main()
