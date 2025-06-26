# dps_qkd_source.py

import random
import math

class LightSource:
    
    def __init__(self, average_photon_number=0.2):
        if not (0 < average_photon_number < 1):
            raise ValueError("Average photon number (mu) for WCP should be between 0 and 1.")
        self.mu = average_photon_number 

    def generate_single_pulse_photon_count(self):
        num_photons = 0
        L = math.exp(-self.mu)
        p = 1.0
        k = 0
        while p > L:
            k += 1
            p *= random.random()
        num_photons = k - 1
        return num_photons

    def get_initial_phase(self):
       
        return 0.0 

class PhaseModulator:
    
    def modulate_phase(self, current_phase, desired_phase_shift):
        return (current_phase + desired_phase_shift) % (2 * math.pi)

class Sender:
   
    def __init__(self, avg_photon_number=0.2):
        self.light_source = LightSource(avg_photon_number)
        self.phase_modulator = PhaseModulator()
        self.raw_key_bits = [] 
        self.sent_pulses_info = [] 
        self.last_sent_phase = None # Keep track of the phase of the last pulse sent for DPS encoding

    def prepare_and_send_pulse(self, time_slot): # Removed previous_pulse_phase from here, managed internally
        photon_count = self.light_source.generate_single_pulse_photon_count()

        if self.last_sent_phase is None:
            # For the very first pulse in a session, choose a random initial phase
            # This pulse doesn't encode a bit for DPS.
            modulated_phase_on_this_pulse = random.choice([0.0, math.pi])
            current_secret_bit = None # No bit encoded by the first pulse
        else:
            # Alice chooses her secret bit for this pair (current_pulse, previous_pulse)
            current_secret_bit = random.randint(0, 1) 
            self.raw_key_bits.append(current_secret_bit) # Store Alice's intended bit

            # Alice modulates the current pulse such that its phase difference from the previous pulse encodes the bit
            desired_phase_difference_for_bit = 0.0 if current_secret_bit == 0 else math.pi
            modulated_phase_on_this_pulse = self.phase_modulator.modulate_phase(
                self.last_sent_phase, desired_phase_difference_for_bit
            )
        
        self.last_sent_phase = modulated_phase_on_this_pulse # Update last sent phase for the next pulse

        self.sent_pulses_info.append({
            'time_slot': time_slot,
            'photon_count': photon_count,
            'modulated_phase': modulated_phase_on_this_pulse,
            'alice_intended_bit_for_pair': current_secret_bit # None for the very first pulse
        })
        
        return modulated_phase_on_this_pulse, photon_count

    def get_pulse_info(self, time_slot):
        """Retrieves information about a pulse Alice sent at a given time slot."""
        for pulse_info in self.sent_pulses_info:
            if pulse_info['time_slot'] == time_slot:
                return pulse_info
        return None
    
class SenderCOW:
    def __init__(self, avg_photon_number=0.2, monitor_pulse_ratio=0.1):
        self.light_source = LightSource(avg_photon_number)
        self.phase_modulator = PhaseModulator() # Not typically used for COW data encoding, but kept for consistency
        self.mu = avg_photon_number
        self.raw_key_bits = []  # Alice's chosen bits (for data pulses only)
        self.sent_pulses_info = [] # Info about what was actually sent
        self.data_phase = 0.0 # Fixed phase for COW data pulses ('1') and monitoring pulses
        self.monitor_pulse_ratio = monitor_pulse_ratio # Fraction of pulses used for monitoring pairs

    def prepare_pulse_train(self, num_total_pulses):
        self.raw_key_bits = []
        self.sent_pulses_info = []
        
        pulse_type_sequence = ['data'] * num_total_pulses # Initialize all as data
        num_monitor_pairs = int(num_total_pulses * self.monitor_pulse_ratio / 2)
        
        # Ensure we don't try to place more monitor pairs than available slots
        # A monitor pair needs two consecutive slots.
        num_monitor_pairs = min(num_monitor_pairs, (num_total_pulses - 1) // 2)

        available_start_indices = list(range(num_total_pulses - 1)) # Indices where a pair can start (i and i+1)
        random.shuffle(available_start_indices)
        
        placed_monitor_pairs = 0
        occupied_indices = set() # To ensure no overlap between monitor pairs or data pulses overwritten

        for i in available_start_indices:
            if placed_monitor_pairs < num_monitor_pairs:
                # Check if current index and next index are free
                if i not in occupied_indices and (i + 1) not in occupied_indices:
                    pulse_type_sequence[i] = 'monitor_first'
                    pulse_type_sequence[i+1] = 'monitor_second'
                    occupied_indices.add(i)
                    occupied_indices.add(i+1)
                    placed_monitor_pairs += 1
            else:
                break
        
        for i in range(num_total_pulses):
            time_slot = i 
            pulse_type = pulse_type_sequence[i]
            
            photon_count = 0
            intended_bit = None # Only for data pulses, None for monitoring pulses
            
            if pulse_type == 'data':
                current_secret_bit = random.randint(0, 1) # Alice's choice for data bit
                self.raw_key_bits.append(current_secret_bit) # Store Alice's intended key bit
                intended_bit = current_secret_bit
                if current_secret_bit == 1: # Send a pulse for '1'
                    photon_count = self.light_source.generate_single_pulse_photon_count()
                else: # Send vacuum for '0'
                    photon_count = 0
            
            elif pulse_type == 'monitor_first' or pulse_type == 'monitor_second':
                # Monitoring pulses are always coherent pulses (non-vacuum)
                photon_count = self.light_source.generate_single_pulse_photon_count()
                intended_bit = None # Monitoring pulses don't encode key bits

            self.sent_pulses_info.append({
                'time_slot': time_slot,
                'photon_count': photon_count,
                'phase': self.data_phase, # Fixed phase for COW pulses (intensity-encoded)
                'intended_bit': intended_bit, # Alice's bit for data pulses (None for monitor)
                'pulse_type': pulse_type # 'data', 'monitor_first', 'monitor_second'
            })
        return self.sent_pulses_info

    def get_sent_pulse_info(self, time_slot):
        for pulse_info in self.sent_pulses_info:
            if pulse_info['time_slot'] == time_slot:
                return pulse_info
        return None

    def get_intended_key_bits(self):
        return self.raw_key_bits
    
