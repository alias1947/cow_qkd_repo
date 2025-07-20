import matplotlib.pyplot as plt
from simulation.Network import Network
from main import calculate_qber
import numpy as np

def run_two_node_bb84_simulation(link_distance_km=20, num_pulses_per_link=10000, mu=0.2,
                                 detector_efficiency=0.9, dark_count_rate_per_ns=1e-7, pulse_repetition_rate_ns=1):
    temp_network = Network()
    node_ids = ['Node_0', 'Node_1']
    temp_network.add_node(node_ids[0], avg_photon_number=mu)
    temp_network.add_node(node_ids[1], detector_efficiency=detector_efficiency, dark_count_rate=dark_count_rate_per_ns)
    temp_network.connect_nodes(node_ids[0], node_ids[1], distance_km=link_distance_km)
    alice_key, bob_key = temp_network.nodes[node_ids[0]].generate_and_share_key_bb84(
        temp_network.nodes[node_ids[1]], num_pulses_per_link, pulse_repetition_rate_ns
    )
    if alice_key is None:
        alice_key = []
    if bob_key is None:
        bob_key = []
    min_len = min(len(alice_key), len(bob_key))
    alice_key_trunc = alice_key[:min_len]
    bob_key_trunc = bob_key[:min_len]
    qber, num_errors = calculate_qber(alice_key_trunc, bob_key_trunc)
    return min_len, qber

def test_two_node_bb84_qber_vs_distance(num_trials=15):
    distances = [15, 20, 25, 30, 35, 40, 45, 50]
    avg_qbers = []
    avg_key_lengths = []
    for d in distances:
        qbers = []
        key_lengths = []
        for _ in range(num_trials):
            key_len, qber = run_two_node_bb84_simulation(link_distance_km=d)
            qbers.append(qber)
            key_lengths.append(key_len)
        avg_qber = np.mean(qbers)
        avg_key_len = np.mean(key_lengths)
        avg_qbers.append(avg_qber)
        avg_key_lengths.append(avg_key_len)
        print(f"Distance: {d} km, Avg QBER: {avg_qber:.4f}, Avg Key length: {avg_key_len:.2f}")
    plt.figure()
    plt.plot(distances, avg_qbers, marker='o')
    plt.xlabel('Link Distance (km)')
    plt.ylabel('Average QBER')
    plt.title(f'BB84 Average QBER vs Link Distance (2 nodes, {num_trials} trials)')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    test_two_node_bb84_qber_vs_distance(num_trials=10) 