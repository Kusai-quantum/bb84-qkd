# BB84 Quantum Key Distribution Simulation

A Python + Qiskit simulation of the **BB84 quantum key distribution protocol**, with eavesdropper detection, Cascade error correction, and privacy amplification.

![QBER plot](qber_plot.png)

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
