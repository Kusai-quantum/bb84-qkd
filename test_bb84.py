"""
Unit tests for the BB84 QKD simulation.
Run with: pytest test_bb84.py -v
"""
from bb84 import run_bb84, privacy_amplification, cascade_error_correction


# --- BB84 core tests ---
def test_no_eavesdropper_gives_zero_qber():
    r = run_bb84(200, eavesdrop=False, noise=0.0, seed=1)
    assert r['qber'] == 0.0

def test_eavesdropper_gives_quarter_qber():
    r = run_bb84(500, eavesdrop=True, noise=0.0, seed=2)
    assert 0.15 < r['qber'] < 0.35

def test_noise_causes_proportional_qber():
    r = run_bb84(500, eavesdrop=False, noise=0.05, seed=3)
    assert 0.02 < r['qber'] < 0.10

def test_sifting_keeps_half_the_bits():
    r = run_bb84(1000, eavesdrop=False, noise=0.0, seed=4)
    assert 400 < r['sifted_length'] < 600

def test_seed_reproducibility():
    r1 = run_bb84(100, eavesdrop=True, noise=0.05, seed=42)
    r2 = run_bb84(100, eavesdrop=True, noise=0.05, seed=42)
    assert r1 == r2

def test_different_seeds_differ():
    r1 = run_bb84(100, eavesdrop=True, noise=0.05, seed=1)
    r2 = run_bb84(100, eavesdrop=True, noise=0.05, seed=2)
    assert r1 != r2

def test_zero_qubits_edge_case():
    r = run_bb84(0, eavesdrop=False, noise=0.0, seed=5)
    assert r['qber'] == 0.0
    assert r['sifted_length'] == 0


# --- Privacy amplification tests ---
def test_privacy_amplification_is_deterministic():
    key = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1]
    assert privacy_amplification(key, 8) == privacy_amplification(key, 8)

def test_privacy_amplification_changes_input():
    key = [1, 0, 1, 1, 0, 0, 1, 0]
    assert privacy_amplification(key, 8) != key


# --- Cascade tests ---
def test_cascade_fixes_known_errors():
    alice = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0]
    bob   = [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0]  # 2 errors
    a_fix, b_fix, _, residual = cascade_error_correction(alice, bob, seed=42)
    assert residual == 0
    assert a_fix == b_fix

def test_cascade_no_errors_no_change():
    alice = [1, 0, 1, 1, 0, 0, 1, 0]
    bob   = list(alice)
    a_fix, b_fix, bits_revealed, residual = cascade_error_correction(alice, bob, seed=1)
    assert residual == 0
    assert a_fix == alice
    assert b_fix == bob

def test_cascade_reduces_errors_on_real_data():
    r = run_bb84(500, eavesdrop=False, noise=0.05, seed=7)
    errors_before = sum(1 for a, b in zip(r['sifted_alice'], r['sifted_bob']) if a != b)
    a_fix, b_fix, _, residual = cascade_error_correction(
        r['sifted_alice'], r['sifted_bob'], seed=42
    )
    assert residual < errors_before