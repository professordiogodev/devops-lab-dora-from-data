#!/usr/bin/env bash
# The metrics script is fully verifiable automatically.
if python3 verify.py; then echo "- ✅ dora.py matches the reference on all datasets"; exit 0; else echo "- ❌ dora.py does not match the reference (see above)"; exit 1; fi
