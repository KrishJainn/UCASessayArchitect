import os
import json
from dotenv import load_dotenv

# 1. Get the absolute path of the folder where backend.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env from the same directory as backend.py
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH)

# Support Streamlit Cloud secrets
try:
    import streamlit as st
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except:
    pass  # Not running in Streamlit or no secrets configured

print(f"DEBUG: GEMINI_API_KEY is {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")

from google import genai
from google.genai import types
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from ingest_essays import load_pdfs, split_text, store_in_chroma

import chromadb
from chromadb.config import Settings
import time
import random

# ============================================================================
# SAFE GENERATE CONTENT - Rate Limit Protection
# ============================================================================
def safe_generate_content(client, contents, model="gemini-2.5-flash", config=None):
    """
    Wrapper for client.models.generate_content with strict 429 backoff.
    """
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            # Check for rate limit in various ways depending on SDK error structure
            e_str = str(e).lower()
            if "429" in e_str or "quota" in e_str or "resource_exhausted" in e_str:
                wait_time = 10 + random.uniform(1, 5)
                print(f"⚠ Rate Limit Hit (429). Cooling down for {wait_time:.1f}s...")
                time.sleep(wait_time)
                retry_count += 1
            else:
                # Re-raise other errors
                raise e
    
    raise Exception("Max retries exceeded for safe_generate_content")


# ============================================================================
# ANTIGRAVITY STYLE CONSTANTS
# ============================================================================
GOOD_STYLE = "Reading Stiglitz encouraged me to question U.S. policy... To explore this further, I wrote an article... (Notice: Active verbs. 'Input -> Output' logic.)"

BAD_AI_STYLE = "The book provided me with a deep understanding... which is a testament to the complex landscape... (Notice: Passive, uses 'testament', 'landscape'.)"

BANNED_WORDS = [
    "delve", "tapestry", "unwavering", "landscape", "testament", "underscores", 
    "paramount", "multifaceted", "realm", "passionate", "fostered", "honing", "meticulous",
    "moreover", "in conclusion", "ignited", "sparked", "pivotal", "transformative", 
    "profound", "invaluable", "wholeheartedly"
]

