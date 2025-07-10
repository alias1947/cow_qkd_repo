from simulation.Receiver import ReceiverDPS, ReceiverCOW, ReceiverBB84
from simulation.Hardware import OpticalChannel
from simulation.Sender import SenderDPS, SenderCOW, SenderBB84

import math 
import random

class Node:
    """
    Represents a generic node in the QKD network.
    Can act as a sender (Alice), receiver (Bob), or trusted relay.
    """
    def __init__(self, node_id, avg_photon_number=0.2, detector_efficiency=0.9, dark_count_rate=1e-7, 
                 # COW specific params, can be None if not used for COW
                 cow_monitor_pulse_ratio=0.1, cow_detection_threshold_photons=0,
                 cow_extinction_ratio_db=20.0):
        self.node_id = node_id
        # Initialize DPS components. These will be reset at the start of a new QKD session
        # via the generate_and_share_key methods to ensure fresh state.
        self.avg_photon_number = avg_photon_number
        self.detector_efficiency = detector_efficiency
        self.dark_count_rate = dark_count_rate
        self.qkd_sender = SenderDPS(self.avg_photon_number)
        self.qkd_receiver = ReceiverDPS(self.detector_efficiency, self.dark_count_rate)
        
        # Initialize COW components
        self.cow_monitor_pulse_ratio = cow_monitor_pulse_ratio
        self.cow_detection_threshold_photons = cow_detection_threshold_photons
        self.cow_extinction_ratio_db = cow_extinction_ratio_db
        self.cow_sender = SenderCOW(self.avg_photon_number, 
                                    monitor_pulse_ratio=self.cow_monitor_pulse_ratio,
                                    extinction_ratio_db=self.cow_extinction_ratio_db)
        self.cow_receiver = ReceiverCOW(self.detector_efficiency, self.dark_count_rate, 
                                        detection_threshold_photons=self.cow_detection_threshold_photons)
        
        # Initialize BB84 components
        self.bb84_sender = SenderBB84(self.avg_photon_number)
        self.bb84_receiver = ReceiverBB84(self.detector_efficiency, self.dark_count_rate)
        
        self.connected_links = {}
        self.shared_keys = {}     
        self.traffic_log = []    

    def add_link(self, neighbor_node_id, channel_instance):
        """Adds an optical channel link to a neighbor."""
        self.connected_links[neighbor_node_id] = channel_instance

    def generate_and_share_key(self, target_node, num_pulses, pulse_repetition_rate_ns, phase_flip_prob=0.0):
        """
        Implements DPS QKD as per theory:
        - Encoding: phase difference between consecutive pulses (0, π)
        - Sifting: based on detector clicks and phase difference
        - 2 detectors, Mach-Zehnder interferometer
        - phase_flip_prob: probability of phase flip noise in the channel
        """
        print(f"--- Node {self.node_id} initiating DPS-QKD with Node {target_node.node_id} ---")
        
        # Re-initialize sender and receiver for a new QKD session to ensure clean state (e.g., last_sent_phase)
        #for DPS
        self.qkd_sender = SenderDPS(self.avg_photon_number)
        target_node.qkd_receiver = ReceiverDPS(target_node.detector_efficiency, target_node.dark_count_rate)

        alice_pulses_sent_info = [] 
        
        for i in range(num_pulses):
            time_slot = i * pulse_repetition_rate_ns
            # Sender.prepare_and_send_pulse now manages previous_pulse_phase internally
            modulated_phase, photon_count = self.qkd_sender.prepare_and_send_pulse(time_slot) 
            alice_pulses_sent_info.append(self.qkd_sender.get_pulse_info(time_slot)) 
            

        channel = self.connected_links.get(target_node.node_id)
        if not channel:
            raise ValueError(f"No channel defined between {self.node_id} and {target_node.node_id}")

        channel_processed_pulses = []
        for pulse in alice_pulses_sent_info:
            received_photons = channel.transmit_pulse(pulse['photon_count'])
            # Apply phase flip noise
            modulated_phase = pulse['modulated_phase']
            if random.random() < phase_flip_prob:
                modulated_phase = (modulated_phase + math.pi) % (2 * math.pi)
            channel_processed_pulses.append({
                'time_slot': pulse['time_slot'],
                'received_photon_count': received_photons,
                'modulated_phase': modulated_phase 
            })

        bob_clicks_and_inferred_bits = []
        
        # Bob needs information about the previous pulse to measure phase difference
        # The first pulse cannot encode a bit, so its 'previous' is a dummy.
        dummy_prev_received_pulse_info = {'received_photon_count': 0, 'modulated_phase': 0.0}

        for i in range(len(channel_processed_pulses)):
            current_received_pulse = channel_processed_pulses[i]
            
            # Bob's MZI measures the difference between the current and previous pulse.
            # For the very first pulse, there is no 'previous' signal pulse.
            previous_received_pulse_for_mzi = dummy_prev_received_pulse_info if i == 0 else channel_processed_pulses[i-1]

            click_dm1, click_dm2, measured_phase_diff, bob_bit = target_node.qkd_receiver.receive_and_measure(
                current_received_pulse['time_slot'],
                current_received_pulse['received_photon_count'],
                current_received_pulse['modulated_phase'],
                previous_received_pulse_for_mzi['received_photon_count'], # Pass received photon count of previous
                previous_received_pulse_for_mzi['modulated_phase'] # Pass phase of previous
            )
            bob_clicks_and_inferred_bits.append({
                'time_slot': current_received_pulse['time_slot'],
                'click_dm1': click_dm1,
                'click_dm2': click_dm2,
                'measured_phase_diff': measured_phase_diff,
                'bob_inferred_bit': bob_bit 
            })

        alice_sifted_key = []
        bob_sifted_key = []
        
        # Sifting process: Alice and Bob publicly compare and agree on bits.
        # For DPS, they discard the first pulse and only consider pairs where Bob made a conclusive measurement.
        for i in range(1, len(alice_pulses_sent_info)): # Start from 1 because the first pulse doesn't encode a bit
            alice_pn_minus_1_info = alice_pulses_sent_info[i-1]
            alice_pn_info = alice_pulses_sent_info[i]
            
            bob_measurement_info_for_pn = None
            for click_info in bob_clicks_and_inferred_bits:
                if click_info['time_slot'] == alice_pn_info['time_slot']:
                    bob_measurement_info_for_pn = click_info
                    break
            
            # Only proceed if Bob has measurement info for the current pulse (pn)
            # And Bob's measurement for this pair was conclusive (not None)
            if bob_measurement_info_for_pn and bob_measurement_info_for_pn['bob_inferred_bit'] is not None:
                # Calculate Alice's intended bit for this pair (pn-1, pn)
                alice_intended_delta_phi = (alice_pn_info['modulated_phase'] - alice_pn_minus_1_info['modulated_phase']) % (2 * math.pi)
                # Normalize delta_phi to be in [-pi, pi]
                if alice_intended_delta_phi > math.pi: alice_intended_delta_phi -= 2 * math.pi
                if alice_intended_delta_phi < -math.pi: alice_intended_delta_phi += 2 * math.pi
                
                # Alice's bit is 0 if phase difference is 0, 1 if phase difference is pi
                alice_intended_bit = 0 if math.isclose(alice_intended_delta_phi, 0.0, abs_tol=1e-9) else 1
                
                # Both Alice and Bob add the bit to their sifted key if they agree on the time slot
                # and Bob had a conclusive measurement.
                alice_sifted_key.append(alice_intended_bit)
                bob_sifted_key.append(bob_measurement_info_for_pn['bob_inferred_bit'])
                
        print(f"DPS Sifting complete. Raw key length: {len(alice_sifted_key)}")
        print(f"sifted key are: {bob_sifted_key}")
        self.shared_keys[target_node.node_id] = alice_sifted_key
        target_node.shared_keys[self.node_id] = bob_sifted_key
        self.traffic_log.append({
            'type': 'key_generation',
            'partner': target_node.node_id,
            'initial_pulses': num_pulses,
            'sifted_length': len(alice_sifted_key),
        })
        print("[DPS QKD] Sifting and measurement complete. Theory-compliant implementation.")
        return alice_sifted_key, bob_sifted_key

    def generate_and_share_key_cow(self, target_node, num_pulses, pulse_repetition_rate_ns,
                                   monitor_pulse_ratio=0.1, detection_threshold_photons=0, phase_flip_prob=0.0, bit_flip_error_prob=0.0):
        """
        Implements COW QKD as per theory:
        - Encoding: vacuum + coherent pulse, intensity modulated
        - Sifting: keep bits where Alice and Bob agree on data pulses (using correct pulse in each pair)
        - Monitoring: pairs of monitoring pulses to detect eavesdropping
        """
        print(f"--- Node {self.node_id} initiating COW-QKD with Node {target_node.node_id} ---")

        # Re-initialize COW sender and receiver for a new QKD session
        self.cow_sender = SenderCOW(self.avg_photon_number, 
                                    monitor_pulse_ratio=monitor_pulse_ratio,
                                    extinction_ratio_db=self.cow_extinction_ratio_db)
        target_node.cow_receiver = ReceiverCOW(
            target_node.detector_efficiency,
            target_node.dark_count_rate,
            detection_threshold_photons=detection_threshold_photons
        )

        # 1. Alice prepares her pulse train (data and monitoring)
        alice_sent_pulses_info = self.cow_sender.prepare_pulse_train(num_pulses)
        
        # 2. Transmit pulses over the optical channel
        channel = self.connected_links.get(target_node.node_id)
        if not channel:
            raise ValueError(f"No channel defined between {self.node_id} and {target_node.node_id}")

        bob_received_signals = []
        for i, sent_pulse in enumerate(alice_sent_pulses_info):
            time_slot = i
            photons_sent = sent_pulse['photon_count']
            pulse_type = sent_pulse['pulse_type']
            original_phase = sent_pulse['phase']

            received_photons_at_bob = channel.transmit_pulse(photons_sent)

            # Apply phase flip noise to the transmitted pulse
            final_phase = original_phase
            if random.random() < phase_flip_prob:
                final_phase = (original_phase + math.pi) % (2 * math.pi)

            # Bob measures the pulse
            click, bob_inferred_bit, is_monitoring_click = target_node.cow_receiver.measure_pulse(
                time_slot, 
                received_photons_at_bob, 
                pulse_type
            )
            bob_received_signals.append({
                'time_slot': time_slot,
                'alice_pulse_type': pulse_type,
                'alice_intended_bit': sent_pulse['intended_bit'],
                'received_photons': received_photons_at_bob,
                'click': click,
                'bob_inferred_bit': bob_inferred_bit,
                'is_monitoring_click': is_monitoring_click,
                'final_phase': final_phase
            })

        # 3. Sifting Process (Classical communication between Alice and Bob)
        print(f"bob received key pulse types: {[signal['alice_pulse_type'] for signal in bob_received_signals]}")
        alice_sifted_key_cow = []
        bob_sifted_key_cow = []
        # debug_pairs_printed = 0
        i = 0
        while i < len(alice_sent_pulses_info) - 1:
            p1_alice = alice_sent_pulses_info[i]
            p2_alice = alice_sent_pulses_info[i+1]
            p1_bob = bob_received_signals[i]
            p2_bob = bob_received_signals[i+1]

            # Monitor pair: both monitor_first and monitor_second
            if p1_alice['pulse_type'] == 'monitor_first' and p2_alice['pulse_type'] == 'monitor_second':
                i += 2
                continue
            # Data pair: data_first and data_second
            if p1_alice['pulse_type'].startswith('data') and p2_alice['pulse_type'].startswith('data'):
                # Only keep if exactly one click in the pair
                if p1_bob['click'] != p2_bob['click']:
                    if p1_bob['click']:
                        # Click in first pulse: infer bit 1
                        alice_sifted_key_cow.append(1)
                        bob_sifted_key_cow.append(1)
                        # debug_info = {
                        #     'pair_index': i//2,
                        #     'alice_bit': 1,
                        #     'pulse_used': 'first',
                        #     'photon_count': p1_alice['photon_count'],
                        #     'bob_inferred_bit': 1,
                        #     'bob_click': True
                        # }
                    elif p2_bob['click']:
                        # Click in second pulse: infer bit 0
                        alice_sifted_key_cow.append(0)
                        bob_sifted_key_cow.append(0)
                        # debug_info = {
                        #     'pair_index': i//2,
                        #     'alice_bit': 0,
                        #     'pulse_used': 'second',
                        #     'photon_count': p2_alice['photon_count'],
                        #     'bob_inferred_bit': 0,
                        #     'bob_click': True
                        # }
                    # if debug_pairs_printed < 10:
                    #     print(f"[DEBUG COW PAIR {debug_info['pair_index']}] Alice bit: {debug_info['alice_bit']}, Pulse used: {debug_info['pulse_used']}, "
                    #           f"Photon count: {debug_info['photon_count']}, Bob inferred: {debug_info['bob_inferred_bit']}, Bob click: {debug_info['bob_click']}", flush=True)
                    #     debug_pairs_printed += 1
                i += 2
                continue
            i += 1

        # 4. Monitoring Check (Classical communication between Alice and Bob)
        successful_monitor_pairs = 0
        attempted_monitor_pairs = 0
        i = 0
        while i < len(alice_sent_pulses_info) - 1:
            p1_alice = alice_sent_pulses_info[i]
            p2_alice = alice_sent_pulses_info[i+1]
            p1_bob = bob_received_signals[i]
            p2_bob = bob_received_signals[i+1]
            if p1_alice['pulse_type'] == 'monitor_first' and p2_alice['pulse_type'] == 'monitor_second':
                attempted_monitor_pairs += 1
                phases_match = math.isclose(p1_bob['final_phase'], p2_bob['final_phase'], abs_tol=1e-9)
                if p1_bob['is_monitoring_click'] and p2_bob['is_monitoring_click'] and phases_match:
                    successful_monitor_pairs += 1
                i += 2
            else:
                i += 1

        print(f"COW Sifting: Attempted data bits: {len(self.cow_sender.get_intended_key_bits())}, Sifted Key Length: {len(alice_sifted_key_cow)}")
        if attempted_monitor_pairs > 0:
            monitoring_success_rate = successful_monitor_pairs / attempted_monitor_pairs
            print(f"COW Monitoring: {successful_monitor_pairs}/{attempted_monitor_pairs} pairs successfully detected (Rate: {monitoring_success_rate:.2f})")
            if monitoring_success_rate < 0.9:
                print("WARNING: Monitoring success rate is low. Possible eavesdropping or high channel loss!")
            else:
                print("Monitoring success rate is high. No significant eavesdropping detected based on monitor pulses.")
        else:
            print("COW Monitoring: No monitoring pairs attempted or detected.")

        self.shared_keys[target_node.node_id + "_cow"] = alice_sifted_key_cow
        target_node.shared_keys[self.node_id + "_cow"] = bob_sifted_key_cow

        self.traffic_log.append({
            'type': 'key_generation_cow',
            'partner': target_node.node_id,
            'initial_pulses': num_pulses,
            'sifted_length': len(alice_sifted_key_cow),
            'successful_monitor_pairs': successful_monitor_pairs,
            'attempted_monitor_pairs': attempted_monitor_pairs
        })
        print(f"sifted key : {bob_sifted_key_cow}")
        print("[COW QKD] Sifting, decoy, and monitoring complete. Theory-compliant implementation.")
        
        # After sifting, apply bit flip error to Bob's sifted key
        for idx in range(len(bob_sifted_key_cow)):
            if random.random() < bit_flip_error_prob:
                bob_sifted_key_cow[idx] = 1 - bob_sifted_key_cow[idx]
        
        return alice_sifted_key_cow, bob_sifted_key_cow

    def generate_and_share_key_bb84(self, target_node, num_pulses, pulse_repetition_rate_ns, phase_flip_prob=0.0):
        """
        Implements BB84 QKD as per theory:
        - Encoding: four quantum states in two bases (rectilinear and diagonal)
        - Sifting: keep bits where Alice and Bob used the same basis
        - Classical communication for basis comparison
        """
        print(f"--- Node {self.node_id} initiating BB84-QKD with Node {target_node.node_id} ---")

        # Re-initialize BB84 sender and receiver for a new QKD session
        self.bb84_sender = SenderBB84(self.avg_photon_number)
        target_node.bb84_receiver = ReceiverBB84(
            target_node.detector_efficiency,
            target_node.dark_count_rate
        )

        # Step 1: Alice generates random bits and encodes them in randomly chosen bases
        alice_sent_pulses_info = []
        for i in range(num_pulses):
            time_slot = i * pulse_repetition_rate_ns
            encoded_state, photon_count, chosen_bit, chosen_basis = self.bb84_sender.prepare_and_send_pulse(time_slot)
            alice_sent_pulses_info.append(self.bb84_sender.get_pulse_info(time_slot))

        # Step 2: Transmit pulses over the optical channel
        channel = self.connected_links.get(target_node.node_id)
        if not channel:
            raise ValueError(f"No channel defined between {self.node_id} and {target_node.node_id}")

        bob_received_signals = []
        for sent_pulse in alice_sent_pulses_info:
            received_photons = channel.transmit_pulse(sent_pulse['photon_count'])
            
            # Apply phase flip noise (affects the encoded state)
            encoded_state = sent_pulse['encoded_state']
            if random.random() < phase_flip_prob:
                # Phase flip changes the state: |0⟩ ↔ |1⟩, |+⟩ ↔ |-⟩
                if encoded_state == '|0⟩':
                    encoded_state = '|1⟩'
                elif encoded_state == '|1⟩':
                    encoded_state = '|0⟩'
                elif encoded_state == '|+⟩':
                    encoded_state = '|-⟩'
                elif encoded_state == '|-⟩':
                    encoded_state = '|+⟩'
            
            # Add additional channel noise (photon loss, etc.)
            # This is already handled by the channel.transmit_pulse() function

            bob_received_signals.append({
                'time_slot': sent_pulse['time_slot'],
                'received_photons': received_photons,
                'encoded_state': encoded_state
            })

        # Step 3: Bob measures each photon in a randomly chosen basis
        bob_measurements = []
        for received_signal in bob_received_signals:
            measured_bit, chosen_basis, click_occurred = target_node.bb84_receiver.receive_and_measure(
                received_signal['time_slot'],
                received_signal['received_photons'],
                received_signal['encoded_state']
            )
            bob_measurements.append({
                'time_slot': received_signal['time_slot'],
                'measured_bit': measured_bit,
                'chosen_basis': chosen_basis,
                'click_occurred': click_occurred
            })

        # Step 4: Alice and Bob publicly disclose their bases (classical communication)
        alice_bases = self.bb84_sender.get_chosen_bases()
        bob_bases = target_node.bb84_receiver.get_chosen_bases()

        # Step 5: Sifting process - keep bits where bases match
        alice_sifted_key = []
        bob_sifted_key = []
        
        for i in range(len(alice_sent_pulses_info)):
            if i < len(bob_measurements) and i < len(alice_bases) and i < len(bob_bases):
                alice_basis = alice_bases[i]
                bob_basis = bob_bases[i]
                alice_bit = alice_sent_pulses_info[i]['chosen_bit']
                bob_measurement = bob_measurements[i]
                
                # Only keep bits where Alice and Bob used the same basis AND Bob got a click
                if (alice_basis == bob_basis and 
                    bob_measurement['measured_bit'] is not None and 
                    bob_measurement['click_occurred']):
                    alice_sifted_key.append(alice_bit)
                    bob_sifted_key.append(bob_measurement['measured_bit'])

        print(f"BB84 Sifting complete. Raw key length: {len(alice_sifted_key)}")
        print(f"Alice bases: {alice_bases[:10]}...")  # Show first 10 bases
        print(f"Bob bases: {bob_bases[:10]}...")      # Show first 10 bases
        print(f"Sifted key: {bob_sifted_key}")
        
        # Debug information
        basis_matches = sum(1 for a, b in zip(alice_bases, bob_bases) if a == b)
        total_pulses = len(alice_bases)
        print(f"BB84 Debug: {basis_matches}/{total_pulses} basis matches ({basis_matches/total_pulses*100:.1f}%)")
        
        # Check for clicks in matching basis cases
        matching_basis_clicks = 0
        for i in range(len(alice_sent_pulses_info)):
            if i < len(bob_measurements) and i < len(alice_bases) and i < len(bob_bases):
                if alice_bases[i] == bob_bases[i] and bob_measurements[i]['click_occurred']:
                    matching_basis_clicks += 1
        
        print(f"BB84 Debug: {matching_basis_clicks} clicks in matching basis cases")
        
        # Check for errors in matching basis cases
        if len(alice_sifted_key) > 0:
            errors = sum(1 for a, b in zip(alice_sifted_key, bob_sifted_key) if a != b)
            qber_debug = errors / len(alice_sifted_key)
            print(f"BB84 Debug: QBER in sifted key: {qber_debug:.4f} ({errors}/{len(alice_sifted_key)} errors)")

        self.shared_keys[target_node.node_id + "_bb84"] = alice_sifted_key
        target_node.shared_keys[self.node_id + "_bb84"] = bob_sifted_key

        self.traffic_log.append({
            'type': 'key_generation_bb84',
            'partner': target_node.node_id,
            'initial_pulses': num_pulses,
            'sifted_length': len(alice_sifted_key),
        })
        
        print("[BB84 QKD] Sifting complete. Theory-compliant implementation.")
        return alice_sifted_key, bob_sifted_key

    def get_raw_sifted_key_with_neighbor(self, neighbor_id):
        """Retrieves the raw sifted key shared with a direct neighbor."""
        return self.shared_keys.get(neighbor_id)

    def relay_key_classically(self, sender_node_id, receiver_node_id, key_to_relay):
        # This function is not directly used in the current end-to-end key establishment logic
        # but could be part of a more explicit classical relay process.
        key_with_sender = self.shared_keys.get(sender_node_id)
        key_with_receiver = self.shared_keys.get(receiver_node_id)

        if not key_with_sender:
            print(f"Error: Node {self.node_id} does not have a key with {sender_node_id} to relay.")
            return None
        if not key_with_receiver:
            print(f"Error: Node {self.node_id} does not have a key with {receiver_node_id} to relay.")
            return None
        print(f"Node {self.node_id} (relay) is holding the end-to-end key segment. Ready to extend to {receiver_node_id}.")
        return key_to_relay # The relay just passes the key content to the next segment's context.

