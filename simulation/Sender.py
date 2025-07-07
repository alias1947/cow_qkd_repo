import random
import math
from .Hardware import LightSource, PhaseModulator, IntensityModulator

class Sender:
    def __init__(self, avg_photon_number=0.2):
        self.light_source = LightSource(avg_photon_number)
        self.phase_modulator = PhaseModulator()
        self.raw_key_bits = []
        self.sent_pulses_info = []
        self.last_sent_phase = None
    def prepare_and_send_pulse(self, time_slot):
        photon_count = self.light_source.generate_single_pulse_photon_count()
        if self.last_sent_phase is None:
            modulated_phase_on_this_pulse = random.choice([0.0, math.pi])
            current_secret_bit = None
        else:
            current_secret_bit = random.randint(0, 1)
            self.raw_key_bits.append(current_secret_bit)
            desired_phase_difference_for_bit = 0.0 if current_secret_bit == 0 else math.pi
            modulated_phase_on_this_pulse = self.phase_modulator.modulate_phase(
                self.last_sent_phase, desired_phase_difference_for_bit
            )
        self.last_sent_phase = modulated_phase_on_this_pulse
        self.sent_pulses_info.append({
            'time_slot': time_slot,
            'photon_count': photon_count,
            'modulated_phase': modulated_phase_on_this_pulse,
            'alice_intended_bit_for_pair': current_secret_bit
        })
        return modulated_phase_on_this_pulse, photon_count
    def get_pulse_info(self, time_slot):
        for pulse_info in self.sent_pulses_info:
            if pulse_info['time_slot'] == time_slot:
                return pulse_info
        return None

class SenderCOW:
    def __init__(self, avg_photon_number=0.2, monitor_pulse_ratio=0.1, extinction_ratio_db=20.0):
        if not (0 < avg_photon_number < 1):
            raise ValueError("Average photon number (mu) for COW should be between 0 and 1.")
        self.light_source = LightSource(avg_photon_number)
        self.phase_modulator = PhaseModulator()
        self.intensity_modulator = IntensityModulator(extinction_ratio_db)
        self.mu = avg_photon_number
        self.raw_key_bits = []
        self.sent_pulses_info = []
        self.data_phase = 0.0
        self.monitor_pulse_ratio = monitor_pulse_ratio
    def prepare_pulse_train(self, num_total_pulses):
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
                bit = random.randint(0, 1)
                self.raw_key_bits.append(bit)
                if bit == 0:
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
    def __init__(self, avg_photon_number=0.2):
        self.light_source = LightSource(avg_photon_number)
        self.phase_modulator = PhaseModulator()
        self.intensity_modulator = IntensityModulator()
        self.raw_key_bits = []
        self.chosen_bases = []
        self.sent_pulses_info = []
    def prepare_and_send_pulse(self, time_slot):
        bit = random.randint(0, 1)
        basis = random.choice(['Z', 'X'])
        self.raw_key_bits.append(bit)
        self.chosen_bases.append(basis)
        if basis == 'Z':
            encoded_state = 'Z0' if bit == 0 else 'Z1'
        else:
            encoded_state = 'X+' if bit == 0 else 'X-'
        photon_count = self.light_source.generate_single_pulse_photon_count()
        self.sent_pulses_info.append({
            'time_slot': time_slot,
            'photon_count': photon_count,
            'encoded_state': encoded_state,
            'bit': bit,
            'basis': basis
        })
        return encoded_state, photon_count
    def get_pulse_info(self, time_slot):
        for pulse_info in self.sent_pulses_info:
            if pulse_info['time_slot'] == time_slot:
                return pulse_info
        return None
    def get_raw_key_bits(self):
        return self.raw_key_bits
    def get_chosen_bases(self):
        return self.chosen_bases 