"""
real_hardware.py — Run a mini BB84 experiment on real IBM Quantum hardware.

This is not a full 200-qubit simulation (real hardware is expensive and
queued). Instead, we test the core physics of BB84:

    Alice prepares 4 possible states: |0>, |1>, |+>, |->
    Bob measures in either the Z basis or the X basis.

The theoretical predictions:
    - Same basis    -> Bob gets Alice's bit perfectly (0% error)
    - Different basis -> Bob gets a random bit (50% error)

Real hardware adds noise, so we expect a few percent of errors even in
the same-basis case. That noise IS the experiment.
"""
import os
from pathlib import Path
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler


# ---------- Load token ----------
env_path = Path(".env")
token = None
for line in env_path.read_text().splitlines():
    if line.startswith("IBM_QUANTUM_TOKEN="):
        token = line.split("=", 1)[1].strip()

if not token:
    raise SystemExit("ERROR: IBM_QUANTUM_TOKEN not set in .env")

# ---------- Connect ----------
print("Connecting to IBM Quantum...")
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)

# Pick the least-busy real backend with at least 2 qubits
backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
print(f"Using backend: {backend.name}  ({backend.num_qubits} qubits)\n")


# ---------- Build the 4 experiments ----------
def build_circuit(alice_bit, alice_basis, bob_basis):
    """
    alice_bit:   0 or 1
    alice_basis: 0 (Z) or 1 (X)
    bob_basis:   0 (Z) or 1 (X)
    """
    qc = QuantumCircuit(1, 1)

    # Alice prepares the state
    if alice_bit == 1:
        qc.x(0)
    if alice_basis == 1:
        qc.h(0)

    # Bob chooses a basis
    if bob_basis == 1:
        qc.h(0)

    qc.measure(0, 0)
    return qc


# Four representative cases (Alice_bit=1 for all, varies bases)
cases = [
    ("Same basis (Z, Z)",     1, 0, 0),
    ("Same basis (X, X)",     1, 1, 1),
    ("Different bases (Z, X)", 1, 0, 1),
    ("Different bases (X, Z)", 1, 1, 0),
]

circuits = [build_circuit(bit, ab, bb) for _, bit, ab, bb in cases]

# Transpile for the real backend (must use its native gates)
transpiled = transpile(circuits, backend=backend, optimization_level=1)

print(f"Transpiled {len(transpiled)} circuits. Submitting job...\n")

# ---------- Submit to real hardware ----------
sampler = Sampler(backend)
job = sampler.run(transpiled, shots=1000)
print(f"Job ID: {job.job_id()}")
print(f"Status: {job.status()}")
print(f"\nThis may sit in the queue for a few minutes. "
      f"Monitor progress at https://quantum.ibm.com/jobs/{job.job_id()}\n")
print("Waiting for result...")

result = job.result()
print("Done!\n")


# ---------- Analyze ----------
print("=" * 60)
print(" REAL HARDWARE RESULTS — BB84 mini-experiment")
print("=" * 60)
print(f"{'Case':<28} {'P(0)':>8} {'P(1)':>8}   Interpretation")
print("-" * 60)

for (label, _, _, _), pub_result in zip(cases, result):
    counts = pub_result.data.c.get_counts()
    total = sum(counts.values())
    p0 = counts.get('0', 0) / total
    p1 = counts.get('1', 0) / total

    if "Same" in label:
        interpretation = f"Bob gets Alice's bit with {max(p0, p1)*100:.1f}%"
    else:
        interpretation = f"Random: {p0*100:.1f}% / {p1*100:.1f}%"

    print(f"{label:<28} {p0:>8.3f} {p1:>8.3f}   {interpretation}")

print("-" * 60)
print("\nWhat this shows:")
print("  * Same basis    -> Bob's bit matches Alice's bit (small errors =")
print("                     real hardware noise, not a simulation bug).")
print("  * Different basis -> Bob gets a ~50/50 random result.")
print("\nThis is the physical basis of BB84: Eve cannot copy a qubit without")
print("disturbing it, and disturbances show up as errors in the sifted key.")