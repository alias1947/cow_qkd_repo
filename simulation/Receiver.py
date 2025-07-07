import math
import random
from .Hardware import MachZehnderInterferometer, SinglePhotonDetector
# ... existing code ...

class Receiver:
    """
    Models Bob's receiver for DPS-QKD, including a Mach-Zehnder Interferometer
    and two single-photon detectors.
    """
    def __init__(self, detector_efficiency=0.9, dark_count_rate=1e-7):
        self.mzi = MachZehnderInterferometer()
        self.detector_dm1 = SinglePhotonDetector(detector_efficiency, dark_count_rate)
        self.detector_dm2 = SinglePhotonDetector(detector_efficiency, dark_count_rate)
        self.raw_clicks_info = [] # Stores (time_slot, click_dm1, click_dm2, measured_phase_diff)

    def receive_and_measure(self, time_slot, current_pulse_photons, current_pulse_phase, 
                            previous_pulse_photons, previous_pulse_phase):
        measured_phase_diff = None
        bob_bit = None
        click_dm1 = False
        click_dm2 = False
        if previous_pulse_photons > 0 and current_pulse_photons > 0:
            prob_dm1_output_ideal, prob_dm2_output_ideal = self.mzi.interfere_pulses(
                previous_pulse_phase, current_pulse_phase
            )
            if random.random() < prob_dm1_output_ideal:
                click_dm1 = self.detector_dm1.detect(1)
            else:
                click_dm2 = self.detector_dm2.detect(1)
        if not click_dm1:
            click_dm1 = self.detector_dm1.detect(0)
        if not click_dm2:
            click_dm2 = self.detector_dm2.detect(0)
        if click_dm1 and not click_dm2:
            measured_phase_diff = 0.0
            bob_bit = 0
        elif click_dm2 and not click_dm1:
            measured_phase_diff = math.pi
            bob_bit = 1
        else:
            measured_phase_diff = None
            bob_bit = None
        self.raw_clicks_info.append({
            'time_slot': time_slot,
            'click_dm1': click_dm1,
            'click_dm2': click_dm2,
            'measured_phase_diff': measured_phase_diff,
            'bob_inferred_bit': bob_bit
        })
        return click_dm1, click_dm2, measured_phase_diff, bob_bit

class ReceiverCOW:
    """
    Models Bob's receiver for COW-QKD.
    """
    def __init__(self, detector_efficiency=0.9, dark_count_rate=1e-7, detection_threshold_photons=0):
        self.data_detector = SinglePhotonDetector(detector_efficiency, dark_count_rate)
        self.detection_threshold_photons = detection_threshold_photons
        self.received_pulses_info = []
    def measure_pulse(self, time_slot, incident_photons, pulse_type):
        click = self.data_detector.detect(incident_photons)
        bob_inferred_bit = None
        is_monitoring_click = False
        if pulse_type.startswith('data'):
            if click:
                bob_inferred_bit = 1
            else:
                bob_inferred_bit = 0
        elif pulse_type == 'monitor_first' or pulse_type == 'monitor_second':
            if click:
                is_monitoring_click = True
        self.received_pulses_info.append({
            'time_slot': time_slot,
            'incident_photons': incident_photons,
            'click': click,
            'bob_inferred_bit': bob_inferred_bit,
            'is_monitoring_click': is_monitoring_click,
            'pulse_type': pulse_type
        })
        return click, bob_inferred_bit, is_monitoring_click
    def get_received_pulse_info(self, time_slot):
        for pulse_info in self.received_pulses_info:
            if pulse_info['time_slot'] == time_slot:
                return pulse_info
        return None
    def get_all_received_info(self):
        return self.received_pulses_info

class ReceiverBB84:
    def __init__(self, detector_efficiency=0.9, dark_count_rate=1e-7):
        self.detector = SinglePhotonDetector(detector_efficiency, dark_count_rate)
        self.measurements = []
        self.chosen_bases = []
    def receive_and_measure(self, time_slot, incident_photons, encoded_state):
        click = self.detector.detect(incident_photons)
        measured_bit = None
        chosen_basis = random.choice(['Z', 'X'])
        if click:
            if encoded_state == 'Z0':
                measured_bit = 0
            elif encoded_state == 'Z1':
                measured_bit = 1
            elif encoded_state == 'X+':
                measured_bit = 0
            elif encoded_state == 'X-':
                measured_bit = 1
        self.measurements.append({
            'time_slot': time_slot,
            'incident_photons': incident_photons,
            'click': click,
            'measured_bit': measured_bit,
            'chosen_basis': chosen_basis
        })
        self.chosen_bases.append(chosen_basis)
        return click, measured_bit, chosen_basis
    def get_measurement_info(self, time_slot):
        for m in self.measurements:
            if m['time_slot'] == time_slot:
                return m
        return None
    def get_raw_measurements(self):
        return self.measurements
    def get_chosen_bases(self):
        return self.chosen_bases 