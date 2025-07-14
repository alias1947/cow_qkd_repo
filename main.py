# main_simulation.py

# We only import the Network class, as it manages the Alice/Bob components internally
from simulation.Network import Network

import math # Still used for QBER calculation, even if not formal post-processing
import random

def calculate_qber(alice_sifted_key, bob_sifted_key, dr=0.10, seed=None):
    """
    Calculates the QBER using a random sample (disclose rate, DR) of the sifted key.
    Only a fraction (DR) of the key is publicly compared for QBER estimation.
    """
    if len(alice_sifted_key) != len(bob_sifted_key):
        raise ValueError("Sifted keys must be of the same length to calculate QBER.")

    key_length = len(alice_sifted_key)
    if key_length == 0:
        return 0.0, 0

    sample_size = max(1, int(dr * key_length))
    indices = list(range(key_length))
    if seed is not None:
        random.seed(seed)
    sample_indices = random.sample(indices, sample_size)

    num_errors = 0
    for idx in sample_indices:
        # print("sample index")
        if alice_sifted_key[idx] != bob_sifted_key[idx]:
            num_errors += 1

    qber = num_errors / sample_size
    return qber, num_errors

def postprocessing(raw_key_length, qber, dr=0.10, error_correction_efficiency=1.2, privacy_amplification_ratio=0.5):
    """
    Simulates postprocessing as described in QKD theory:
    - Parameter estimation: uses a fraction DR of the key for QBER estimation
    - Error correction: reduces key length based on QBER and error correction efficiency
    - Privacy amplification: further compresses the key using a compression ratio (CR)
    Returns the final key length and a breakdown of each step.
    """
    # Parameter estimation: remove DR fraction for QBER estimation
    key_after_dr = raw_key_length * (1 - dr)
    # Error correction: remove fraction based on QBER and efficiency
    # (Shannon limit: h(QBER), efficiency > 1)
    from math import log2
    def binary_entropy(x):
        if x == 0 or x == 1:
            return 0.0
        return -x * log2(x) - (1 - x) * log2(1 - x)
    ec_fraction = error_correction_efficiency * binary_entropy(qber)
    key_after_ec = key_after_dr * (1 - ec_fraction)
    # Privacy amplification: further compress
    key_after_pa = key_after_ec * (1 - privacy_amplification_ratio)
    
    # Ensure final key length is not negative
    final_key_length = max(0, int(key_after_pa))
    
    # Warn if QBER is too high for secure key generation
    if qber > 0.10:  # 10% is now the upper limit for all protocols
        print(f"WARNING: QBER ({qber:.4f}) is too high for secure key generation!")
    
    return final_key_length, {
        'after_parameter_estimation': int(key_after_dr),
        'after_error_correction': int(key_after_ec),
        'after_privacy_amplification': int(key_after_pa),
        'dr': dr,
        'ec_fraction': ec_fraction,
        'privacy_amplification_ratio': privacy_amplification_ratio
    }

