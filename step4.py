import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()
n = 20

alice_bits = np.random.randint(2, size=n)
alice_bases = np.random.randint(2, size=n)
bob_bases = np.random.randint(2, size=n)
bob_results = []

for i in range(n):
    qc = QuantumCircuit(1, 1)
    if alice_bits[i] == 1: qc.x(0)
    if alice_bases[i] == 1: qc.h(0)
    if bob_bases[i] == 1: qc.h(0)
    qc.measure(0, 0)
    
    result = sim.run(qc, shots=1).result().get_counts()
    bob_results.append(int(list(result.keys())[0]))

# SIFTING
sifted_alice_key = []
sifted_bob_key = []

for i in range(n):
    if alice_bases[i] == bob_bases[i]:
        sifted_alice_key.append(alice_bits[i])
        sifted_bob_key.append(bob_results[i])

print("--- FULL DATA ---")
print(f"Alice's bits:  {alice_bits}")
print(f"Alice's bases: {alice_bases}")
print(f"Bob's bases:   {bob_bases}")
print(f"Bob's results: {bob_results}")

print("\n--- SIFTED KEY ---")
print(f"Alice's key: {sifted_alice_key}")
print(f"Bob's key:   {sifted_bob_key}")
print(f"Kept {len(sifted_alice_key)} out of {n} bits.")

if sifted_alice_key == sifted_bob_key:
    print("\nSUCCESS! Keys match perfectly.")
else:
    print("\nERROR! Keys do not match.")