def generate_separated_essay(user_profile: str, retrieved_exemplars: str, brain_config: dict) -> dict:
    """ 
    Phoenix 4.0: ANTIGRAVITY BLUEPRINT 2.0 (Audit -> Bluepint -> Draft).
    """
    
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # DEFENSIVE: Ensure brain_config is a dict
    if not isinstance(brain_config, dict):
        brain_config = {}
    
    # DEFENSIVE: Handle Anti_Patterns schema mismatch (List vs Dict)
    anti_patterns = brain_config.get("Anti_Patterns", [])
    banned = []
    if isinstance(anti_patterns, list):
        banned = anti_patterns
    elif isinstance(anti_patterns, dict):
        banned = anti_patterns.get("Banned_Words", [])
    
    # CRITICAL: Always append the Global Hardcoded Banned Words (Safety Net)
    # This addresses user request to "pinpoint reduces" AI generated stuff.
    banned = list(set(banned + BANNED_WORDS))

    # THE 'STRUCTURAL MIRROR' PROMPT
    # This forces the AI to copy the SYNTAX of the exemplars, not just the tone.
    system_instruction = f""" ROLE: You are the 'Antigravity' Ghostwriter.

INPUT 1: THE STYLE BIBLE (Adhere to this VOICE)
{retrieved_exemplars}

INPUT 2: USER RAW NOTES (Ingredients)
{user_profile}

INPUT 3: DEEP BLUEPRINT (The DNA)
Vocabulary: {brain_config.get('Vocabulary_Bank', [])[:15]}
Templates: {brain_config.get('Sentence_Templates', [])[:5]}
Structure: {brain_config.get('Structure_Blueprint', 'Analyze the Exemplars to match their flow')}

STRICT RULES FOR HUMANIZATION (STRUCTURAL MIRRORING):
1. **NO META-COMMENTARY:** Never explain what you learned. (e.g. DELETE "This experience taught me...", "This role highlighted...", "My goal is..."). Just tell the story.
2. **NO "MY [NOUN]" OPENERS:** Do not start sentences with "My passion", "My interest", "My EPQ", "My responsibilities". *Start with I*. ("I analyzed...", "I led...", "I read...").
3. **NO LISTS OF 3:** Do not Say "X, Y, and Z". Say "X and Y". Lists of 3 are high-perplexity AI markers.
4. **KILL THE ADJECTIVE:** Delete "rigorous", "invaluable", "pivotal", "complex".

BAD ROBOTIC EXAMPLE (DO NOT WRITE LIKE THIS):
"My EPQ served as a practical immersion... This project taught me the importance of..." (Score: 100% AI).

GOOD HUMAN EXAMPLE (WRITE LIKE THIS):
"For my EPQ, I analyzed the 2008 crash. The models failed because they assumed house prices always rise. That mistake cost trillions." (Score: 0% AI).

TASK:
Write the Personal Statement in 3 sections with STRICT TARGET RANGES (DO NOT WRITE SHORT, DO NOT OVERSHOOT):
- **Q1 (Motivation):** Target 800 - 950 Characters. (Be punchy).
- **Q2 (Academics):** Target 1200 - 1400 Characters.
- **Q3 (Activities):** Target 1400 - 1600 Characters.
- **TOTAL LIMIT:** Must fall between 3600 and 4100 Characters.
- TONE: Sharp, Intellectual, Direct.
- BANNED: {banned} + [driven to, underpinning, instilled, akin to, demystify, power of, drawn to, allure, fascinated, deeply, profoundly, framework, landscape, tapestry, utilize, leverage]

OUTPUT FORMAT:
- JSON with keys: q1_answer, q2_answer, q3_answer.
- DO NOT Use Markdown.
"""

    try:
        # Blueprint 3.0: Structural Mirroring + 12k Thinking
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Write the essay now. Adhere to the Structural Mirroring rules.",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(
                    include_thoughts=False,
                    thinking_budget=12000 # 12k Safe Budget
                ),
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "q1_answer": {"type": "STRING", "description": "Motivation (Human Style)"},
                        "q2_answer": {"type": "STRING", "description": "Academics (Human Style)"},
                        "q3_answer": {"type": "STRING", "description": "Activities (Human Style)"}
                    },
                    "required": ["q1_answer", "q2_answer", "q3_answer"]
                },
                temperature=1.0 
            )
        )
        
        result = json.loads(response.text)
        if isinstance(result, list):
            result = result[0] if len(result) > 0 else {}
        return result

    except Exception as e:
        return {"error": str(e)}

# BANNED PHRASES - Generic clichés that must not appear
BANNED_PHRASES = [
    "ever since I was young",
    "from a young age",
    "this experience taught me valuable skills",
    "I am passionate about",
    "I have always been fascinated",
    "I want to make a difference",
    "it sparked my interest",
    "opened my eyes to",
    "pushed me out of my comfort zone",
    "gave me a newfound appreciation",
    "in today's fast-paced world",
    "in an ever-changing world",
    "I believe that",
    "It goes without saying",
    "needless to say",
    "at the end of the day"
]

# DEFAULT STYLE GUIDE - Fallback if extraction fails
DEFAULT_STYLE_GUIDE = {
    "sentence_rules": {"length_range": "12-25 words", "variation": "mix short punchy with longer analytical"},
    "tone_rules": {"primary": "modest confidence", "avoid": "dramatic, boastful, robotic"},
    "vocab_rules": {"prefer": "plain verbs, concrete nouns", "avoid": "abstract nouns, buzzwords"},
    "transition_rules": {"frequency": "sparingly", "type": "implicit connections, not signposting"},
    "do_not_do": ["start with I too often", "use passive voice", "list activities without reflection"]
}

