from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Create a circuit with 1 qubit and 1 classical bit
qc = QuantumCircuit(1, 1)

# Apply a Hadamard gate to qubit 0
qc.h(0)

# Measure qubit 0, store the result in classical bit 0
qc.measure(0, 0)

# Print the circuit as text
print(qc.draw('text'))

# Run the circuit 1000 times
sim = AerSimulator()
result = sim.run(qc, shots=1000).result()
counts = result.get_counts()

print(counts)