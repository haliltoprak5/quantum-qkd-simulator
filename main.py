import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from src import BB84Protocol


NUM_QUBITS = 200


def print_results(label: str, results: dict):
    detected = results["eavesdropping_detected"]
    status = "DETECTED" if detected else "NOT DETECTED"
    color = "\033[91m" if detected else "\033[92m"
    reset = "\033[0m"

    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    print(f"  Qubits transmitted  : {results['num_qubits']}")
    print(f"  Sifted key length   : {results['sifted_key_length']} bits")
    print(f"  QBER                : {results['qber'] * 100:.1f}%")
    print(f"  Eavesdropping       : {color}{status}{reset}")


def plot_comparison(result_clean: dict, result_eve: dict):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("BB84 QKD Protocol — Simulation Results", fontsize=14, fontweight="bold")

    categories = ["Clean Channel", "Eve Present"]
    qbers = [result_clean["qber"] * 100, result_eve["qber"] * 100]
    key_lengths = [result_clean["sifted_key_length"], result_eve["sifted_key_length"]]
    colors = ["#2ecc71", "#e74c3c"]

    ax1 = axes[0]
    bars = ax1.bar(categories, qbers, color=colors, edgecolor="black", linewidth=0.8)
    ax1.axhline(y=11, color="orange", linestyle="--", linewidth=1.5, label="Security threshold (11%)")
    ax1.set_title("Quantum Bit Error Rate (QBER)")
    ax1.set_ylabel("QBER (%)")
    ax1.set_ylim(0, 35)
    ax1.legend()
    for bar, val in zip(bars, qbers):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{val:.1f}%", ha="center", va="bottom", fontweight="bold")

    ax2 = axes[1]
    bars2 = ax2.bar(categories, key_lengths, color=colors, edgecolor="black", linewidth=0.8)
    ax2.set_title("Sifted Key Length")
    ax2.set_ylabel("Bits")
    for bar, val in zip(bars2, key_lengths):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 str(val), ha="center", va="bottom", fontweight="bold")

    legend_patches = [
        mpatches.Patch(color="#2ecc71", label="No eavesdropping"),
        mpatches.Patch(color="#e74c3c", label="Eve intercept-resend"),
    ]
    fig.legend(handles=legend_patches, loc="lower center", ncol=2, frameon=False, fontsize=10)

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig("qkd_results.png", dpi=150, bbox_inches="tight")
    print("\n  Chart saved to: qkd_results.png")
    plt.show()


def plot_sample_circuit(protocol: BB84Protocol):
    qc = protocol.get_sample_circuit(index=0)
    print(f"\n  Sample circuit ({qc.name}):")
    print(qc.draw(output="text"))


def main():
    print("\nRunning BB84 simulation — no eavesdropping...")
    proto_clean = BB84Protocol(num_qubits=NUM_QUBITS, eve_present=False)
    result_clean = proto_clean.run()
    print_results("Scenario 1: Clean Channel", result_clean)

    print("\nRunning BB84 simulation — Eve present...")
    proto_eve = BB84Protocol(num_qubits=NUM_QUBITS, eve_present=True)
    result_eve = proto_eve.run()
    print_results("Scenario 2: Eavesdropper (Eve) Active", result_eve)

    plot_sample_circuit(proto_clean)
    plot_comparison(result_clean, result_eve)


if __name__ == "__main__":
    main()
