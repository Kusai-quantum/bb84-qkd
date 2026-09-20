"""
pns_attack.py — Photon-Number-Splitting (PNS) attack and its decoy-state defense.

Demonstrates:
  1. A realistic laser emitting Poisson-distributed photon numbers.
  2. Eve's PNS attack: she steals one photon from every multi-photon pulse,
     learns the key bit, and introduces ZERO QBER — undetectable in
     standard BB84 without decoy states.
  3. Decoy-state detection: by comparing photon-number statistics for a
     high-intensity signal and a low-intensity decoy, Alice and Bob can
     detect the PNS attack.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson


def p_multi(mu):
    """Probability of a pulse carrying 2+ photons, for Poisson mean mu."""
    return 1 - poisson.pmf(0, mu) - poisson.pmf(1, mu)


def simulate_pns_attack(mu, n_pulses, seed=0):
    """
    Simulate BB84 under a PNS attack with NO decoy states.

    Returns:
        multi_photon_fraction: fraction of pulses Eve can attack
        eve_info:              fraction of sifted key Eve learns
        qber:                  measured QBER (stays at 0%)
    """
    rng = np.random.default_rng(seed)
    photon_counts = rng.poisson(mu, size=n_pulses)

    # Eve attacks only multi-photon pulses. Because the remaining photons
    # carry the SAME state Alice originally sent, Bob's measurements are
    # undisturbed -> QBER remains 0%.
    multi = photon_counts >= 2
    multi_photon_fraction = multi.mean()
    eve_info = multi_photon_fraction
    qber = 0.0

    return multi_photon_fraction, eve_info, qber


def simulate_decoy_detection(mu_signal, mu_decoy, n_pulses, seed=0):
    """
    With decoy states, the PNS attack is revealed because it distorts the
    observed multi-photon statistics for the two intensities.

    Returns observed vs. theoretical multi-photon rates for each intensity.
    """
    rng = np.random.default_rng(seed)

    # Randomly assign each pulse to signal or decoy
    is_signal = rng.random(n_pulses) < 0.5
    photon_counts = np.where(
        is_signal,
        rng.poisson(mu_signal, size=n_pulses),
        rng.poisson(mu_decoy, size=n_pulses),
    )

    # Under PNS, Eve steals one photon from multi-photon pulses. This
    # slightly shifts the observed counts toward lower photon numbers,
    # making observed multi-photon rates differ from the theory.
    # (Simplified: Eve effectively "downgrades" 2-photon pulses to 1-photon.)
    simulated = photon_counts.copy()
    for i in range(len(simulated)):
        if simulated[i] >= 2:
            simulated[i] -= 1  # Eve steals one photon

    observed_signal = (simulated[is_signal] >= 2).mean()
    observed_decoy = (simulated[~is_signal] >= 2).mean()

    return {
        "signal": (p_multi(mu_signal), observed_signal),
        "decoy": (p_multi(mu_decoy), observed_decoy),
    }


def main():
    print("=" * 62)
    print(" PNS ATTACK + DECOY-STATE DEFENSE")
    print("=" * 62)

    # ---------- Part 1: attack with no decoys ----------
    print("\n--- PART 1: PNS attack, NO decoy states ---")
    mu = 0.5
    n = 100_000
    multi_frac, eve_info, qber = simulate_pns_attack(mu, n)

    print(f"Signal intensity (mu):       {mu}")
    print(f"Pulses sent:                 {n}")
    print(f"Multi-photon fraction:       {multi_frac*100:.2f}%")
    print(f"Fraction of key Eve learns:  {eve_info*100:.2f}%")
    print(f"Observed QBER:               {qber*100:.2f}%")
    print()
    print("  WARNING: Eve now knows ~1/4 of the key, and Alice/Bob")
    print("  see ZERO errors. Without decoy states, this attack is")
    print("  UNDETECTABLE.")

    # ---------- Part 2: with decoy states ----------
    print("\n--- PART 2: PNS attack WITH decoy states ---")
    mu_signal = 0.5
    mu_decoy  = 0.1
    stats = simulate_decoy_detection(mu_signal, mu_decoy, n)

    print(f"Signal intensity (mu):       {mu_signal}")
    print(f"Decoy  intensity (nu):       {mu_decoy}")
    print()
    print(f"{'Intensity':<10} {'Theory P(2+)':>14} {'Observed':>12} {'Diff':>8}")
    print("-" * 50)
    for name, (theory, observed) in stats.items():
        print(f"{name:<10} {theory:>14.4f} {observed:>12.4f} {observed-theory:>8.4f}")

    print()
    print("  Alice and Bob compare their observed multi-photon rates")
    print("  against the Poisson predictions for each intensity. Under")
    print("  a PNS attack, BOTH intensities show a distorted rate —")
    print("  which is impossible without an eavesdropper.")

    # ---------- Plot ----------
    mus = np.linspace(0.05, 0.8, 50)
    theory = [p_multi(m) for m in mus]
    plt.figure(figsize=(8, 5))
    plt.plot(mus, theory, color='steelblue', linewidth=2,
             label='Theory: P(2+ photons) for Poisson(mu)')
    plt.axvline(mu_signal, color='orange', ls='--', alpha=0.7,
                label=f'Signal mu = {mu_signal}')
    plt.axvline(mu_decoy, color='green', ls='--', alpha=0.7,
                label=f'Decoy nu = {mu_decoy}')
    plt.xlabel('Mean photon number per pulse (μ)')
    plt.ylabel('Probability of multi-photon pulse')
    plt.title('Decoy-State QKD: Why Two Intensities Defeat PNS')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('pns_decoy.png', dpi=150)
    print("\n✅ Plot saved as 'pns_decoy.png'")
    plt.show()


if __name__ == "__main__":
    main()