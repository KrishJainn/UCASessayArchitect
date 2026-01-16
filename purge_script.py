import backend
import os

print("Starting purge...")
success = backend.reset_brain()
if success:
    print("PURGE SUCCESSFUL")
else:
    print("PURGE FAILED")
