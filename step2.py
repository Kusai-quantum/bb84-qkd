from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()

# --- CASE 1: SAME BASIS ---
# Alice sends bit 0 in the Z basis. Bob measures in the Z basis.
qc1 = QuantumCircuit(1, 1)
# (No gates needed for Alice to send 0 in Z basis)
qc1.measure(0, 0) 
print("Case 1: Alice=Z, Bob=Z")
print(sim.run(qc1, shots=10).result().get_counts())
print("-" * 30)

# --- CASE 2: DIFFERENT BASIS ---
# Alice sends bit 0 in the Z basis. Bob measures in the X basis.
qc2 = QuantumCircuit(1, 1)
qc2.h(0) # This is Bob's X-basis measurement
qc2.measure(0, 0)
print("Case 2: Alice=Z, Bob=X")
print(sim.run(qc2, shots=10).result().get_counts())
print("-" * 30)

# --- CASE 3: DIFFERENT BASIS (the other way) ---
# Alice sends bit 0 in the X basis. Bob measures in the Z basis.
qc3 = QuantumCircuit(1, 1)
qc3.h(0) # This is Alice preparing in X basis
qc3.measure(0, 0)
print("Case 3: Alice=X, Bob=Z")
print(sim.run(qc3, shots=10).result().get_counts())
print("-" * 30)

# --- CASE 4: SAME BASIS (X) ---
# Alice sends bit 0 in the X basis. Bob measures in the X basis.
qc4 = QuantumCircuit(1, 1)
qc4.h(0) # Alice prepares
qc4.h(0) # Bob measures
qc4.measure(0, 0)
print("Case 4: Alice=X, Bob=X")
print(sim.run(qc4, shots=10).result().get_counts())
print("-" * 30)