# ============================================================================
# QUALITY GATE - The Final Quality Check (Auto-Regenerate if Fail)
# ============================================================================
def quality_gate(essay_text):
    """
    Grades the essay before showing to user.
    Returns (passed: bool, reason: str, score: int)
    """
    issues = []
    score = 100
    
    # 1. Check for Banned Words
    for word in BANNED_WORDS:
        if word.lower() in essay_text.lower():
            issues.append(f"Contains banned word: '{word}'")
            score -= 5
    
    # 2. Check for Banned Phrases
    for phrase in BANNED_PHRASES:
        if phrase.lower() in essay_text.lower():
            issues.append(f"Contains banned phrase: '{phrase}'")
            score -= 10
    
    # 3. Check for "List Logic" (The ChatGPT Test)
    list_words = ["Additionally", "Furthermore", "Moreover", "In addition", "Also,"]
    list_count = sum(essay_text.count(w) for w in list_words)
    if list_count > 2:
        issues.append(f"Too list-like ({list_count} list transitions)")
        score -= 15
    
    # 4. Check for "Struggle Markers" (The Grok Test)
    struggle_words = ['failed', 'mistake', 'error', 'debug', 'struggle', 'revised', 
                      'challenged', 'difficulty', 'problem', 'overcame', 'initially']
    struggle_count = sum(1 for w in struggle_words if w.lower() in essay_text.lower())
    if struggle_count < 3:
        issues.append(f"Lacks narrative struggle (only {struggle_count} markers)")
        score -= 20
    
    # 5. Check for Proper Nouns in Q3 (Technical Density)
    # Simple heuristic: count capitalized words that aren't sentence starters
    words = essay_text.split()
    proper_nouns = [w for i, w in enumerate(words) if w[0].isupper() and i > 0 and words[i-1][-1] != '.']
    if len(proper_nouns) < 10:
        issues.append(f"Low technical density ({len(proper_nouns)} proper nouns)")
        score -= 10
    
    # 6. Check character count
    char_count = len(essay_text)
    if char_count > 4200:
        issues.append(f"Over limit ({char_count} chars)")
        score -= 15
    elif char_count < 3500:
        issues.append(f"Too short ({char_count} chars)")
        score -= 10
    
    passed = score >= 60 and len([i for i in issues if "banned" in i.lower()]) == 0
    
    return passed, issues, score

# 2. Force the database folder to be right here
DB_PATH = os.path.join(BASE_DIR, 'chroma_db')

# ============================================================================
# CACHED EMBEDDING MODEL (Prevents reloading on every Streamlit interaction)
# ============================================================================

# Helper to get ST cache safely
def get_st_cache_resource():
    try:
        import streamlit as st
        return st.cache_resource
    except ImportError:
        return lambda func: func

@get_st_cache_resource()
def get_embedding_function():
    """Returns a cached embedding function to avoid reloading the model."""
    print("DEBUG: Loading embedding model (first time only)...")
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2", # Explicit repo reduces lookup hangs
        model_kwargs={'device': 'cpu'}
    )

@get_st_cache_resource()
def get_vectorstore_client():
    """Cached connection to the persistent database."""
    print(f"DEBUG: Connecting to Persistent Database at: {DB_PATH}")
    return chromadb.PersistentClient(path=DB_PATH)

def get_vectorstore():
    """Returns the vectorstore object using the cached client and embeddings."""
    client = get_vectorstore_client()
    embedding_function = get_embedding_function()
    
    return Chroma(
        client=client,
        collection_name="college_essays",
        embedding_function=embedding_function,
    )

def get_essay_count():
    try:
        # Check if the directory exists first
        if not os.path.exists(DB_PATH):
            return 0
            
        vectorstore = get_vectorstore()
        # Using the underlying collection count which is safer/faster
        count = vectorstore._collection.count()
        return count
    except Exception as e:
        print(f"Error counting essays: {e}")
        return 0

# Path for the learned brain configuration
BRAIN_CONFIG_PATH = os.path.join(BASE_DIR, 'brain_config.json')

