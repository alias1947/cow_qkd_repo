import random
import math

class OpticalChannel:
    def __init__(self, distance_km, attenuation_db_per_km=0.2):
        self.distance_km = distance_km
        self.attenuation_db_per_km = attenuation_db_per_km
        self.survival_probability = 10**(-(self.distance_km * self.attenuation_db_per_km) / 10)

    def transmit_pulse(self, photon_count):
        received_photons = 0
        for _ in range(photon_count):
            if random.random() < self.survival_probability:
                received_photons += 1
        return received_photons

class MachZehnderInterferometer:
   
    def __init__(self, ideal_split_ratio=0.5):
        self.ideal_split_ratio = ideal_split_ratio

    def interfere_pulses(self, phase_n_minus_1, phase_n):
        """
        Calculates the probabilities of detection at each output port (DM1 and DM2)
        based on the phase difference between two coherent pulses.
        """
        delta_phi = (phase_n - phase_n_minus_1) % (2 * math.pi)
        
        # Normalize delta_phi to be within [-pi, pi] for consistency with cos/sin behavior
        if delta_phi > math.pi:
            delta_phi -= 2 * math.pi
        elif delta_phi < -math.pi:
            delta_phi += 2 * math.pi

        # Probabilities for detection at Detector M1 (constructive) and Detector M2 (destructive)
        # for a phase difference.
        prob_dm1 = math.cos(delta_phi / 2)**2
        prob_dm2 = math.sin(delta_phi / 2)**2
        
        return prob_dm1, prob_dm2

class SinglePhotonDetector:
    """
    Models a single-photon detector (SPD or SNSPD).
    Accounts for quantum efficiency and dark counts.
    """
    def __init__(self, quantum_efficiency=0.9, dark_count_rate_per_ns=1e-7, time_window_ns=1):
        self.quantum_efficiency = quantum_efficiency 
        self.dark_count_rate = dark_count_rate_per_ns
        self.time_window = time_window_ns 
        
        # Probability of a dark count occurring within a given time window
        self.prob_dark_count_per_window = self.dark_count_rate * self.time_window

    def detect(self, incident_photons):
        """
        Simulates the detection of photons.
        A click can occur due to an incident photon or a dark count.
        """
        click = False
        
        # First, check for detection due to actual incident photons
        if incident_photons > 0:
            # Probability that at least one photon is detected given multiple incident photons
            prob_actual_detection = 1 - (1 - self.quantum_efficiency)**incident_photons
            if random.random() < prob_actual_detection:
                click = True
        
        # If no real photon caused a click, check for a dark count
        if not click: 
             if random.random() < self.prob_dark_count_per_window:
                 click = True
                 
        return click 

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
        # For COW, Bob usually has one detector for data and monitoring pulses.
        self.data_detector = SinglePhotonDetector(detector_efficiency, dark_count_rate)
        # Minimum photons for a click to be considered a '1' (distinguishes signal from dark count for '1's)
        self.detection_threshold_photons = detection_threshold_photons 
        self.received_pulses_info = [] # Stores info about received pulses and Bob's interpretation

    def measure_pulse(self, time_slot, incident_photons, pulse_type):
        """
        Measures a single pulse for COW QKD.
        For data pulses, determines if it's a '0' or '1' based on detection.
        For monitoring pulses, just records the click status.
        """
        click = self.data_detector.detect(incident_photons)
        
        bob_inferred_bit = None # Initialize to None for inconclusive cases
        is_monitoring_click = False

        if pulse_type == 'data':
            # Simple COW logic: if the detector clicks, Bob infers a '1'. No click means '0'.
            # Errors (dark counts on a '0' slot, or photon loss on a '1' slot) are handled this way.
            if click:
                bob_inferred_bit = 1
            else: # No click
                bob_inferred_bit = 0

        elif pulse_type == 'monitor_first' or pulse_type == 'monitor_second':
            if click:
                is_monitoring_click = True
            # For monitoring pulses, Bob doesn't infer a bit. He just records if a click occurred.

        self.received_pulses_info.append({
            'time_slot': time_slot,
            'incident_photons': incident_photons,
            'click': click,
            'bob_inferred_bit': bob_inferred_bit, # Only for data pulses
            'is_monitoring_click': is_monitoring_click, # For monitoring pulses
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


#writing code for Fiber selction from ui , and provided definit params
class SMF:
    def __init__(
        self,
        length_km=20.0,
        attenuation_db_per_km=0.2,
        fiber_type="single_mode_fiber"
    ):
        """
        Models an optical fiber for QKD simulation.

        Args:
            length_km (float): Length of the fiber in kilometers.
            attenuation_db_per_km (float): Attenuation (loss) per kilometer in dB.
            fiber_type (str): Type of fiber (for future extension).
        """
        self.length_km = length_km
        self.attenuation_db_per_km = attenuation_db_per_km
        self.fiber_type = fiber_type

    def total_attenuation_db(self):
        """Returns the total attenuation in dB for the fiber."""
        return self.length_km * self.attenuation_db_per_km

    def transmission_probability(self):
        """
        Returns the probability that a photon is transmitted through the fiber.
        Uses the formula: T = 10^(-total_attenuation_db/10)
        """
        total_db = self.total_attenuation_db()
        return 10 ** (-total_db / 10)

    def __repr__(self):
        return (
            f"Fiber(length_km={self.length_km}, "
            f"attenuation_db_per_km={self.attenuation_db_per_km}, "
            f"type='{self.fiber_type}')"
        )