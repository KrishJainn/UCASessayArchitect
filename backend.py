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
def safe_generate_content(client, contents, model="gemini-3-flash-preview", config=None):
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
    Phoenix 5.0: THE HUMANIZER PROTOCOL.
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
    
    # CRITICAL: Merge all banned lists into one Master List
    # 1. Hardcoded Words (Generic AI)
    # 2. Hardcoded Phrases (Clichés)
    # 3. Dynamic Anti-Patterns (from Brain Config)
    # 4. User-Specific Complaints (driven to, etc.)
    
    user_complaints = ["driven to", "underpinning", "instilled", "akin to", "demystify", "power of", 
                       "drawn to", "allure", "fascinated", "deeply", "profoundly", "framework", 
                       "landscape", "tapestry", "utilize", "leverage", "captivated", "glimpsing", 
                       "eager", "revealing", "precise logic", "steered my interest", "forms the core",
                       "presents a compelling", "my ambition is", "felt like discerning", "burgeoning",
                       "illuminated", "inherent irrationality", "bedrock assumptions", "dual perspective",
                       "forms the core of my motivation", "revelation steered", "beyond mere", "intricate calculus",
                       "decode", "propelling", "intersection of"]
                       
    master_banned = list(set(BANNED_WORDS + BANNED_PHRASES + banned + user_complaints))
    
    # VOCAB INJECTION: force the model to use the student's unique words
    vocab_bank = brain_config.get('Vocabulary_Bank', [])
    sentence_templates = brain_config.get('Sentence_Templates', [])
    
    forced_vocab = []
    if len(vocab_bank) >= 7:
        forced_vocab = random.sample(vocab_bank, 7) 
    else:
        forced_vocab = vocab_bank # Use all if less than 7

    # DYNAMIC STRUCTURE LOGIC
    # Load blueprint or default to standard structure if missing
    blueprint = brain_config.get("Structure_Blueprint", {})
    q1_pct = blueprint.get("Q1_percentage", 20) / 100
    q2_pct = blueprint.get("Q2_percentage", 40) / 100
    q3_pct = blueprint.get("Q3_percentage", 40) / 100
    
    total_target = 3900 # Safe target under 4000
    q1_limit = int(total_target * q1_pct)
    q2_limit = int(total_target * q2_pct)
    q3_limit = int(total_target * q3_pct)

    # THE 'STYLE CLONE' PROMPT (Phoenix 10.0: EXACT COPY)
    # Forces AI to clone the EXACT style of uploaded essays
    system_instruction = f"""You are rewriting a personal statement by CLONING the exact style of the example essays below.

CRITICAL: You MUST copy the EXACT writing style, sentence patterns, and tone from these real essays:

=== EXAMPLE ESSAYS TO CLONE (COPY THIS STYLE EXACTLY) ===
{retrieved_exemplars}
=== END EXAMPLES ===

YOUR TASK:
Take the student's raw information and rewrite it in the EXACT SAME STYLE as the examples above.
- Copy their sentence structures
- Copy their paragraph flow
- Copy their vocabulary choices
- Copy their tone and voice
- Copy how they introduce ideas
- Copy how they transition between topics

STUDENT RAW INFORMATION:
{user_profile}

LENGTH REQUIREMENTS (CRITICAL):
- Q1: MINIMUM {q1_limit} characters - write MORE if needed
- Q2: MINIMUM {q2_limit} characters - write MORE if needed  
- Q3: MINIMUM {q3_limit} characters - write MORE if needed
- TOTAL: TARGET 3700-3900 characters (you are currently writing too short - EXPAND!)

The output is too short if under 3500 characters. ADD MORE CONTENT.

BANNED WORDS (NEVER USE THESE - they flag as AI):
{BANNED_WORDS}
Also NEVER use: "illuminated", "profound", "meticulous", "moreover", "furthermore", "in conclusion", "testament", "landscape"

Q3 SPECIFIC RULES (This section keeps getting flagged as AI):
- NEVER say "I was responsible for" - say "I handled" or "I ran"
- NEVER say "This experience provided me with" or "This experience gave me"
- NEVER say "skills directly transferable" or "skills transferable to"
- NEVER say "within an organizational setting" or "real-world setting"
- NEVER say "taught me how to" - say "I learned to" or just describe what you did
- NEVER use "direct insight into" or "clear understanding of"
- NEVER say "Alongside this" or "Furthermore" or "Additionally"
- NEVER say "continuously developed" or "have continuously"
- NEVER say "outside of classroom settings"
- NEVER say "to deepen my understanding"
- NEVER say "I taught myself" - just say what you learned
- NEVER say "going beyond just"
- NEVER say "This involved working with"
- NEVER say "which often mirror" 
- NEVER say "For example, I built" - just say "I built"
- NEVER say "learning how to" - just say "I learned"
- NEVER say "This self-directed learning has cultivated"
- NEVER say "problem-solving capabilities" - say "I got better at fixing things"
- NEVER say "my ability to navigate"
- NEVER say "have instilled in me"
- Keep it SHORT and PUNCHY. Real students don't write corporate-speak.
- Example BAD: "This experience gave me a clear understanding of financial responsibility"
- Example GOOD: "I learned budgeting the hard way - our first event lost money."

WHAT NOT TO DO:
- Do NOT write like an AI
- Do NOT use fancy words like "profound", "meticulous", "illuminated"
- Do NOT use transitions like "Moreover", "Furthermore", "In conclusion"
- Do NOT be too wordy - stay UNDER 3900 total characters

OUTPUT FORMAT:
Return JSON with keys: "analysis_log", "q1_answer", "q2_answer", "q3_answer"
"""

    try:
        # Blueprint 7.0: SCORCHED EARTH - High Temp for Chaos
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents="Execute SCORCHED EARTH. Be Concrete. Be Boring. No Poetry.",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(
                    include_thoughts=False,
                    thinking_budget=16000 
                ),
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "analysis_log": {"type": "STRING", "description": "Confirm you deleted all metaphors."},
                        "q1_answer": {"type": "STRING", "description": "Hook (Concrete)"},
                        "q2_answer": {"type": "STRING", "description": "Academics (Argumentative)"},
                        "q3_answer": {"type": "STRING", "description": "Activities (Direct)"}
                    },
                    "required": ["analysis_log", "q1_answer", "q2_answer", "q3_answer"]
                },
                temperature=1.0 # Controlled creativity - stay close to exemplar style
            )
        )
        
        result = json.loads(response.text)
        if isinstance(result, list):
            result = result[0] if len(result) > 0 else {}
        
        # HARD LIMIT ENFORCEMENT (4200 chars max - allows proper endings)
        q1 = result.get("q1_answer", "")
        q2 = result.get("q2_answer", "")
        q3 = result.get("q3_answer", "")
        total = len(q1) + len(q2) + len(q3)
        
        if total > 4200:
            # Helper function to truncate at last complete sentence
            def truncate_at_sentence(text, max_chars):
                if len(text) <= max_chars:
                    return text
                truncated = text[:max_chars]
                # Find last sentence-ending punctuation
                last_period = truncated.rfind('.')
                last_exclaim = truncated.rfind('!')
                last_question = truncated.rfind('?')
                last_end = max(last_period, last_exclaim, last_question)
                if last_end > max_chars * 0.5:  # Only if we keep at least half
                    return truncated[:last_end + 1]
                return truncated  # Fallback if no good sentence end found
            
            # Proportionally truncate each section at sentence boundaries
            ratio = 3950 / total  # Target 3950 to leave buffer
            result["q1_answer"] = truncate_at_sentence(q1, int(len(q1) * ratio))
            result["q2_answer"] = truncate_at_sentence(q2, int(len(q2) * ratio))
            result["q3_answer"] = truncate_at_sentence(q3, int(len(q3) * ratio))
            print(f"TRUNCATED: {total} -> {len(result['q1_answer']) + len(result['q2_answer']) + len(result['q3_answer'])}")
        
        # GRAMMAR CHECK - Fix any grammar issues before output
        def grammar_check(text, client):
            if not text or len(text) < 50:
                return text
            try:
                grammar_response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"""Fix ONLY grammar and spelling errors in this text. 
Do NOT change the meaning, style, or add any new content.
Return ONLY the corrected text, nothing else.

Text: {text}""",
                    config=types.GenerateContentConfig(temperature=0.1)
                )
                return grammar_response.text.strip()
            except:
                return text  # Return original if grammar check fails
        
        result["q1_answer"] = grammar_check(result.get("q1_answer", ""), client)
        result["q2_answer"] = grammar_check(result.get("q2_answer", ""), client)
        result["q3_answer"] = grammar_check(result.get("q3_answer", ""), client)
        
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
    "at the end of the day",
    "steered my interest",
    "forms the core of",
    "presents a compelling",
    "felt like discerning",
    "illuminated the",
    "unveiled the",
    "deciphering the tapestry",
    "dual perspective",
    "inherent irrationality",
    "bedrock assumptions"
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
    if char_count > 4000:
        issues.append(f"OVER UCAS LIMIT ({char_count}/4000 chars)")
        score -= 100 # Instant Fail
    elif char_count < 3000:
        issues.append(f"Too short ({char_count} chars)")
        score -= 20
    
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
    
    # Get ALL documents from the vectorstore (True "All", not just similarity)
    print(f"Retrieving all {essay_count} chunks...")
    vectorstore = get_vectorstore()
    
    # Access the underlying Chroma collection to get EVERYTHING
    # similarity_search is biased; generic 'get' is complete.
    try:
        results = vectorstore._collection.get(include=['documents'])
        all_docs_text = results.get('documents', [])
        all_text = "\n\n===ESSAY BOUNDARY===\n\n".join(all_docs_text)
    except Exception as e:
        print(f"Error fetching all docs: {e}")
        return {"error": str(e)}
    
    print(f"Analyzing {len(all_docs_text)} document chunks...")
    
    analysis_prompt = f"""Analyze these {len(all_docs_text)} Personal Statement excerpts. 
    OBJECTIVE: Extract ONLY vocabulary, sentence templates, and tones. DO NOT analyze structure.
    
    TASK: SYNTAX HUNTER
    - Extract unique, jagged sentence structures.
    - Ignore cliches.
    
    OUTPUT STRICT JSON ONLY (no markdown):
    {{
        "Structure_Blueprint": {{
            "Q1_percentage": 22,
            "Q2_percentage": 33,
            "Q3_percentage": 45,
            "typical_total_chars": 4000,
            "notes": "Fixed structure as specified by user"
        }},
        "Vocabulary_Bank": [
            "List 50+ specific words (e.g., 'galvanized', 'curiosity', 'realm')."
        ],
        "Section_Tone": {{
            "Q1_tone": "Describe the tone of the opening hooks (e.g. 'Urgent', 'Reflective').",
            "Q2_tone": "Describe the tone of the academic critique sections.",
            "Q3_tone": "Describe the tone of the practical evidence sections."
        }},
        "Sentence_Templates": [
            "Extract 10 UNIQUE sentence structures (e.g., 'The problem wasn't X; it was Y.').",
            "DO NOT extract 'I did X and learned Y'." 
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
        # Use a high temperature to find unique things
        config.temperature = 0.7 
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
            "analyzed_chunks": len(all_docs_text),
            "analysis_date": str(os.popen("date").read().strip()),
            "model_used": "gemini-3-flash-preview"
        }
        
        # Save to file
        with open(BRAIN_CONFIG_PATH, 'w') as f:
            json.dump(brain_config, f, indent=2)
        
        print(f"Brain config saved to {BRAIN_CONFIG_PATH}")
        return brain_config
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return {"error": str(e)}

def reset_brain():
    """
    DANGER: Wipes the entire vector database and brain config.
    Used when user wants to re-upload fresh essays.
    """
    print("WARNING: Resetting Brain...")
    try:
        # 1. Reset Chroma (if possible easily) or just delete the folder
        if os.path.exists(DB_PATH):
            import shutil
            shutil.rmtree(DB_PATH)
            print(f"Deleted DB at {DB_PATH}")
            
        # 2. Delete Brain Config
        if os.path.exists(BRAIN_CONFIG_PATH):
            os.remove(BRAIN_CONFIG_PATH)
            print(f"Deleted config at {BRAIN_CONFIG_PATH}")
            
        return True
    except Exception as e:
        print(f"Error resetting brain: {e}")
        return False
        
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

