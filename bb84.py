import argparse
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SIM = AerSimulator()


# ---------------------------------------------------------------
# Privacy Amplification
# ---------------------------------------------------------------
def privacy_amplification(key_bits, target_length):
    """Compress a key using SHA-256."""
    if len(key_bits) == 0:
        return []
    key_str = ''.join(map(str, key_bits))
    digest = hashlib.sha256(key_str.encode()).digest()
    bits = [(byte >> i) & 1 for byte in digest for i in range(7, -1, -1)]
    counter = 0
    while len(bits) < target_length:
        counter += 1
        digest = hashlib.sha256((key_str + str(counter)).encode()).digest()
        bits.extend([(byte >> i) & 1 for byte in digest for i in range(7, -1, -1)])
    return bits[:target_length]


# ---------------------------------------------------------------
# Cascade Error Correction
# ---------------------------------------------------------------
def cascade_error_correction(alice_key, bob_key, block_size=4, passes=4, seed=None):
    """
    Simplified Cascade protocol.

    Alice and Bob publicly compare parities of blocks and use binary
    search to locate errors. Returns:
        (corrected_alice, corrected_bob, bits_revealed, residual_errors)
    """
    if seed is not None:
        np.random.seed(seed)

    alice = list(alice_key)
    bob = list(bob_key)
    n = len(alice)
    bits_revealed = 0

    for p in range(passes):
        size = block_size * (2 ** p)
        if size > n:
            break

        # Alice and Bob agree on a public permutation for this pass
        perm = np.random.permutation(n).tolist()

        for start in range(0, n, size):
            block_idx = perm[start:start + size]
            if len(block_idx) < 2:
                continue

            alice_parity = sum(alice[i] for i in block_idx) % 2
            bob_parity = sum(bob[i] for i in block_idx) % 2
            bits_revealed += 1

            if alice_parity != bob_parity:
                # Odd number of errors -> binary search to find one
                candidates = list(block_idx)
                while len(candidates) > 1:
                    mid = len(candidates) // 2
                    left = candidates[:mid]
                    right = candidates[mid:]

                    a_par = sum(alice[i] for i in left) % 2
                    b_par = sum(bob[i] for i in left) % 2
                    bits_revealed += 1

                    candidates = left if a_par != b_par else right

                # Flip Bob's bit at the located error
                err_idx = candidates[0]
                bob[err_idx] ^= 1

    residual = sum(1 for a, b in zip(alice, bob) if a != b)
    return alice, bob, bits_revealed, residual


