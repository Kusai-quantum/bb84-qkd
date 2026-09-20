import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()
n = 10

alice_bits = np.random.randint(2, size=n)
alice_bases = np.random.randint(2, size=n)
bob_bases = np.random.randint(2, size=n)
bob_results = []

print("--- Starting the Exchange ---\n")

for i in range(n):
    qc = QuantumCircuit(1, 1)
    if alice_bits[i] == 1: qc.x(0)
    if alice_bases[i] == 1: qc.h(0)
    if bob_bases[i] == 1: qc.h(0)
    qc.measure(0, 0)
    
    result = sim.run(qc, shots=1).result().get_counts()
    measured_bit = int(list(result.keys())[0])
    bob_results.append(measured_bit)
    
    alice_basis_name = "Z" if alice_bases[i] == 0 else "X"
    bob_basis_name = "Z" if bob_bases[i] == 0 else "X"
    
    print(f"Round {i+1}: Alice={alice_basis_name}, Bob={bob_basis_name} | Alice bit={alice_bits[i]}, Bob got={measured_bit}")
    if alice_bases[i] == bob_bases[i]:
        print("  -> MATCH!")
    else:
        print("  -> No match (random)")

print(f"\nAlice's bits:  {alice_bits}")
print(f"Bob's results: {bob_results}")