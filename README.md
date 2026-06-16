# Quantum Key Distribution (QKD) Simulator with Eavesdropping Detection

A Python-based simulation of quantum cryptographic protocols using **IBM Qiskit**. This project implements the **BB84 Protocol** to demonstrate secure key generation between two parties (Alice and Bob) and quantifies the security impacts when an active eavesdropper (Eve) attempts to intercept the quantum channel.

## Features

- **Quantum Bit Generation:** Simulates Alice generating random bits and encoding them into quantum states using random bases (Rectilinear `+` and Diagonal `x`).
- **Active Eavesdropping (Eve):** Simulates an intercept-resend attack where Eve measures qubits mid-transit, triggering the quantum no-cloning theorem.
- **Key Sifting & Error Rate Calculation:** Implements the classic reconciliation phase, calculating the Quantum Bit Error Rate (QBER) to detect anomalies.
- **Visual Circuit Analysis:** Generates quantum circuit diagrams and statistical plots showing QBER comparisons.

## Tech Stack

- **Language:** Python 3.10+
- **Quantum Framework:** IBM Qiskit 1.x
- **Simulation Engine:** Qiskit Aer
- **Data & Visualization:** NumPy, Matplotlib

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/haliltoprak5/quantum-qkd-simulator.git
   cd quantum-qkd-simulator
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

```bash
python main.py
```

The simulation outputs:
- Sifted key length (with and without Eve)
- Quantum Bit Error Rate (QBER)
- Eavesdropping detection verdict
- Quantum circuit diagram for a sample qubit

## Theoretical Background

In classical cryptography, an attacker can silently copy data in transit. In this quantum simulation, any unauthorized measurement by Eve collapses the qubit's wave function (Heisenberg Uncertainty Principle), introducing detectable errors.

**Expected QBER:**
| Scenario | QBER |
|---|---|
| No eavesdropping | ~0% |
| Eve present (intercept-resend) | ~25% |

If the measured QBER exceeds a security threshold (default: 11%), Alice and Bob abort the key exchange, preventing any information leakage.

## BB84 Protocol Flow

```
Alice          Quantum Channel          Bob
  |                                      |
  |-- encodes bits with random bases --> |
  |                                      |-- measures with random bases
  |<------- basis comparison (public) --|
  |                                      |
  |---- keep bits where bases match ---> sifted key
  |                                      |
  |-- sample subset to estimate QBER ---|
  |                                      |
  [ if QBER < threshold: secure key confirmed ]
```

## License

MIT
