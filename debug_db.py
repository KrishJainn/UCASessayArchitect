
import os
import sys
import glob

# Add current dir to path
sys.path.append(os.getcwd())

from backend import get_essay_count, get_vectorstore, DB_PATH

print(f"Checking DB_PATH: {DB_PATH}")
if os.path.exists(DB_PATH):
    # Calculate size using python
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(DB_PATH):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    print(f"DB Directory exists. Size: {total_size / (1024*1024):.2f} MB")
else:
    print("DB Directory DOES NOT EXIST")

print("Attempting to get vectorstore...")
try:
    vs = get_vectorstore()
    print("Vectorstore initialized.")
    # Add a timeout? No easy way in chroma, but let's see.
    print("Attempting to count...")
    count = vs._collection.count()
    print(f"Count: {count}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