def analyze_all_essays():
    """
    Global Learning: Analyzes ALL essays in the database to create a 
    unified Structure Blueprint and Style Bible.
    Saves to brain_config.json for use during generation.
    """
    print("=== GLOBAL CORPUS ANALYSIS ===")
    
    # Check for essays
    essay_count = get_essay_count()
    if essay_count == 0:
        return {"error": "No essays in database. Upload some first."}
    
    # API setup
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not set."}
    
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(temperature=0.2)
    
    # Get ALL documents from the vectorstore
    print(f"Retrieving all {essay_count} chunks...")
    vectorstore = get_vectorstore()
    
    # Retrieve all documents (use a high k value)
    all_docs = vectorstore.similarity_search("personal statement", k=min(essay_count, 200))
    all_text = "\n\n===ESSAY BOUNDARY===\n\n".join([doc.page_content for doc in all_docs])
    
    print(f"Analyzing {len(all_docs)} document chunks...")
    
    analysis_prompt = f"""Analyze these {len(all_docs)} Personal Statement excerpts. 
Reverse-engineer the student's unique "Linguistic Fingerprint".

OUTPUT STRICT JSON ONLY (no markdown):
{{
    "Structure_Blueprint": {{
        "Q1_percentage": <number>,
        "Q2_percentage": <number>,
        "Q3_percentage": <number>,
        "typical_total_chars": 3800,
        "notes": "brief observation about structure"
    }},
    "Vocabulary_Bank": [
        "List 50+ specific words this student uses (e.g., 'galvanized', 'curiosity', 'realm'). Do NOT list generic words."
    ],
    "Sentence_Templates": [
        "List 15+ sentence structures to fill in. Example: 'The intersection of [Subject] and [Subject] led me to...'",
        "Example: 'While I initially thought [X], I soon realized [Y]...'"
    ],
    "Narrative_Archetypes": [
        "Describe 3 abstract storytelling arcs found in the essays (e.g., 'The Problem-Solver Arc', 'The Academic Epiphany Arc')"
    ],
    "Style_Bible": [
        "Rule 1: <strict writing rule>",
        "Rule 2: <another pattern>"
    ],
    "Anti_Patterns": [
        "things these essays NEVER do (e.g. 'Never use passive voice')"
    ]
}}

ESSAY EXCERPTS:
{all_text[:25000]}
"""
    
    try:
        # Safe call
        response = safe_generate_content(client, analysis_prompt, config=config)
        result_text = response.text.strip()
        
        # Clean up markdown if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        brain_config = json.loads(result_text)
        
        # Add metadata
        brain_config["_metadata"] = {
            "analyzed_chunks": len(all_docs),
            "analysis_date": str(os.popen("date").read().strip()),
            "model_used": "gemini-2.5-flash"
        }
        
        # Save to file
        with open(BRAIN_CONFIG_PATH, 'w') as f:
            json.dump(brain_config, f, indent=2)
        
        print(f"Brain config saved to {BRAIN_CONFIG_PATH}")
        return brain_config
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return {"error": str(e)}

def load_brain_config():
    """Load the brain_config.json if it exists."""
    if os.path.exists(BRAIN_CONFIG_PATH):
        try:
            with open(BRAIN_CONFIG_PATH, 'r') as f:
                config = json.load(f)
                if isinstance(config, dict):
                    return config
                else:
                    print(f"WARNING: Brain config at {BRAIN_CONFIG_PATH} is not a dict (got {type(config)}). Ignoring.")
                    return None
        except Exception as e:
            print(f"Failed to load brain config: {e}")
    return None

# ============================================================================
# SYNTHETIC CLONER - Multiply Training Data
# ============================================================================
def generate_synthetic_essays(exemplar_text, subject_list=None):
    """
    Takes one high-quality essay and rewrites it for different subjects,
    keeping the exact sentence structure and scene-card logic.
    Returns list of (subject, synthetic_essay) tuples.
    """
    if subject_list is None:
        subject_list = [
            "Computer Science", 
            "Law", 
            "Medicine", 
            "Mechanical Engineering", 
            "Physics",
            "Mathematics",
            "Economics",
            "Philosophy, Politics and Economics (PPE)"
        ]
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return [("error", "GEMINI_API_KEY not set")]
    
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(temperature=0.6)
    
    results = []
    
    for subject in subject_list:
        print(f"Generating synthetic essay for: {subject}...")
        
        clone_prompt = f"""You are a "Structure Cloner" for UCAS Personal Statements.

YOUR TASK:
Take this EXEMPLAR essay and rewrite it for a student applying to {subject}.

CRITICAL RULES:
1. PRESERVE THE EXACT SENTENCE STRUCTURE - Same sentence lengths, same paragraph breaks
2. PRESERVE THE SCENE-CARD LOGIC - Keep the Constraint -> Failure -> Iteration -> Result pattern
3. PRESERVE THE EMOTIONAL ARC - Same struggles, same growth moments
4. CHANGE ONLY THE CONTENT:
   - Swap the subject-specific concepts (e.g., Economics terms -> {subject} terms)
   - Swap the projects/activities to be relevant to {subject}
   - Swap the books/papers to be appropriate for {subject}

EXEMPLAR ESSAY TO CLONE:
{exemplar_text}

OUTPUT: A complete UCAS Personal Statement for {subject} that would fool an admissions tutor into thinking it was written by the same quality of student.
"""
        
        try:
            # Safe call with delay
            time.sleep(4)
            response = safe_generate_content(client, clone_prompt, config=config)
            synthetic_essay = response.text
            results.append((subject, synthetic_essay))
            print(f"  ✓ Generated for {subject}")
        except Exception as e:
            print(f"  ✗ Failed for {subject}: {e}")
            results.append((subject, f"Error: {e}"))
    
    return results

