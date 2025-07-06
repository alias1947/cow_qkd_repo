# dps_qkd_source.py

import random
import math

class LightSource:
    
    def __init__(self, average_photon_number=0.2):
        if not (0 < average_photon_number < 1):
            raise ValueError("Average photon number (mu) for WCP should be between 0 and 1.")
        self.mu = average_photon_number 

    def generate_single_pulse_photon_count(self, mu=None):
        if mu is None:
            mu = self.mu
        num_photons = 0
        L = math.exp(-mu)
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

class IntensityModulator:
    """
    Models an intensity modulator with a finite extinction ratio.
    The extinction ratio is the ratio of maximum power (on) to minimum power (off).
    """
    def __init__(self, extinction_ratio_db=20.0):
        if extinction_ratio_db <= 0:
            raise ValueError("Extinction ratio must be a positive value in dB.")
        self.extinction_ratio_db = extinction_ratio_db
        # Convert dB to a linear ratio
        self.extinction_ratio_linear = 10**(self.extinction_ratio_db / 10)

    def modulate(self, base_mu, state):
        """
        Modulates the intensity of the light source.
        Returns the effective average photon number (mu) for the given state.
        """
        if state == 'on':
            return base_mu
        elif state == 'off':
            # For the 'off' state, mu is reduced by the extinction ratio
            return base_mu / self.extinction_ratio_linear
        else:
            raise ValueError("Modulator state must be 'on' or 'off'")

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
    def __init__(self, avg_photon_number=0.2, monitor_pulse_ratio=0.1, extinction_ratio_db=20.0):
        """
        COW sender: prepares pulse pairs as per protocol.
        - Data pairs: |0⟩|α⟩ (bit 0), |α⟩|0⟩ (bit 1), each with probability (1-f)/2
        - Decoy/monitor pairs: |α⟩|α⟩, with probability f
        - mu (avg_photon_number) must be < 1
        """
        if not (0 < avg_photon_number < 1):
            raise ValueError("Average photon number (mu) for COW should be between 0 and 1.")
        self.light_source = LightSource(avg_photon_number)
        self.phase_modulator = PhaseModulator() # Not typically used for COW data encoding, but kept for consistency
        self.intensity_modulator = IntensityModulator(extinction_ratio_db)
        self.mu = avg_photon_number
        self.raw_key_bits = []  # Alice's chosen bits (for data pairs only)
        self.sent_pulses_info = [] # Info about what was actually sent
        self.data_phase = 0.0 # Fixed phase for COW data pulses ('1') and monitoring pulses
        self.monitor_pulse_ratio = monitor_pulse_ratio # f: Fraction of pairs used for monitoring/decoy

    def prepare_pulse_train(self, num_total_pulses):
        """
        Prepares a sequence of pulse pairs for COW protocol.
        Each pair is either:
        - Data: |0⟩|α⟩ (bit 0) or |α⟩|0⟩ (bit 1), each with probability (1-f)/2
        - Decoy: |α⟩|α⟩, with probability f
        Returns a flat list of pulses (dicts) with time_slot, photon_count, phase, intended_bit, pulse_type.
        """
        self.raw_key_bits = []
        self.sent_pulses_info = []
        f = self.monitor_pulse_ratio
        num_pairs = num_total_pulses // 2
        time_slot = 0
        mu_on = self.intensity_modulator.modulate(self.mu, 'on')
        mu_off = self.intensity_modulator.modulate(self.mu, 'off')
        for _ in range(num_pairs):
            r = random.random()
            if r < f:
                # Decoy/monitor pair: |α⟩|α⟩
                self.sent_pulses_info.append({
                    'time_slot': time_slot,
                    'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                    'phase': self.data_phase,
                    'intended_bit': None,
                    'pulse_type': 'monitor_first'
                })
                time_slot += 1
                self.sent_pulses_info.append({
                    'time_slot': time_slot,
                    'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                    'phase': self.data_phase,
                    'intended_bit': None,
                    'pulse_type': 'monitor_second'
                })
                time_slot += 1
            else:
                # Data pair: randomly choose bit 0 or 1
                bit = random.randint(0, 1)
                self.raw_key_bits.append(bit)
                if bit == 0:
                    # |0⟩|α⟩
                    self.sent_pulses_info.append({
                        'time_slot': time_slot,
                        'photon_count': self.light_source.generate_single_pulse_photon_count(mu_off),
                        'phase': self.data_phase,
                        'intended_bit': bit,
                        'pulse_type': 'data_first'
                    })
                    time_slot += 1
                    self.sent_pulses_info.append({
                        'time_slot': time_slot,
                        'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                        'phase': self.data_phase,
                        'intended_bit': bit,
                        'pulse_type': 'data_second'
                    })
                    time_slot += 1
                else:
                    # |α⟩|0⟩
                    self.sent_pulses_info.append({
                        'time_slot': time_slot,
                        'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                        'phase': self.data_phase,
                        'intended_bit': bit,
                        'pulse_type': 'data_first'
                    })
                    time_slot += 1
                    self.sent_pulses_info.append({
                        'time_slot': time_slot,
                        'photon_count': self.light_source.generate_single_pulse_photon_count(mu_off),
                        'phase': self.data_phase,
                        'intended_bit': bit,
                        'pulse_type': 'data_second'
                    })
                    time_slot += 1
        return self.sent_pulses_info

    def get_sent_pulse_info(self, time_slot):
        for pulse_info in self.sent_pulses_info:
            if pulse_info['time_slot'] == time_slot:
                return pulse_info
        return None

    def get_intended_key_bits(self):
        return self.raw_key_bits