def run_point_to_point_simulation(num_pulses_per_link=10000, distance_km=20, mu=0.2,
                                  detector_efficiency=0.9, dark_count_rate_per_ns=1e-7,
                                  pulse_repetition_rate_ns=1):
    """
    Runs a single point-to-point DPS-QKD simulation and prints key metrics, including theory-relevant postprocessing.
    QBER should be in the range 3-10% for practical QKD. Prints a warning if outside this range.
    """
    print("\n--- Running Point-to-Point QKD Simulation ---")
    
    # Create a temporary network with two nodes for the point-to-point simulation
    temp_network = Network()
    node_alice = temp_network.add_node('Alice', avg_photon_number=mu)
    node_bob = temp_network.add_node('Bob', detector_efficiency=detector_efficiency,
                                        dark_count_rate=dark_count_rate_per_ns)
    temp_network.connect_nodes('Alice', 'Bob', distance_km=distance_km)
    
    print(f"Simulating point-to-point QKD for {distance_km} km with {num_pulses_per_link} pulses.")
    
    # Generate the raw sifted key for this link
    alice_raw_sifted_key, bob_raw_sifted_key = node_alice.generate_and_share_key(
        node_bob, num_pulses_per_link, pulse_repetition_rate_ns
    )
    
    # Calculate QBER for this link
    qber, num_errors = calculate_qber(alice_raw_sifted_key, bob_raw_sifted_key)
    if not (0.03 <= qber <= 0.10):
        print(f"WARNING: QBER ({qber:.4f}) is outside the practical range (3-10%) for QKD!")
    else:
        print(f"QBER ({qber:.4f}) is within the practical range (3-10%) for QKD.")
    # --- Theory-relevant postprocessing ---
    final_key_len, postproc = postprocessing(len(alice_raw_sifted_key), qber)
    print(f"\n--- Postprocessing (Theory-Relevant) ---")
    print(f"Key after parameter estimation (DR): {postproc['after_parameter_estimation']}")
    print(f"Key after error correction: {postproc['after_error_correction']}")
    print(f"Key after privacy amplification: {postproc['after_privacy_amplification']}")
    print(f"Final key length: {final_key_len}")
    print(f"(DR={postproc['dr']}, EC fraction={postproc['ec_fraction']:.4f}, PA ratio={postproc['privacy_amplification_ratio']})")
    
    # Calculate Raw Sifted Key Rate (bits/pulse)
    if num_pulses_per_link > 0:
        raw_key_rate_per_pulse = len(alice_raw_sifted_key) / num_pulses_per_link
        print(f"Raw Sifted Key Rate (bits/pulse): {raw_key_rate_per_pulse:.4f}")
    
    # Calculate Raw Sifted Key Rate (bits/second)
    total_time_s = (num_pulses_per_link * pulse_repetition_rate_ns) / 1e9 # Convert ns to seconds
    if total_time_s > 0:
        raw_key_rate_bps = len(alice_raw_sifted_key) / total_time_s
        print(f"Raw Sifted Key Rate (bits/second): {raw_key_rate_bps:.2f} bps")
    else:
        print("Raw Sifted Key Rate (bits/second): N/A (too few pulses)")
        
    # --- Secure Key Rates ---
    if total_time_s > 0:
        secure_key_rate_bps = final_key_len / total_time_s
        print(f"Secure Key Rate (bits/second): {secure_key_rate_bps:.2f} bps")
    else:
        print("Secure Key Rate (bits/second): N/A")
  
    return final_key_len, qber

def run_multi_node_trusted_relay_simulation(num_pulses_per_link=10000, link_distance_km=10, num_relays=1,
                                            mu=0.2, detector_efficiency=0.9, dark_count_rate_per_ns=1e-7,
                                            pulse_repetition_rate_ns=1):
    """
    Runs a multi-node trusted relay QKD simulation and prints key metrics.
    """
    print(f"\n--- Running Multi-Node (Trusted Relay) QKD Simulation with {num_relays} relay(s) ---")
    
    network = Network()
    
    # Define nodes: Alice, Relay1, ..., RelayN, Bob
    sender_id = 'Alice'
    receiver_id = 'Bob'
    relay_ids = [f'Relay{i+1}' for i in range(num_relays)]
    all_node_ids = [sender_id] + relay_ids + [receiver_id]

    # Add all nodes to the network
    for node_id in all_node_ids:
        network.add_node(node_id, avg_photon_number=mu,
                         detector_efficiency=detector_efficiency, dark_count_rate=dark_count_rate_per_ns)
        
    # Connect nodes sequentially in a chain (Alice - Relay1 - ... - RelayN - Bob)
    for i in range(len(all_node_ids) - 1):
        node1_id = all_node_ids[i]
        node2_id = all_node_ids[i+1]
        network.connect_nodes(node1_id, node2_id, distance_km=link_distance_km)

    # Define the path for end-to-end key establishment
    path = all_node_ids
    
    # Establish the end-to-end raw sifted key via trusted relays
    final_end_to_end_raw_key = network.establish_end_to_end_raw_key(
        sender_id, receiver_id, path, num_pulses_per_link, pulse_repetition_rate_ns
    )

    print(f"\n--- Multi-Node Results ({num_relays} relays, {link_distance_km}km per link) ---")
    if final_end_to_end_raw_key is not None:
        print(f"End-to-End Raw Sifted Key Length: {len(final_end_to_end_raw_key)}")
        
        # Calculate total distance and total pulses
        num_links = len(all_node_ids) - 1
        total_distance_km = num_links * link_distance_km
        total_pulses_generated_across_all_links = num_pulses_per_link * num_links # Sum of pulses for each link
        
        print(f"Total Network Distance: {total_distance_km} km")
        print(f"Total Pulses Generated (sum across links): {total_pulses_generated_across_all_links}")
        
        # Total time is the sum of times to generate key on each link (assuming sequential generation)
        total_time_s = (total_pulses_generated_across_all_links * pulse_repetition_rate_ns) / 1e9
        
        if total_time_s > 0:
            end_to_end_raw_key_rate_bps = len(final_end_to_end_raw_key) / total_time_s
            print(f"End-to-End Raw Sifted Key Rate (bits/second): {end_to_end_raw_key_rate_bps:.2f} bps")
        else:
            print("End-to-End Raw Sifted Key Rate (bits/second): N/A (too few pulses)")
    else:
        print("End-to-End raw sifted key establishment failed.")
        
    return final_end_to_end_raw_key

