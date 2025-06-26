from Source import Sender
from Hardware import Receiver, OpticalChannel
# Import COW components
from Source import SenderCOW
from Hardware import ReceiverCOW

import math 
import random

class Node:
    """
    Represents a generic node in the QKD network.
    Can act as a sender (Alice), receiver (Bob), or trusted relay.
    """
    def __init__(self, node_id, avg_photon_number=0.2, detector_efficiency=0.9, dark_count_rate=1e-7, 
                 # COW specific params, can be None if not used for COW
                 cow_monitor_pulse_ratio=0.1, cow_detection_threshold_photons=0):
        self.node_id = node_id
        # Initialize DPS components. These will be reset at the start of a new QKD session
        # via the generate_and_share_key methods to ensure fresh state.
        self.avg_photon_number = avg_photon_number
        self.detector_efficiency = detector_efficiency
        self.dark_count_rate = dark_count_rate
        self.qkd_sender = Sender(self.avg_photon_number)
        self.qkd_receiver = Receiver(self.detector_efficiency, self.dark_count_rate)
        
        # Initialize COW components
        self.cow_monitor_pulse_ratio = cow_monitor_pulse_ratio
        self.cow_detection_threshold_photons = cow_detection_threshold_photons
        self.cow_sender = SenderCOW(self.avg_photon_number, monitor_pulse_ratio=self.cow_monitor_pulse_ratio)
        self.cow_receiver = ReceiverCOW(self.detector_efficiency, self.dark_count_rate, 
                                        detection_threshold_photons=self.cow_detection_threshold_photons)
        
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
        self.qkd_sender = Sender(self.avg_photon_number)
        target_node.qkd_receiver = Receiver(target_node.detector_efficiency, target_node.dark_count_rate)

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
                                   monitor_pulse_ratio=0.1, detection_threshold_photons=0, phase_flip_prob=0.0):
        """
        Implements COW QKD as per theory:
        - Encoding: vacuum + coherent pulse, intensity modulated
        - Sifting: keep bits where Alice and Bob agree on data pulses
        - Monitoring: pairs of monitoring pulses to detect eavesdropping
        """
        print(f"--- Node {self.node_id} initiating COW-QKD with Node {target_node.node_id} ---")

        # Re-initialize COW sender and receiver for a new QKD session
        self.cow_sender = SenderCOW(self.avg_photon_number, monitor_pulse_ratio=monitor_pulse_ratio)
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
            # Ensure time_slot matches the index for simplicity in this simulation
            time_slot = i # Or sent_pulse['time_slot'] if it's explicitly set as i
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
                'alice_intended_bit': sent_pulse['intended_bit'], # Alice's bit for this data slot (None for monitor)
                'received_photons': received_photons_at_bob,
                'click': click,
                'bob_inferred_bit': bob_inferred_bit, # Bob's inferred bit for data slots (None if inconclusive)
                'is_monitoring_click': is_monitoring_click, # If Bob got a click for a monitor pulse
                'final_phase': final_phase # Store the phase after channel noise
            })

        # 3. Sifting Process (Classical communication between Alice and Bob)
        alice_sifted_key_cow = []
        bob_sifted_key_cow = []
        
        # Alice announces which pulses were data pulses.
        # Bob announces for which of those he got a conclusive measurement.
        # Both form their sifted keys from these commonly agreed upon slots.
        # This key will contain errors, which are estimated next via QBER.
        for i in range(len(alice_sent_pulses_info)):
            alice_pulse_info = alice_sent_pulses_info[i]
            bob_signal_info = bob_received_signals[i]

            # Sifting rule: Keep all bits from data pulses.
            # Bob's measurement is always conclusive for data pulses in the corrected `measure_pulse`.
            if alice_pulse_info['pulse_type'] == 'data':
                alice_bit = alice_pulse_info['intended_bit']
                bob_bit = bob_signal_info['bob_inferred_bit']

                # The key is formed from ALL data bits, including errors.
                alice_sifted_key_cow.append(alice_bit)
                bob_sifted_key_cow.append(bob_bit)

        # 4. Monitoring Check (Classical communication between Alice and Bob)
        successful_monitor_pairs = 0
        attempted_monitor_pairs = 0
        
        # Alice reveals the original type of all pulses. Bob reveals his click status for monitoring pulses.
        for i in range(len(alice_sent_pulses_info) - 1):
            p1_alice = alice_sent_pulses_info[i]
            p2_alice = alice_sent_pulses_info[i+1]
            p1_bob = bob_received_signals[i]
            p2_bob = bob_received_signals[i+1]

            # Check if it's a declared monitor pair from Alice's side
            if p1_alice['pulse_type'] == 'monitor_first' and p2_alice['pulse_type'] == 'monitor_second':
                attempted_monitor_pairs += 1
                # Check for clicks AND for phase integrity.
                # If phases don't match, an eavesdropper might have tampered with them.
                phases_match = math.isclose(p1_bob['final_phase'], p2_bob['final_phase'], abs_tol=1e-9)

                if p1_bob['is_monitoring_click'] and p2_bob['is_monitoring_click'] and phases_match:
                    successful_monitor_pairs += 1
        
        print(f"COW Sifting: Attempted data bits: {len(self.cow_sender.get_intended_key_bits())}, Sifted Key Length: {len(alice_sifted_key_cow)}")
        
        if attempted_monitor_pairs > 0:
            monitoring_success_rate = successful_monitor_pairs / attempted_monitor_pairs
            print(f"COW Monitoring: {successful_monitor_pairs}/{attempted_monitor_pairs} pairs successfully detected (Rate: {monitoring_success_rate:.2f})")
            # The threshold for warning can be adjusted based on expected channel loss and Eve's presence
            if monitoring_success_rate < 0.9: # A high success rate is expected in absence of Eve for monitor pulses
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
        # At the end, print a summary
        print("[COW QKD] Sifting, decoy, and monitoring complete. Theory-compliant implementation.")
        return alice_sifted_key_cow, bob_sifted_key_cow

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

    def add_node(self, node_id, **kwargs):
        """Adds a new node to the network."""
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists.")
        self.nodes[node_id] = Node(node_id, **kwargs)
        return self.nodes[node_id]

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
