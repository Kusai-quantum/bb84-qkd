# BB84 Quantum Key Distribution Simulation

[![Tests](https://github.com/Kusai-quantum/bb84-qkd/actions/workflows/tests.yml/badge.svg)](https://github.com/Kusai-quantum/bb84-qkd/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Qiskit](https://img.shields.io/badge/Qiskit-1.x-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
A Python + Qiskit simulation of the **BB84 quantum key distribution protocol**, with eavesdropper detection, Cascade error correction, and privacy amplification.

![QBER plot](qber_plot.png)

## Live Simulation

![BB84 Animation](bb84_animation.gif)

*The dot travels from Alice to Bob. When Eve (the red X in the middle) intercepts and guesses the wrong basis, the dot turns red, and the QBER climbs toward 25%.*

## Motivation

Today's financial infrastructure relies on RSA and elliptic-curve cryptography — both broken by a sufficiently large quantum computer running Shor's algorithm. QKD is a physics-based alternative: security comes from the **no-cloning theorem** and the **measurement-disturbance principle**, not from computational hardness.

This project simulates BB84 end-to-end to demonstrate how banks could detect an eavesdropper using quantum physics alone.

## Features

- ✅ Full BB84 protocol: bit encoding, basis reconciliation, sifting
- ✅ **Intercept-resend eavesdropper** that introduces a measurable ~25% QBER
- ✅ **Channel noise simulation** (bit-flip probability)
- ✅ **Cascade error correction** to fix errors in the sifted key
- ✅ **Privacy amplification** via SHA-256 to compress the key against Eve's knowledge
- ✅ **Interactive animation** showing the protocol in real time (`animate.py`)
- ✅ **13 unit tests** covering every stage of the pipeline
- ✅ **GitHub Actions CI** running tests on every push

## Results

| Scenario | QBER |
|----------|------|
| No eavesdropper, no noise | ~0% |
| 5% channel noise | ~5% |
| Eavesdropper (intercept-resend) | ~25% |
| Security threshold | 11% |

The jump from 0% to 25% when Eve listens is the entire point of BB84: any eavesdropper is detectable.

## Installation

```bash
git clone https://github.com/Kusai-quantum/bb84-qkd.git
cd bb84-qkd
pip install -r requirements.txt
```

## Usage

**Basic run (no eavesdropper):**
```bash
python bb84.py
```

**Simulate an eavesdropper:**
```bash
python bb84.py --eavesdrop
```

**Add 5% channel noise:**
```bash
python bb84.py --noise 0.05
```

**Full pipeline (sift → correct → amplify):**
```bash
python bb84.py --noise 0.05 --correct --amplify
```

**Generate the QBER plot:**
```bash
python bb84.py --plot
```

**Run the animation (creates `bb84_animation.gif`):**
```bash
python animate.py
```

**Run the test suite:**
```bash
pytest test_bb84.py -v
```

## How it works

### 1. The exchange
Alice picks a random bit and a random basis (Z or X) for each qubit, encodes it, and sends it to Bob. Bob measures in a randomly chosen basis.

### 2. Sifting
Alice and Bob publicly compare their bases (never their bits). Bits where the bases matched form the **sifted key**.

### 3. Eavesdropper detection (QBER)
If Eve intercepts and re-sends qubits, she guesses the wrong basis 50% of the time, causing Bob to get a random result 50% of those times. Result: **~25% QBER** — far above the 11% security threshold.

### 4. Cascade error correction
Alice and Bob use public parity comparisons and binary search to locate and fix residual errors — without ever revealing the key.

### 5. Privacy amplification
Both parties hash their key with SHA-256, compressing it into a shorter string that Eve has essentially zero information about.

## Tech Stack

- Python 3.10+
- Qiskit 1.x + Qiskit Aer
- NumPy, Matplotlib, Pillow
- Pytest for unit testing
- GitHub Actions for CI

## References

- Bennett, C. H., & Brassard, G. (1984). *Quantum cryptography: Public key distribution and coin tossing.*
- Shor, P. W., & Preskill, J. (2000). *Simple proof of security of the BB84 quantum key distribution protocol.*
- Qiskit documentation: https://qiskit.org

## License

MIT
