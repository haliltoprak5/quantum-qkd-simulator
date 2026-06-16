import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


RECTILINEAR = 0  # |0> and |1> basis
DIAGONAL = 1     # |+> and |-> basis

QBER_SECURITY_THRESHOLD = 0.11


class BB84Protocol:
    """Simulates the BB84 quantum key distribution protocol.

    Supports optional eavesdropping (Eve) using an intercept-resend attack.
    Eve measures each qubit with a random basis and re-prepares it, which
    introduces ~25% QBER due to basis mismatch — detectable by Alice and Bob.
    """

    def __init__(self, num_qubits: int = 100, eve_present: bool = False):
        if num_qubits < 10:
            raise ValueError("num_qubits must be at least 10 for meaningful statistics")
        self.num_qubits = num_qubits
        self.eve_present = eve_present
        self.simulator = AerSimulator()

        self.alice_bits: np.ndarray = np.array([])
        self.alice_bases: np.ndarray = np.array([])
        self.bob_bases: np.ndarray = np.array([])
        self.bob_results: list[int] = []
        self.sifted_key: list[int] = []
        self.qber: float = 0.0

    def _encode_qubit(self, bit: int, basis: int) -> QuantumCircuit:
        """Builds a single-qubit circuit encoding Alice's bit in the chosen basis."""
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)
        if basis == DIAGONAL:
            qc.h(0)
        return qc

    def _eve_intercept(self, qc: QuantumCircuit) -> QuantumCircuit:
        """Intercept-resend attack: Eve measures and re-prepares the qubit.

        Eve picks a random basis. If she guesses wrong, the re-prepared qubit
        will introduce a 50% chance of error at Bob's detector.
        """
        eve_basis = np.random.randint(0, 2)
        if eve_basis == DIAGONAL:
            qc.h(0)
        qc.measure(0, 0)

        job = self.simulator.run(qc, shots=1)
        eve_result = int(list(job.result().get_counts().keys())[0])

        fresh = QuantumCircuit(1, 1)
        if eve_result == 1:
            fresh.x(0)
        if eve_basis == DIAGONAL:
            fresh.h(0)
        return fresh

    def _measure_qubit(self, qc: QuantumCircuit, basis: int) -> int:
        """Bob measures in his randomly chosen basis and returns the classical bit."""
        if basis == DIAGONAL:
            qc.h(0)
        qc.measure(0, 0)

        job = self.simulator.run(qc, shots=1)
        return int(list(job.result().get_counts().keys())[0])

    def run(self) -> dict:
        """Executes the full BB84 protocol and returns results."""
        self.alice_bits = np.random.randint(0, 2, self.num_qubits)
        self.alice_bases = np.random.randint(0, 2, self.num_qubits)
        self.bob_bases = np.random.randint(0, 2, self.num_qubits)

        self.bob_results = []
        for i in range(self.num_qubits):
            qc = self._encode_qubit(self.alice_bits[i], self.alice_bases[i])
            if self.eve_present:
                qc = self._eve_intercept(qc)
            result = self._measure_qubit(qc, self.bob_bases[i])
            self.bob_results.append(result)

        self._sift_key()
        self._estimate_qber()

        return {
            "num_qubits": self.num_qubits,
            "eve_present": self.eve_present,
            "sifted_key_length": len(self.sifted_key),
            "qber": round(self.qber, 4),
            "eavesdropping_detected": self.qber > QBER_SECURITY_THRESHOLD,
            "sifted_key": self.sifted_key,
        }

    def _sift_key(self):
        """Keeps only bits where Alice and Bob used the same basis."""
        self.sifted_key = [
            self.alice_bits[i]
            for i in range(self.num_qubits)
            if self.alice_bases[i] == self.bob_bases[i]
        ]
        self._bob_sifted = [
            self.bob_results[i]
            for i in range(self.num_qubits)
            if self.alice_bases[i] == self.bob_bases[i]
        ]

    def _estimate_qber(self):
        """Samples a subset of the sifted key to compute the error rate."""
        if not self.sifted_key:
            self.qber = 0.0
            return

        sample_size = max(1, len(self.sifted_key) // 4)
        indices = np.random.choice(len(self.sifted_key), sample_size, replace=False)
        errors = sum(
            1 for i in indices if self.sifted_key[i] != self._bob_sifted[i]
        )
        self.qber = errors / sample_size

    def get_sample_circuit(self, index: int = 0) -> QuantumCircuit:
        """Returns the encoded+measured circuit for a given qubit index (for visualization)."""
        if not self.alice_bits.size:
            raise RuntimeError("Call run() before requesting a sample circuit")
        qc = self._encode_qubit(self.alice_bits[index], self.alice_bases[index])
        if self.bob_bases[index] == DIAGONAL:
            qc.h(0)
        qc.measure(0, 0)
        qc.name = f"Qubit {index} | Alice basis={'x' if self.alice_bases[index] else '+'}"
        return qc