# ---------------------------------------------------------------
# BB84 Simulation
# ---------------------------------------------------------------
def run_bb84(n_qubits, eavesdrop=False, noise=0.0, seed=None):
    if seed is not None:
        np.random.seed(seed)

    alice_bits = np.random.randint(2, size=n_qubits)
    alice_bases = np.random.randint(2, size=n_qubits)
    bob_bases = np.random.randint(2, size=n_qubits)
    bob_results = []
    eve_bases = np.random.randint(2, size=n_qubits)

    for i in range(n_qubits):
        qc = QuantumCircuit(1, 2) if eavesdrop else QuantumCircuit(1, 1)

        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)

        if noise > 0.0 and np.random.random() < noise:
            qc.x(0)

        if eavesdrop:
            if eve_bases[i] == 1:
                qc.h(0)
            qc.measure(0, 0)
            qc.reset(0)
            with qc.if_test((qc.clbits[0], 1)):
                qc.x(0)
            if eve_bases[i] == 1:
                qc.h(0)
            if bob_bases[i] == 1:
                qc.h(0)
            qc.measure(0, 1)
        else:
            if bob_bases[i] == 1:
                qc.h(0)
            qc.measure(0, 0)

        result = SIM.run(qc, shots=1, seed_simulator=seed).result().get_counts()
        key = list(result.keys())[0].replace(' ', '')
        bob_results.append(int(key[0]))

    sifted_alice = []
    sifted_bob = []
    for i in range(n_qubits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(int(alice_bits[i]))
            sifted_bob.append(int(bob_results[i]))

    errors = sum(1 for a, b in zip(sifted_alice, sifted_bob) if a != b)
    qber = errors / len(sifted_alice) if len(sifted_alice) > 0 else 0.0

    return {
        'qber': qber,
        'sifted_length': len(sifted_alice),
        'sifted_alice': sifted_alice,
        'sifted_bob': sifted_bob,
    }


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="BB84 QKD Simulation with Cascade + Privacy Amplification")
    parser.add_argument("--qubits", type=int, default=200)
    parser.add_argument("--eavesdrop", action="store_true")
    parser.add_argument("--noise", type=float, default=0.0)
    parser.add_argument("--correct", action="store_true",
                        help="Run Cascade error correction on the sifted key")
    parser.add_argument("--amplify", action="store_true",
                        help="Run privacy amplification")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    # ---- Plot mode ----
    if args.plot:
        print("Generating QBER plot...")
        n_values = [50, 100, 200, 400, 800]
        qbers_no_eve = []
        qbers_with_eve = []
        for n in n_values:
            avg_no_eve = np.mean([run_bb84(n, eavesdrop=False, seed=i)['qber'] for i in range(5)])
            avg_with_eve = np.mean([run_bb84(n, eavesdrop=True, seed=i)['qber'] for i in range(5)])
            qbers_no_eve.append(avg_no_eve)
            qbers_with_eve.append(avg_with_eve)

        plt.figure(figsize=(8, 5))
        plt.plot(n_values, qbers_no_eve, 'o-', color='green', label='No Eavesdropper')
        plt.plot(n_values, qbers_with_eve, 's-', color='red', label='Eavesdropper')
        plt.axhline(0.11, color='black', linestyle='--', label='Security Threshold (~11%)')
        plt.xlabel('Number of Transmitted Qubits')
        plt.ylabel('QBER')
        plt.title('BB84: Detecting an Eavesdropper')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('qber_plot.png', dpi=150)
        print("✅ Saved as 'qber_plot.png'")
        plt.show()
        return

    # ---- Single run ----
    print(f"Running BB84 with {args.qubits} qubits...")
    if args.eavesdrop:
        print("⚠️  Eve is ACTIVE!")
    else:
        print("🔒 No eavesdropper.")
    if args.noise > 0.0:
        print(f"📡 Channel noise: {args.noise * 100:.1f}%")

    result = run_bb84(args.qubits, eavesdrop=args.eavesdrop, noise=args.noise)
    qber = result['qber']

    print("\n--- STAGE 1: SIFTING ---")
    print(f"Sifted key length: {result['sifted_length']} bits")
    print(f"QBER: {qber * 100:.2f}%")

    if qber > 0.11:
        print("🚨 ALERT: Eavesdropper detected! Aborting key.")
        return
    print("✅ QBER below threshold. Proceeding.")

    alice_key = result['sifted_alice']
    bob_key = result['sifted_bob']

    # ---- Cascade Error Correction ----
    if args.correct:
        print("\n--- STAGE 2: CASCADE ERROR CORRECTION ---")
        errors_before = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
        print(f"Errors before correction: {errors_before}")

        alice_key, bob_key, bits_revealed, residual = cascade_error_correction(
            alice_key, bob_key, block_size=4, passes=4, seed=42
        )

        print(f"Bits revealed publicly:   {bits_revealed}")
        print(f"Errors after correction:  {residual}")
        if residual == 0:
            print("✅ Keys are now IDENTICAL.")
        else:
            print(f"⚠️  {residual} residual errors remain. Key is unsafe.")

    # ---- Privacy Amplification ----
    if args.amplify:
        print("\n--- STAGE 3: PRIVACY AMPLIFICATION ---")
        target = max(1, len(alice_key) // 2)
        final_alice = privacy_amplification(alice_key, target)
        final_bob = privacy_amplification(bob_key, target)

        print(f"Raw key length:     {len(alice_key)} bits")
        print(f"Amplified key:      {target} bits")
        print(f"Alice's final key:  {''.join(map(str, final_alice))}")
        print(f"Bob's final key:    {''.join(map(str, final_bob))}")

        if final_alice == final_bob:
            print("✅ Final keys MATCH. Ready for encryption.")
        else:
            print("❌ Final keys do NOT match. Abort.")


if __name__ == "__main__":
    main()