def save_synthetic_essays(results):
    """Save synthetic essays as text files for ingestion."""
    synthetic_dir = os.path.join(BASE_DIR, 'synthetic_essays')
    if not os.path.exists(synthetic_dir):
        os.makedirs(synthetic_dir)
    
    saved_files = []
    for subject, essay in results:
        if not essay.startswith("Error"):
            filename = f"synthetic_{subject.replace(' ', '_').replace(',', '').lower()}.txt"
            filepath = os.path.join(synthetic_dir, filename)
            with open(filepath, 'w') as f:
                f.write(essay)
            saved_files.append(filepath)
            print(f"Saved: {filepath}")
    
    return saved_files

def analyze_essay_structure(text):
    """
    Uses Gemini to analyze the essay's structure before storage.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Skipping analysis.")
        return text

    client = genai.Client(api_key=api_key)
    
    prompt = f"""Analyze this UCAS Personal Statement. 
    Extract its [Structural Blueprint] (e.g., Hook -> Academic Evidence -> Supercurricular -> Conclusion) and its [Key Themes].
    Output a brief 5-sentence summary of WHY this essay is successful.
    
    ESSAY TEXT:
    {text[:8000]} # Limit context window just in case
    """
    
    try:
        # Safe call
        response = safe_generate_content(client, prompt)
        analysis = response.text
        # Format the enriched text
        enriched_text = f"[AI ANALYSIS: {analysis}]\n\n[ORIGINAL TEXT START]\n{text}"
        return enriched_text
    except Exception as e:
        print(f"Error analyzing essay: {e}")
        return text

def ingest_essay(pdf_path):
    """
    Ingests a single file (PDF or DOCX) into the vector database.
    """
    print(f"Ingesting {pdf_path}...")
    # Reuse logic from ingest_essays.py, but for a single file we can just use the same loader
    # The load_pdfs function expects a directory, so we can adapt or just import the loader directly
    from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
    
    try:
        if pdf_path.lower().endswith('.docx'):
            loader = Docx2txtLoader(pdf_path)
        else:
            loader = PyPDFLoader(pdf_path)
            
        docs = loader.load()
        full_text = "\n".join([doc.page_content for doc in docs])
        print(f"Loaded {len(docs)} pages/sections. Analyzing structure...")
        
        # Smart Ingestion: Analyze and Enrich
        enriched_text = analyze_essay_structure(full_text)
        
        # Re-wrap as a Document object (simplest way to reuse split_text logic)
        # Note: split_text expects a list of Documents. 
        # We'll create a single enriched document.
        from langchain_core.documents import Document
        enriched_doc = Document(page_content=enriched_text, metadata={"source": pdf_path})
        
        chunks = split_text([enriched_doc])
        if chunks:
            # Use the persistent vectorstore directly instead of store_in_chroma
            print("Adding chunks to persistent vectorstore...")
            vectorstore = get_vectorstore()
            vectorstore.add_documents(chunks)
            # ChromaDB 0.4+ with PersistentClient auto-persists, but let's verify
            print(f"DEBUG: Auto-persisting... DB should be at {DB_PATH}")
            return f"Successfully ingested {len(chunks)} enriched chunks from {os.path.basename(pdf_path)}."
        else:
            return "No text chunks created."
    except Exception as e:
        return f"Error ingesting file: {e}"

# ============================================================================
# ADVANCED HUMANIZATION PIPELINE
# ============================================================================

# ============================================================================
# ANTIGRAVITY ELITE GENERATOR
# ============================================================================

if __name__ == "__main__":
    # Test the Phoenix Generator
    print("--- Testing generate_separated_essay (Phoenix) ---")
    
    # Check if API key is set before running
    if "GEMINI_API_KEY" not in os.environ:
        print("WARNING: GEMINI_API_KEY not set. Generation will likely fail or return error.")
    else:
        test_profile = "Target Course: Computer Science\nMotivation: I want to explore algorithms."
        test_exemplars = "This is a sample exemplar essay text for style reference."
        test_config = {"Anti_Patterns": {"Banned_Words": ["delve", "tapestry"]}}
        
        result = generate_separated_essay(test_profile, test_exemplars, test_config)
        print("\n--- Generated Essay ---")
        print(result)

