import math
import random
from .Hardware import MachZehnderInterferometer, SinglePhotonDetector

class ReceiverDPS:
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
        """
        Bob receives the current pulse and, using the previously received pulse,
        measures the phase difference via his MZI and records the detection.
        """
        measured_phase_diff = None
        bob_bit = None
        click_dm1 = False
        click_dm2 = False

        # Bob only makes a measurement if he has received photons for *both* pulses
        # that form the interference pair. If either is zero, no interference occurs.
        if previous_pulse_photons > 0 and current_pulse_photons > 0:
            # Calculate the ideal probabilities for photons exiting the MZI at DM1 and DM2
            prob_dm1_output_ideal, prob_dm2_output_ideal = self.mzi.interfere_pulses(
                previous_pulse_phase, current_pulse_phase
            )
            
            # Simulate which path the "effective" photon takes (DM1 or DM2)
            # Assuming one effective photon per pair for measurement.
            # This is a simplification; a full simulation would involve tracking individual photons.
            
            # Use a single random draw to decide which detector *would* ideally get the photon
            if random.random() < prob_dm1_output_ideal:
                # If it ideally goes to DM1, simulate detection at DM1
                click_dm1 = self.detector_dm1.detect(1) # Pass 1 for a potential photon
            else:
                # If it ideally goes to DM2, simulate detection at DM2
                click_dm2 = self.detector_dm2.detect(1) # Pass 1 for a potential photon
       
        # Even if no real photons arrive or interfere, dark counts can still occur.
        # Check for dark counts independently for each detector.
        if not click_dm1:
            click_dm1 = self.detector_dm1.detect(0) # Check for dark count (0 incident photons)
        if not click_dm2:
            click_dm2 = self.detector_dm2.detect(0) # Check for dark count (0 incident photons)

        # Infer the bit based on detector clicks
        if click_dm1 and not click_dm2:
            measured_phase_diff = 0.0 # Corresponds to a '0' bit
            bob_bit = 0
        elif click_dm2 and not click_dm1:
            measured_phase_diff = math.pi # Corresponds to a '1' bit
            bob_bit = 1
        else: 
            # If both detectors clicked or neither clicked, the measurement is inconclusive.
            # These events are typically discarded in QKD sifting to maintain security.
            measured_phase_diff = None
            bob_bit = None 
            # print(f"Debug: Inconclusive detection at time {time_slot}. DM1: {click_dm1}, DM2: {click_dm2}")

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
    """
    Models Bob's receiver for BB84-QKD.
    - Bob randomly chooses measurement bases
    - Measures received photons in chosen bases
    - Records measurement results and chosen bases for sifting
    """
    def __init__(self, detector_efficiency=0.9, dark_count_rate=1e-7):
        self.detector = SinglePhotonDetector(detector_efficiency, dark_count_rate)
        self.raw_measurements = []
        self.chosen_bases = []
        self.received_pulses_info = []
    def receive_and_measure(self, time_slot, incident_photons, encoded_state):
        chosen_basis = random.choice(['R', 'D'])
        self.chosen_bases.append(chosen_basis)
        click_occurred = self.detector.detect(incident_photons)
        measured_bit = None
        if click_occurred:
            if chosen_basis == 'R':
                if encoded_state == '|0⟩':
                    if random.random() < 0.02:
                        measured_bit = 1
                    else:
                        measured_bit = 0
                elif encoded_state == '|1⟩':
                    if random.random() < 0.02:
                        measured_bit = 0
                    else:
                        measured_bit = 1
                else:
                    measured_bit = random.randint(0, 1)
            else:
                if encoded_state == '|+⟩':
                    if random.random() < 0.02:
                        measured_bit = 1
                    else:
                        measured_bit = 0
                elif encoded_state == '|-⟩':
                    if random.random() < 0.02:
                        measured_bit = 0
                    else:
                        measured_bit = 1
                else:
                    measured_bit = random.randint(0, 1)
        else:
            measured_bit = None
        if len(self.raw_measurements) <= 3:
            print(f"BB84 Debug: Time {time_slot}, State {encoded_state}, Basis {chosen_basis}, Click {click_occurred}, Bit {measured_bit}")
        self.raw_measurements.append(measured_bit)
        measurement_info = {
            'time_slot': time_slot,
            'incident_photons': incident_photons,
            'encoded_state': encoded_state,
            'chosen_basis': chosen_basis,
            'click_occurred': click_occurred,
            'measured_bit': measured_bit
        }
        self.received_pulses_info.append(measurement_info)
        return measured_bit, chosen_basis, click_occurred
    def get_measurement_info(self, time_slot):
        for measurement_info in self.received_pulses_info:
            if measurement_info['time_slot'] == time_slot:
                return measurement_info
        return None
    def get_raw_measurements(self):
        return self.raw_measurements.copy()
    def get_chosen_bases(self):
        return self.chosen_bases.copy() 