def run_point_to_point_cow_simulation(num_pulses_per_link=10000, distance_km=20, mu=0.1,
                                      detector_efficiency=0.9, dark_count_rate_per_ns=1e-7,
                                      pulse_repetition_rate_ns=1, cow_monitor_pulse_ratio=0.1,
                                      cow_detection_threshold_photons=0, cow_extinction_ratio_db=20.0,
                                      bit_flip_error_prob=0.05):
    """
    Runs a single point-to-point COW-QKD simulation and prints key metrics, including theory-relevant postprocessing.
    QBER should be in the range 3-10% for practical QKD. Prints a warning if outside this range.
    """
    print("\n--- Running Point-to-Point COW QKD Simulation ---")
    
    temp_network = Network()
    # Pass COW specific parameters when adding nodes for COW simulation
    node_alice = temp_network.add_node('Alice', avg_photon_number=mu, 
                                       cow_monitor_pulse_ratio=cow_monitor_pulse_ratio,
                                       cow_detection_threshold_photons=cow_detection_threshold_photons,
                                       cow_extinction_ratio_db=cow_extinction_ratio_db)
    node_bob = temp_network.add_node('Bob', detector_efficiency=detector_efficiency,
                                      dark_count_rate=dark_count_rate_per_ns,
                                      cow_monitor_pulse_ratio=cow_monitor_pulse_ratio, # Bob also needs these for receiver init
                                      cow_detection_threshold_photons=cow_detection_threshold_photons)
    temp_network.connect_nodes('Alice', 'Bob', distance_km=distance_km)
    
    print(f"Simulating COW QKD for {distance_km} km with {num_pulses_per_link} pulses.")
    
    alice_sifted_key_cow, bob_sifted_key_cow = node_alice.generate_and_share_key_cow(
        node_bob, num_pulses_per_link, pulse_repetition_rate_ns,
        monitor_pulse_ratio=cow_monitor_pulse_ratio,
        detection_threshold_photons=cow_detection_threshold_photons,
        bit_flip_error_prob=bit_flip_error_prob
    )
    
    qber_cow, num_errors_cow = calculate_qber(alice_sifted_key_cow, bob_sifted_key_cow)
    if not (0.03 <= qber_cow <= 0.10):
        print(f"WARNING: QBER ({qber_cow:.4f}) is outside the practical range (3-10%) for QKD!")
    else:
        print(f"QBER ({qber_cow:.4f}) is within the practical range (3-10%) for QKD.")
    # --- Theory-relevant postprocessing ---
    final_key_len, postproc = postprocessing(len(alice_sifted_key_cow), qber_cow)
    print(f"\n--- Postprocessing (Theory-Relevant) ---")
    print(f"Key after parameter estimation (DR): {postproc['after_parameter_estimation']}")
    print(f"Key after error correction: {postproc['after_error_correction']}")
    print(f"Key after privacy amplification: {postproc['after_privacy_amplification']}")
    print(f"Final key length: {final_key_len}")
    print(f"(DR={postproc['dr']}, EC fraction={postproc['ec_fraction']:.4f}, PA ratio={postproc['privacy_amplification_ratio']})")
    
    if num_pulses_per_link > 0:
        # Effective number of data pulses (approximate, depends on random assignment)
        num_data_pulses_approx = num_pulses_per_link * (1 - cow_monitor_pulse_ratio)
        if num_data_pulses_approx > 0:
            raw_key_rate_per_data_pulse = len(alice_sifted_key_cow) / num_data_pulses_approx
            print(f"COW Sifted Key Rate (bits/data pulse, approx): {raw_key_rate_per_data_pulse:.4f}")
    
    total_time_s = (num_pulses_per_link * pulse_repetition_rate_ns) / 1e9
    if total_time_s > 0:
        raw_key_rate_bps = len(alice_sifted_key_cow) / total_time_s
        print(f"COW Sifted Key Rate (bits/second, total pulses): {raw_key_rate_bps:.2f} bps")
    else:
        print("COW Sifted Key Rate (bits/second): N/A (too few pulses)")
        
    # --- Secure Key Rates ---
    if total_time_s > 0:
        secure_key_rate_bps = final_key_len / total_time_s
        print(f"Secure Key Rate (bits/second): {secure_key_rate_bps:.2f} bps")
    else:
        print("Secure Key Rate (bits/second): N/A")

    if num_pulses_per_link > 0:
        secure_key_rate_per_pulse = final_key_len / num_pulses_per_link
        print(f"Secure Key Rate (bits/pulse): {secure_key_rate_per_pulse:.4f}")
    else:
        print("Secure Key Rate (bits/pulse): N/A")

    # TODO: Could add multi-node COW simulation example later
    return final_key_len, qber_cow

