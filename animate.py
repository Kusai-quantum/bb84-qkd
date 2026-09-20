"""
animate.py — Visual animation of the BB84 protocol.

Creates bb84_animation.gif showing:
  - Alice sending qubits to Bob
  - Eve intercepting them (if enabled)
  - Live QBER computation

Requires: pillow  (pip install pillow)
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SIM = AerSimulator()

# ============ CONFIG ============
N_QUBITS = 25
EAVESDROP = True          # <-- set to False for the clean version
FRAMES_PER_QUBIT = 12
FPS = 20
OUTPUT = "bb84_animation.gif"
# ================================

# ---------- Pre-compute the whole run ----------
np.random.seed(7)

alice_bits  = np.random.randint(2, size=N_QUBITS)
alice_bases = np.random.randint(2, size=N_QUBITS)
bob_bases   = np.random.randint(2, size=N_QUBITS)
eve_bases   = np.random.randint(2, size=N_QUBITS)
bob_results = []

for i in range(N_QUBITS):
    qc = QuantumCircuit(1, 2) if EAVESDROP else QuantumCircuit(1, 1)
    if alice_bits[i] == 1: qc.x(0)
    if alice_bases[i] == 1: qc.h(0)
    if EAVESDROP:
        if eve_bases[i] == 1: qc.h(0)
        qc.measure(0, 0)
        qc.reset(0)
        with qc.if_test((qc.clbits[0], 1)):
            qc.x(0)
        if eve_bases[i] == 1: qc.h(0)
        if bob_bases[i] == 1: qc.h(0)
        qc.measure(0, 1)
    else:
        if bob_bases[i] == 1: qc.h(0)
        qc.measure(0, 0)
    result = SIM.run(qc, shots=1, seed_simulator=i).result().get_counts()
    bob_results.append(int(list(result.keys())[0].replace(' ', '')[0]))

outcomes = []
for i in range(N_QUBITS):
    kept = (alice_bases[i] == bob_bases[i])
    correct = (alice_bits[i] == bob_results[i]) if kept else None
    outcomes.append((kept, correct))

qber_timeline = []
running_alice, running_bob = [], []
for i in range(N_QUBITS):
    if outcomes[i][0]:
        running_alice.append(alice_bits[i])
        running_bob.append(bob_results[i])
        errs = sum(1 for a, b in zip(running_alice, running_bob) if a != b)
        qber_timeline.append(errs / len(running_alice))
    else:
        qber_timeline.append(qber_timeline[-1] if qber_timeline else 0.0)

# ---------- Figure ----------
fig, (ax_top, ax_bot) = plt.subplots(
    2, 1, figsize=(12, 7), gridspec_kw={'height_ratios': [2, 1]}
)
fig.patch.set_facecolor('#0d1117')
fig.suptitle('BB84 Quantum Key Distribution — Live Simulation',
             color='white', fontsize=14, fontweight='bold')

for ax in (ax_top, ax_bot):
    ax.set_facecolor('#0d1117')
    for spine in ax.spines.values():
        spine.set_color('#30363d')
    ax.tick_params(colors='white')

AXIS_MAX_X = 12
ax_top.set_xlim(-1, AXIS_MAX_X + 1)
ax_top.set_ylim(-1.2, 2.0)
ax_top.axis('off')

ax_top.text(0, 1.6, 'Alice', color='#7ee787', fontsize=15,
            ha='center', fontweight='bold')
ax_top.text(AXIS_MAX_X, 1.6, 'Bob', color='#79c0ff', fontsize=15,
            ha='center', fontweight='bold')
ax_top.plot([0, AXIS_MAX_X], [0, 0], color='#30363d', lw=2, zorder=1)

ax_top.scatter([0], [0], s=200, color='#7ee787', zorder=3, marker='s')
ax_top.scatter([AXIS_MAX_X], [0], s=200, color='#79c0ff', zorder=3, marker='s')

if EAVESDROP:
    ax_top.text(AXIS_MAX_X / 2, 1.6, 'Eve', color='#ff7b72',
                fontsize=15, ha='center', fontweight='bold')
    ax_top.scatter([AXIS_MAX_X / 2], [0], s=200, color='#ff7b72',
                   zorder=3, marker='x')

qubit_dot, = ax_top.plot([], [], 'o', markersize=20, zorder=5)
qubit_label = ax_top.text(0, 0, '', color='white', fontsize=11,
                          ha='center', va='center', zorder=6, fontweight='bold')
status_text = ax_top.text(AXIS_MAX_X / 2, -0.8, '', color='white',
                          fontsize=12, ha='center')

qber_line, = ax_bot.plot([], [], color='#f0883e', lw=2.5, label='QBER')
ax_bot.axhline(0.11, color='#ff7b72', ls='--', lw=1.5, label='11% threshold')
ax_bot.axhline(0.25, color='#8b949e', ls=':', lw=1.5, label='25% (Eve theory)')
ax_bot.set_xlim(0, N_QUBITS)
ax_bot.set_ylim(0, 0.4)
ax_bot.set_xlabel('Qubits processed', color='white')
ax_bot.set_ylabel('QBER', color='white')
ax_bot.legend(loc='upper right', facecolor='#161b22',
              edgecolor='#30363d', labelcolor='white', fontsize=9)
ax_bot.grid(alpha=0.15)

# ---------- Animation ----------
def update(frame):
    i = min(frame // FRAMES_PER_QUBIT, N_QUBITS - 1)
    sub = frame % FRAMES_PER_QUBIT
    progress = sub / max(FRAMES_PER_QUBIT - 1, 1)
    x = progress * AXIS_MAX_X

    if EAVESDROP and progress >= 0.5:
        if eve_bases[i] == alice_bases[i]:
            color = '#7ee787' if alice_bases[i] == 0 else '#f0883e'
        else:
            color = '#ff7b72'
    else:
        color = '#7ee787' if alice_bases[i] == 0 else '#f0883e'

    qubit_dot.set_data([x], [0])
    qubit_dot.set_color(color)

    label = 'Z' if alice_bases[i] == 0 else 'X'
    qubit_label.set_position((x, 0))
    qubit_label.set_text(label)

    kept, correct = outcomes[i]
    if progress > 0.9:
        if not kept:
            status_text.set_text(f"Qubit {i+1}: bases differ -> discarded")
            status_text.set_color('#8b949e')
        elif correct:
            status_text.set_text(f"Qubit {i+1}: bases match, no error")
            status_text.set_color('#7ee787')
        else:
            status_text.set_text(f"Qubit {i+1}: bases match, but ERROR")
            status_text.set_color('#ff7b72')
    else:
        status_text.set_text(f"Sending qubit {i+1} of {N_QUBITS}...")
        status_text.set_color('white')

    x_data = list(range(1, i + 2))
    y_data = qber_timeline[:i + 1]
    qber_line.set_data(x_data, y_data)

    return qubit_dot, qubit_label, status_text, qber_line


total_frames = N_QUBITS * FRAMES_PER_QUBIT + 20
anim = FuncAnimation(fig, update, frames=total_frames,
                     interval=1000 / FPS, blit=False)

plt.tight_layout()
print(f"Saving {OUTPUT} (this takes ~20-30 seconds)...")
anim.save(OUTPUT, writer=PillowWriter(fps=FPS))
print(f"✅ Saved {OUTPUT}")
plt.show()