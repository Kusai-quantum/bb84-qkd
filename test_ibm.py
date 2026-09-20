"""
test_ibm.py — Verify connection to IBM Quantum Platform.

Reads the API token from the local .env file. Never prints the token.
"""
import os
from pathlib import Path

# --- Read token from .env ---
env_path = Path(".env")
if not env_path.exists():
    raise SystemExit("ERROR: .env file not found. Create it with IBM_QUANTUM_TOKEN=...")

token = None
for line in env_path.read_text().splitlines():
    if line.startswith("IBM_QUANTUM_TOKEN="):
        token = line.split("=", 1)[1].strip()

if not token or token == "paste_your_token_here":
    raise SystemExit("ERROR: IBM_QUANTUM_TOKEN not set in .env")

print(f"Token loaded from .env (length {len(token)} chars) — never printed.\n")

# --- Connect to IBM Quantum ---
from qiskit_ibm_runtime import QiskitRuntimeService

try:
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    print("✅ Connected to IBM Quantum (ibm_quantum_platform channel)")
except Exception as e1:
    print(f"Failed with ibm_quantum_platform: {e1}")
    try:
        service = QiskitRuntimeService(channel="ibm_quantum", token=token)
        print("✅ Connected to IBM Quantum (legacy ibm_quantum channel)")
    except Exception as e2:
        raise SystemExit(f"❌ Connection failed: {e2}")

# --- List available backends ---
backends = service.backends(simulator=False, operational=True)
print(f"\nAvailable real quantum backends: {len(backends)}")
for b in backends[:10]:
    print(f"  - {b.name}  ({b.num_qubits} qubits)")

if not backends:
    print("\n⚠️  No real backends available on your account right now.")
    print("   This usually means you need to accept the IBM Quantum terms of service.")
    print("   Visit https://quantum.ibm.com and complete the onboarding.")