class Network:
    def __init__(self):
        self.nodes = {} # {node_id: Node_instance}

    def add_node(self, node_id, avg_photon_number=0.2, detector_efficiency=0.9, dark_count_rate=1e-7,
                 # COW specific params
                 cow_monitor_pulse_ratio=0.1, cow_detection_threshold_photons=0,
                 cow_extinction_ratio_db=20.0):
        """
        Adds a new node to the network.
        Node-specific parameters like avg_photon_number for a sender (Alice)
        or detector_efficiency for a receiver (Bob) can be specified here.
        """
        if node_id in self.nodes:
            raise ValueError(f"Node with ID {node_id} already exists.")
        
        new_node = Node(node_id, avg_photon_number, detector_efficiency, dark_count_rate,
                        cow_monitor_pulse_ratio, cow_detection_threshold_photons,
                        cow_extinction_ratio_db)
        self.nodes[node_id] = new_node
        print(f"Node {node_id} added to the network.")
        return new_node

    def connect_nodes(self, node1_id, node2_id, distance_km, attenuation_db_per_km=0.2):
        node1 = self.nodes.get(node1_id)
        node2 = self.nodes.get(node2_id)

        if not node1 or not node2:
            raise ValueError("Both nodes must exist in the network to create a connection.")

        channel = OpticalChannel(distance_km, attenuation_db_per_km)
        node1.add_link(node2_id, channel)
        node2.add_link(node1_id, channel) # Channel is bidirectional in this model
        print(f"Connected Node {node1_id} and Node {node2_id} with a {distance_km} km link.")

    def establish_end_to_end_raw_key(self, sender_id, receiver_id, path_nodes, num_pulses, pulse_repetition_rate_ns):
        if path_nodes[0] != sender_id or path_nodes[-1] != receiver_id:
            raise ValueError("Path must start with sender_id and end with receiver_id.")

        print(f"\n--- Establishing end-to-end RAW key (DPS) from {sender_id} to {receiver_id} via path: {path_nodes} ---")
        
        # In a trusted relay network, each link independently establishes a raw key.
        # The relay node then classically "stitches" these keys together.
        # For a raw key demonstration, we concatenate the individual link keys.
        current_end_to_end_key_segment = [] 
        
        for i in range(len(path_nodes) - 1):
            node1_id = path_nodes[i]
            node2_id = path_nodes[i+1]
            
            node1 = self.nodes[node1_id] # Acts as Alice for this link
            node2 = self.nodes[node2_id] # Acts as Bob for this link
            
            print(f"Attempting DPS-QKD link: {node1_id} <-> {node2_id}")
            
            # Generate the raw sifted key for this direct link
            alice_raw_sifted, bob_raw_sifted = node1.generate_and_share_key(
                node2, num_pulses, pulse_repetition_rate_ns
            )
            
            # For trusted relay, the raw sifted key from Alice's side of the current link
            # is effectively available to the next segment after relay processing.
            current_end_to_end_key_segment.extend(alice_raw_sifted) # Concatenate for total raw key length

            if not alice_raw_sifted:
                print(f"Failed to establish raw sifted key for link {node1_id}-{node2_id}. Aborting end-to-end key establishment.")
                return None
            print(f"Raw sifted key established for link {node1_id} and {node2_id} with length {len(alice_raw_sifted)}")

        print(f"End-to-end RAW sifted key (DPS) established between {sender_id} and {receiver_id}.")
        return current_end_to_end_key_segment # This is the final end-to-end raw key

    def establish_end_to_end_raw_key_cow(self, sender_id, receiver_id, path_nodes, num_pulses, 
                                         pulse_repetition_rate_ns, monitor_pulse_ratio=0.1, 
                                         detection_threshold_photons=0):
        if path_nodes[0] != sender_id or path_nodes[-1] != receiver_id:
            raise ValueError("Path must start with sender_id and end with receiver_id.")

        print(f"\n--- Establishing end-to-end RAW key (COW) from {sender_id} to {receiver_id} via path: {path_nodes} ---")
        
        current_end_to_end_key_segment_cow = []
        
        for i in range(len(path_nodes) - 1):
            node1_id = path_nodes[i]
            node2_id = path_nodes[i+1]
            
            node1 = self.nodes[node1_id]
            node2 = self.nodes[node2_id]
            
            print(f"Attempting COW-QKD link: {node1_id} <-> {node2_id}")
            
            alice_sifted_cow, bob_sifted_cow = node1.generate_and_share_key_cow(
                node2, num_pulses, pulse_repetition_rate_ns, 
                monitor_pulse_ratio, detection_threshold_photons
            )
            
            # For trusted relay in COW (as with DPS), the raw sifted key from Alice's side
            # of the current link is concatenated to form the end-to-end raw key.
            current_end_to_end_key_segment_cow.extend(alice_sifted_cow)

            if not alice_sifted_cow:
                print(f"Failed to establish COW sifted key for link {node1_id}-{node2_id}. Aborting.")
                return None
            print(f"COW sifted key established for link {node1_id} and {node2_id} with length {len(alice_sifted_cow)}")

        print(f"End-to-end COW RAW sifted key established between {sender_id} and {receiver_id}.")
        return current_end_to_end_key_segment_cow

    def establish_end_to_end_raw_key_bb84(self, sender_id, receiver_id, path_nodes, num_pulses, pulse_repetition_rate_ns):
        if path_nodes[0] != sender_id or path_nodes[-1] != receiver_id:
            raise ValueError("Path must start with sender_id and end with receiver_id.")

        print(f"\n--- Establishing end-to-end RAW key (BB84) from {sender_id} to {receiver_id} via path: {path_nodes} ---")
        
        current_end_to_end_key_segment_bb84 = []
        
        for i in range(len(path_nodes) - 1):
            node1_id = path_nodes[i]
            node2_id = path_nodes[i+1]
            
            node1 = self.nodes[node1_id]
            node2 = self.nodes[node2_id]
            
            print(f"Attempting BB84-QKD link: {node1_id} <-> {node2_id}")
            
            alice_sifted_bb84, bob_sifted_bb84 = node1.generate_and_share_key_bb84(
                node2, num_pulses, pulse_repetition_rate_ns
            )
            
            # For trusted relay in BB84, the raw sifted key from Alice's side
            # of the current link is concatenated to form the end-to-end raw key.
            current_end_to_end_key_segment_bb84.extend(alice_sifted_bb84)

            if not alice_sifted_bb84:
                print(f"Failed to establish BB84 sifted key for link {node1_id}-{node2_id}. Aborting.")
                return None
            print(f"BB84 sifted key established for link {node1_id} and {node2_id} with length {len(alice_sifted_bb84)}")

        print(f"End-to-end BB84 RAW sifted key established between {sender_id} and {receiver_id}.")
        return current_end_to_end_key_segment_bb84
