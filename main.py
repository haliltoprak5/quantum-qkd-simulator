import argparse
import json
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from src import BB84Protocol
from src.qkd_protocol import QBER_SECURITY_THRESHOLD


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="qkd-simulator",
        description="BB84 Quantum Key Distribution simulator with eavesdropping detection",
    )
    parser.add_argument(
        "--qubits", type=int, default=200,
        metavar="N",
        help="Number of qubits to transmit (default: 200, min: 10)",
    )
    parser.add_argument(
        "--eve", action="store_true", default=False,
        help="Enable eavesdropper (Eve) using intercept-resend attack",
    )
    parser.add_argument(
        "--threshold", type=float, default=QBER_SECURITY_THRESHOLD,
        metavar="FLOAT",
        help=f"QBER security threshold 0.0-1.0 (default: {QBER_SECURITY_THRESHOLD})",
    )
    parser.add_argument(
        "--no-plot", action="store_true", default=False,
        help="Skip chart generation, print results to terminal only",
    )
    parser.add_argument(
        "--save-key", type=str, default=None,
        metavar="FILE",
        help="Save sifted key bits to a JSON file (e.g. --save-key key.json)",
    )
    parser.add_argument(
        "--compare", action="store_true", default=False,
        help="Run both clean and Eve scenarios side-by-side for comparison",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace):
    if args.qubits < 10:
        print("Error: --qubits must be at least 10", file=sys.stderr)
        sys.exit(1)
    if not 0.0 < args.threshold < 1.0:
        print("Error: --threshold must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)


def print_results(label: str, results: dict, threshold: float):
    detected = results["qber"] > threshold
    status = "DETECTED" if detected else "NOT DETECTED"
    color = "\033[91m" if detected else "\033[92m"
    reset = "\033[0m"

    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    print(f"  Qubits transmitted  : {results['num_qubits']}")
    print(f"  Sifted key length   : {results['sifted_key_length']} bits")
    print(f"  QBER                : {results['qber'] * 100:.1f}%")
    print(f"  Security threshold  : {threshold * 100:.1f}%")
    print(f"  Eavesdropping       : {color}{status}{reset}")


def save_key(results: dict, filepath: str):
    payload = {
        "sifted_key_length": results["sifted_key_length"],
        "qber": results["qber"],
        "eavesdropping_detected": results["eavesdropping_detected"],
        "key_bits": [int(b) for b in results["sifted_key"]],
    }
    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\n  Key saved to: {filepath}")


def plot_comparison(result_clean: dict, result_eve: dict, threshold: float):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("BB84 QKD Protocol — Simulation Results", fontsize=14, fontweight="bold")

    categories = ["Clean Channel", "Eve Present"]
    qbers = [result_clean["qber"] * 100, result_eve["qber"] * 100]
    key_lengths = [result_clean["sifted_key_length"], result_eve["sifted_key_length"]]
    colors = ["#2ecc71", "#e74c3c"]

    ax1 = axes[0]
    bars = ax1.bar(categories, qbers, color=colors, edgecolor="black", linewidth=0.8)
    ax1.axhline(
        y=threshold * 100, color="orange", linestyle="--",
        linewidth=1.5, label=f"Security threshold ({threshold*100:.0f}%)"
    )
    ax1.set_title("Quantum Bit Error Rate (QBER)")
    ax1.set_ylabel("QBER (%)")
    ax1.set_ylim(0, 35)
    ax1.legend()
    for bar, val in zip(bars, qbers):
        ax1.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", va="bottom", fontweight="bold"
        )

    ax2 = axes[1]
    bars2 = ax2.bar(categories, key_lengths, color=colors, edgecolor="black", linewidth=0.8)
    ax2.set_title("Sifted Key Length")
    ax2.set_ylabel("Bits")
    for bar, val in zip(bars2, key_lengths):
        ax2.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            str(val), ha="center", va="bottom", fontweight="bold"
        )

    legend_patches = [
        mpatches.Patch(color="#2ecc71", label="No eavesdropping"),
        mpatches.Patch(color="#e74c3c", label="Eve intercept-resend"),
    ]
    fig.legend(handles=legend_patches, loc="lower center", ncol=2, frameon=False, fontsize=10)
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig("qkd_results.png", dpi=150, bbox_inches="tight")
    print("\n  Chart saved to: qkd_results.png")
    plt.show()


def plot_single(result: dict, threshold: float, label: str):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle(f"BB84 QKD — {label}", fontsize=13, fontweight="bold")

    color = "#e74c3c" if result["eve_present"] else "#2ecc71"

    ax1 = axes[0]
    ax1.bar(["QBER"], [result["qber"] * 100], color=color, edgecolor="black", linewidth=0.8)
    ax1.axhline(y=threshold * 100, color="orange", linestyle="--", linewidth=1.5,
                label=f"Threshold ({threshold*100:.0f}%)")
    ax1.set_title("Quantum Bit Error Rate")
    ax1.set_ylabel("QBER (%)")
    ax1.set_ylim(0, 35)
    ax1.legend()
    ax1.text(0, result["qber"] * 100 + 0.5, f"{result['qber']*100:.1f}%",
             ha="center", va="bottom", fontweight="bold")

    ax2 = axes[1]
    ax2.bar(["Sifted Key"], [result["sifted_key_length"]], color=color,
            edgecolor="black", linewidth=0.8)
    ax2.set_title("Sifted Key Length")
    ax2.set_ylabel("Bits")
    ax2.text(0, result["sifted_key_length"] + 0.5, str(result["sifted_key_length"]),
             ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    plt.savefig("qkd_results.png", dpi=150, bbox_inches="tight")
    print("\n  Chart saved to: qkd_results.png")
    plt.show()


def run_compare(args: argparse.Namespace):
    print("\nRunning BB84 — clean channel...")
    proto_clean = BB84Protocol(num_qubits=args.qubits, eve_present=False)
    result_clean = proto_clean.run()
    print_results("Scenario 1: Clean Channel", result_clean, args.threshold)

    print("\nRunning BB84 — Eve present...")
    proto_eve = BB84Protocol(num_qubits=args.qubits, eve_present=True)
    result_eve = proto_eve.run()
    print_results("Scenario 2: Eavesdropper (Eve) Active", result_eve, args.threshold)

    if not args.no_plot:
        plot_comparison(result_clean, result_eve, args.threshold)

    if args.save_key:
        save_key(result_clean, f"clean_{args.save_key}")
        save_key(result_eve, f"eve_{args.save_key}")


def run_single(args: argparse.Namespace):
    label = "Eve Present" if args.eve else "Clean Channel"
    print(f"\nRunning BB84 — {label}...")

    proto = BB84Protocol(num_qubits=args.qubits, eve_present=args.eve)
    result = proto.run()
    print_results(label, result, args.threshold)

    if not args.no_plot:
        plot_single(result, args.threshold, label)

    if args.save_key:
        save_key(result, args.save_key)


def main():
    args = parse_args()
    validate_args(args)

    if args.compare:
        run_compare(args)
    else:
        run_single(args)


if __name__ == "__main__":
    main()
