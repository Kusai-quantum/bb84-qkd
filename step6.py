import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()

def run_simulation(n_qubits, eavesdrop=False):
    alice_bits = np.random.randint(2, size=n_qubits)
    alice_bases = np.random.randint(2, size=n_qubits)
    bob_bases = np.random.randint(2, size=n_qubits)
    eve_bases = np.random.randint(2, size=n_qubits)
    bob_results = []

    for i in range(n_qubits):
        if eavesdrop:
            qc = QuantumCircuit(1, 2) # 2 classical bits for Eve and Bob
        else:
            qc = QuantumCircuit(1, 1) # 1 classical bit for Bob

        # Alice encodes
        if alice_bits[i] == 1: qc.x(0)
        if alice_bases[i] == 1: qc.h(0)

        if eavesdrop:
            # Eve intercepts
            if eve_bases[i] == 1: qc.h(0)
            qc.measure(0, 0)
            qc.reset(0)
            with qc.if_test((qc.clbits[0], 1)):
                qc.x(0)
            if eve_bases[i] == 1: qc.h(0)
            # Bob measures into classical bit 1
            if bob_bases[i] == 1: qc.h(0)
            qc.measure(0, 1)
        else:
            # Bob measures normally into classical bit 0
            if bob_bases[i] == 1: qc.h(0)
            qc.measure(0, 0)

        result = sim.run(qc, shots=1).result().get_counts()
        key = list(result.keys())[0].replace(' ', '')
        bob_results.append(int(key[0]))

    # Sifting
    sifted_alice = []
    sifted_bob = []
    for i in range(n_qubits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])

    # QBER Calculation
    errors = sum(1 for a, b in zip(sifted_alice, sifted_bob) if a != b)
    qber = errors / len(sifted_alice) if len(sifted_alice) > 0 else 0
    return qber

# --- RUN THE EXPERIMENT ---
n_values = [50, 100, 200, 400, 800]
qbers_no_eve = []
qbers_with_eve = []

print("Running simulations for the graph... (this might take a minute)")
for n in n_values:
    print(f"Testing with {n} qubits...")
    # Average over 5 runs to smooth out the randomness
    avg_no_eve = np.mean([run_simulation(n, eavesdrop=False) for _ in range(5)])
    avg_with_eve = np.mean([run_simulation(n, eavesdrop=True) for _ in range(5)])
    
    qbers_no_eve.append(avg_no_eve)
    qbers_with_eve.append(avg_with_eve)

# --- PLOT THE GRAPH ---
plt.figure(figsize=(8, 5))
plt.plot(n_values, qbers_no_eve, 'o-', color='green', label='No Eavesdropper')
plt.plot(n_values, qbers_with_eve, 's-', color='red', label='Eavesdropper (Intercept-Resend)')
plt.axhline(0.11, color='black', linestyle='--', label='Security Threshold (~11%)')

plt.xlabel('Number of Transmitted Qubits')
plt.ylabel('Quantum Bit Error Rate (QBER)')
plt.title('BB84 QKD: Detecting an Eavesdropper')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

# Save the image
plt.savefig('qber_plot.png', dpi=150)
print("\nSUCCESS! Graph saved as 'qber_plot.png' in your folder.")
plt.show()