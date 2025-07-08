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
        self.extinction_ratio_linear = 10**(self.extinction_ratio_db / 10)
    def modulate(self, base_mu, state):
        if state == 'on':
            return base_mu
        elif state == 'off':
            return base_mu / self.extinction_ratio_linear
        else:
            raise ValueError("Modulator state must be 'on' or 'off'")

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