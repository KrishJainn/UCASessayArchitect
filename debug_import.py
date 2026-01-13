
print("Starting import test...")
try:
    import backend
    print("Import successful.")
except Exception as e:
    print(f"Import failed: {e}")
except SystemExit:
    print("SystemExit caught")
