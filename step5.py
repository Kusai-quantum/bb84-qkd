import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()
n = 200  # Send 200 qubits to make the error rate very clear

# Alice's data
alice_bits = np.random.randint(2, size=n)
alice_bases = np.random.randint(2, size=n) # 0=Z, 1=X

# Bob's data
bob_bases = np.random.randint(2, size=n)
bob_results = []

# Eve's data (The Hacker)
eve_bases = np.random.randint(2, size=n)

print(f"Simulating {n} qubits with Eve listening...\n")

for i in range(n):
    # 1 qubit, 2 classical bits (one for Eve, one for Bob)
    qc = QuantumCircuit(1, 2)
    
    # --- ALICE ENCODES ---
    if alice_bits[i] == 1: qc.x(0)
    if alice_bases[i] == 1: qc.h(0)
    
    # --- EVE INTERCEPTS ---
    if eve_bases[i] == 1: qc.h(0) # Eve measures in her guessed basis
    qc.measure(0, 0)              # Eve measures the qubit
    qc.reset(0)                   # Eve destroys the original qubit
    
    # Eve prepares a new qubit based on what she measured
    with qc.if_test((qc.clbits[0], 1)): # If Eve measured a 1...
        qc.x(0)                         # ...she prepares a 1
    if eve_bases[i] == 1: qc.h(0)       # Eve prepares it in her basis
    
    # --- BOB MEASURES ---
    if bob_bases[i] == 1: qc.h(0)
    qc.measure(0, 1) # Bob measures into classical bit 1
    
    # Run the simulation
    result = sim.run(qc, shots=1).result().get_counts()
    key = list(result.keys())[0].replace(' ', '')
    
    # The string format is 'Bob_bit Eve_bit'. We only want Bob's bit.
    bob_results.append(int(key[0]))

# --- SIFTING ---
sifted_alice = []
sifted_bob = []

for i in range(n):
    if alice_bases[i] == bob_bases[i]:
        sifted_alice.append(alice_bits[i])
        sifted_bob.append(bob_results[i])

# --- CALCULATING QBER ---
errors = 0
for a, b in zip(sifted_alice, sifted_bob):
    if a != b:
        errors += 1

qber = errors / len(sifted_alice) if len(sifted_alice) > 0 else 0

print("--- FINAL RESULTS ---")
print(f"Sifted key length: {len(sifted_alice)} bits")
print(f"Number of errors: {errors}")
print(f"QBER (Quantum Bit Error Rate): {qber * 100:.2f}%")
print("-" * 30)

if qber > 0.11:
    print("🚨 ALERT: QBER is above 11%!")
    print("Eavesdropper detected! The bank aborts the key.")
else:
    print("✅ QBER is low. No eavesdropper detected. Key is safe.")