def run_network_simulation_from_config(config_path):
    # Implementation of run_network_simulation_from_config function
    pass

if __name__ == "__main__":
    # Common simulation parameters
    common_params = {
        'num_pulses_per_link': 5000, # Number of pulses per QKD session (per link)
        'mu': 0.2,           # Average photon number per pulse (WCP)
        'detector_efficiency': 0.9,
        'dark_count_rate_per_ns': 1e-3, # Further increased dark count rate
        'pulse_repetition_rate_ns': 1    # 1 nanosecond per pulse = 1 GHz repetition rate
    }

    # Example 1: Point-to-Point Simulation
    print("\n" + "="*70)
    print("        RUNNING POINT-TO-POINT QKD SIMULATION")
    print("="*70)
    final_key_len_ptp, qber_ptp = run_point_to_point_simulation(
        distance_km=20, # Alice sends directly to Bob over 20km
        **common_params
    )

    # Example 2: Multi-Node Trusted Relay Simulation with 1 Relay
    print("\n" + "="*70)
    print("        RUNNING MULTI-NODE (1 RELAY) QKD SIMULATION")
    print("="*70)
    final_key_multi_node_1_relay = run_multi_node_trusted_relay_simulation(
        link_distance_km=20, # Each link (Alice-Relay, Relay-Bob) is 20km
        num_relays=1,        # Alice - Relay1 - Bob (Total 40km)
        **common_params
    )

    # Example 3: Multi-Node Trusted Relay Simulation with 2 Relays
    print("\n" + "="*70)
    print("        RUNNING MULTI-NODE (2 RELAYS) QKD SIMULATION")
    print("="*70)
    final_key_multi_node_2_relays = run_multi_node_trusted_relay_simulation(
        link_distance_km=20, # Each link is 20km
        num_relays=2,        # Alice - Relay1 - Relay2 - Bob (Total 60km)
        **common_params
    )
    
    # Example 4: Point-to-Point COW QKD Simulation
    print("\n" + "="*70)
    print("        RUNNING POINT-TO-POINT COW QKD SIMULATION")
    print("="*70)
    cow_params = {
        'num_pulses_per_link': 5000,
        'mu': 0.2,  # COW often uses lower mu for data bits to reduce multi-photon pulses
        'detector_efficiency': 0.9,
        'dark_count_rate_per_ns': 1e-10,
        'pulse_repetition_rate_ns': 1,
        'cow_monitor_pulse_ratio': 0.2, # 20% of pulses for monitoring
        'cow_detection_threshold_photons': 0, # Simplistic: any click is a potential '1' if detector is good
        'cow_extinction_ratio_db': 20.0, # Typical value for an intensity modulator
        # bit_flip_error_prob is omitted so it uses the default of 0.05
    }
    final_key_len_cow_ptp, qber_cow_ptp = run_point_to_point_cow_simulation(
        distance_km=20,
        **cow_params
    )

    print("\n" + "="*70)
    print("SIMULATIONS COMPLETE!")
    print("="*70)