class SenderBB84:
    """
    BB84 sender (Alice) implementation.
    - Generates random bits and encodes them in randomly chosen bases
    - Uses four quantum states: |0⟩, |1⟩ (rectilinear) and |+⟩, |-⟩ (diagonal)
    - Sends encoded photons through quantum channel
    """
    def __init__(self, avg_photon_number=0.2):
        """
        Initialize BB84 sender.
        avg_photon_number: average photon number per pulse (mu)
        """
        if not (0 < avg_photon_number < 1):
            raise ValueError("Average photon number (mu) for BB84 should be between 0 and 1.")
        self.light_source = LightSource(avg_photon_number)
        self.raw_key_bits = []  # Alice's chosen bits
        self.chosen_bases = []  # Alice's chosen bases ('R' for rectilinear, 'D' for diagonal)
        self.sent_pulses_info = []  # Information about sent pulses
        
    def prepare_and_send_pulse(self, time_slot):
        """
        Prepare and send a single BB84 pulse.
        Returns: (encoded_state, photon_count, chosen_bit, chosen_basis)
        """
        # Step 1: Alice generates a random bit
        chosen_bit = random.randint(0, 1)
        self.raw_key_bits.append(chosen_bit)
        
        # Step 2: Alice randomly chooses a basis (rectilinear or diagonal)
        chosen_basis = random.choice(['R', 'D'])  # R for rectilinear, D for diagonal
        self.chosen_bases.append(chosen_basis)
        
        # Step 3: Alice encodes the bit in the chosen basis
        if chosen_basis == 'R':  # Rectilinear basis
            # |0⟩ = (1, 0) for bit 0, |1⟩ = (0, 1) for bit 1
            encoded_state = '|0⟩' if chosen_bit == 0 else '|1⟩'
        else:  # Diagonal basis
            # |+⟩ = 1/√2(1, 1) for bit 0, |-⟩ = 1/√2(1, -1) for bit 1
            encoded_state = '|+⟩' if chosen_bit == 0 else '|-⟩'
        
        # Step 4: Generate photon count for the pulse
        photon_count = self.light_source.generate_single_pulse_photon_count()
        
        # Store pulse information
        pulse_info = {
            'time_slot': time_slot,
            'photon_count': photon_count,
            'encoded_state': encoded_state,
            'chosen_bit': chosen_bit,
            'chosen_basis': chosen_basis
        }
        self.sent_pulses_info.append(pulse_info)
        
        return encoded_state, photon_count, chosen_bit, chosen_basis
    
    def get_pulse_info(self, time_slot):
        """Retrieves information about a pulse Alice sent at a given time slot."""
        for pulse_info in self.sent_pulses_info:
            if pulse_info['time_slot'] == time_slot:
                return pulse_info
        return None
    
    def get_raw_key_bits(self):
        """Returns Alice's raw key bits."""
        return self.raw_key_bits.copy()
    
    def get_chosen_bases(self):
        """Returns Alice's chosen bases."""
        return self.chosen_bases.copy()
    
