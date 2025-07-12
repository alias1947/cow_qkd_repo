QKD Protocols
=============

This section provides comprehensive documentation of the three QKD protocols implemented in the platform: DPS-QKD, COW-QKD, and BB84-QKD.

DPS-QKD (Differential Phase Shift)
---------------------------------

Overview
~~~~~~~~

Differential Phase Shift Quantum Key Distribution (DPS-QKD) is a protocol that encodes information in the phase difference between consecutive optical pulses. It was developed to provide a simple and robust implementation of QKD using standard optical components.

Theory
~~~~~~

**Principle**: Information is encoded in the phase difference between consecutive pulses rather than the absolute phase of individual pulses.

**Encoding Scheme**:
- **Bit 0**: Phase difference :math:`\Delta\phi = 0`
- **Bit 1**: Phase difference :math:`\Delta\phi = \pi`

**Detection Method**: Mach-Zehnder interferometer with two detectors (DM1 and DM2)

**Key Features**:
- Simple phase encoding
- Robust against phase drift
- Uses standard telecom components
- High key rate potential

Mathematical Model
~~~~~~~~~~~~~~~~~

**Phase Encoding**:
For pulse pair :math:`(n-1, n)`:
- Random bit :math:`b \in \{0,1\}`
- Phase difference :math:`\Delta\phi_n = b \cdot \pi`
- Absolute phase :math:`\phi_n = \phi_{n-1} + \Delta\phi_n`

**Interference Measurement**:
The Mach-Zehnder interferometer measures the phase difference:
- Detector 1 (DM1) click probability: :math:`P_1 = \cos^2(\Delta\phi/2)`
- Detector 2 (DM2) click probability: :math:`P_2 = \sin^2(\Delta\phi/2)`

**Bit Inference**:
- DM1 click only: :math:`b_{inferred} = 0`
- DM2 click only: :math:`b_{inferred} = 1`
- Both or neither click: inconclusive measurement

Implementation
~~~~~~~~~~~~~

The DPS-QKD implementation is split between sender and receiver classes:

**Sender Implementation** (:class:`simulation.Sender.SenderDPS`):

.. code-block:: python

   class SenderDPS:
       def __init__(self, avg_photon_number=0.2):
           self.light_source = LightSource(avg_photon_number)
           self.phase_modulator = PhaseModulator()
           self.raw_key_bits = []
           self.sent_pulses_info = []
           self.last_sent_phase = None

       def prepare_and_send_pulse(self, time_slot):
           photon_count = self.light_source.generate_single_pulse_photon_count()
           
           if self.last_sent_phase is None:
               # First pulse - random phase
               modulated_phase = random.choice([0.0, math.pi])
               current_secret_bit = None
           else:
               # Encode bit in phase difference
               current_secret_bit = random.randint(0, 1)
               self.raw_key_bits.append(current_secret_bit)
               desired_phase_difference = 0.0 if current_secret_bit == 0 else math.pi
               modulated_phase = self.phase_modulator.modulate_phase(
                   self.last_sent_phase, desired_phase_difference
               )
           
           self.last_sent_phase = modulated_phase
           return modulated_phase, photon_count
```

**Receiver Implementation** (:class:`simulation.Receiver.ReceiverDPS`):

.. code-block:: python

   class ReceiverDPS:
       def __init__(self, detector_efficiency=0.9, dark_count_rate=1e-7):
           self.mzi = MachZehnderInterferometer()
           self.detector_dm1 = SinglePhotonDetector(detector_efficiency, dark_count_rate)
           self.detector_dm2 = SinglePhotonDetector(detector_efficiency, dark_count_rate)

       def receive_and_measure(self, time_slot, current_pulse_photons, 
                             current_pulse_phase, previous_pulse_photons, 
                             previous_pulse_phase):
           # Calculate interference probabilities
           prob_dm1, prob_dm2 = self.mzi.interfere_pulses(
               previous_pulse_phase, current_pulse_phase
           )
           
           # Simulate detection
           click_dm1 = self.detector_dm1.detect(1 if random.random() < prob_dm1 else 0)
           click_dm2 = self.detector_dm2.detect(1 if random.random() < prob_dm2 else 0)
           
           # Infer bit
           if click_dm1 and not click_dm2:
               bob_bit = 0
           elif click_dm2 and not click_dm1:
               bob_bit = 1
           else:
               bob_bit = None  # Inconclusive
           
           return click_dm1, click_dm2, measured_phase_diff, bob_bit
```

**Key Generation Process**:

.. code-block:: python

   def generate_and_share_key(self, target_node, num_pulses, 
                            pulse_repetition_rate_ns, phase_flip_prob=0.0):
       # Generate pulse train
       for i in range(num_pulses):
           time_slot = i * pulse_repetition_rate_ns
           modulated_phase, photon_count = self.prepare_and_send_pulse(time_slot)
       
       # Transmit through channel
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
       
       # Bob's measurements
       bob_clicks_and_inferred_bits = []
       for i, current_pulse in enumerate(channel_processed_pulses):
           previous_pulse = channel_processed_pulses[i-1] if i > 0 else dummy_pulse
           
           click_dm1, click_dm2, measured_phase_diff, bob_bit = \
               target_node.receive_and_measure(
                   current_pulse['time_slot'],
                   current_pulse['received_photon_count'],
                   current_pulse['modulated_phase'],
                   previous_pulse['received_photon_count'],
                   previous_pulse['modulated_phase']
               )
           
           bob_clicks_and_inferred_bits.append({
               'time_slot': current_pulse['time_slot'],
               'click_dm1': click_dm1,
               'click_dm2': click_dm2,
               'measured_phase_diff': measured_phase_diff,
               'bob_inferred_bit': bob_bit
           })
       
       # Sifting process
       alice_sifted_key = []
       bob_sifted_key = []
       
       for i in range(1, len(alice_pulses_sent_info)):
           alice_pn_minus_1 = alice_pulses_sent_info[i-1]
           alice_pn = alice_pulses_sent_info[i]
           
           bob_measurement = bob_clicks_and_inferred_bits[i]
           
           if bob_measurement['bob_inferred_bit'] is not None:
               # Calculate Alice's intended bit
               alice_intended_delta_phi = (alice_pn['modulated_phase'] - 
                                         alice_pn_minus_1['modulated_phase']) % (2 * math.pi)
               
               if alice_intended_delta_phi > math.pi:
                   alice_intended_delta_phi -= 2 * math.pi
               
               alice_intended_bit = 0 if math.isclose(alice_intended_delta_phi, 0.0) else 1
               
               alice_sifted_key.append(alice_intended_bit)
               bob_sifted_key.append(bob_measurement['bob_inferred_bit'])
       
       return alice_sifted_key, bob_sifted_key
```

Usage Example
~~~~~~~~~~~~

.. code-block:: python

   from simulation.Network import Network
   from main import calculate_qber, postprocessing

   # Create network
   network = Network()
   alice = network.add_node('Alice', avg_photon_number=0.2)
   bob = network.add_node('Bob', detector_efficiency=0.9, dark_count_rate=1e-7)
   network.connect_nodes('Alice', 'Bob', distance_km=20)

   # Generate key
   alice_key, bob_key = alice.generate_and_share_key(
       bob, num_pulses=10000, pulse_repetition_rate_ns=1, phase_flip_prob=0.05
   )

   # Analyze results
   qber, num_errors = calculate_qber(alice_key, bob_key)
   final_key_len, postproc = postprocessing(len(alice_key), qber)

   print(f"QBER: {qber:.4f}")
   print(f"Sifted key length: {len(alice_key)}")
   print(f"Final key length: {final_key_len}")
```

Performance Characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Sifting Efficiency**: ~25% of raw bits
- **QBER Range**: 3-11% for practical systems
- **Key Rate**: High potential due to simple encoding
- **Security**: Based on quantum interference
- **Hardware Requirements**: Standard telecom components

COW-QKD (Coherent One-Way)
--------------------------

Overview
~~~~~~~~

Coherent One-Way Quantum Key Distribution (COW-QKD) is a protocol that uses intensity modulation to encode information and includes monitoring pulses for eavesdropping detection. It was designed to be simple, robust, and secure against various attacks.

Theory
~~~~~~

**Principle**: Information is encoded in the intensity of optical pulses, with monitoring pulses used to detect eavesdropping attempts.

**Encoding Scheme**:
- **Bit 0**: Vacuum pulse followed by coherent pulse (intensity :math:`I_0` then :math:`I_1`)
- **Bit 1**: Coherent pulse followed by vacuum pulse (intensity :math:`I_1` then :math:`I_0`)
- **Monitoring**: Pairs of coherent pulses for eavesdropping detection

**Detection Method**: Single photon detector with intensity monitoring

**Key Features**:
- Simple intensity modulation
- Built-in eavesdropping detection
- Robust against various attacks
- High key rate potential

Mathematical Model
~~~~~~~~~~~~~~~~~

**Pulse Types**:
- **Data Pulse 0**: :math:`I_0 = \mu_{off}`, :math:`I_1 = \mu_{on}`
- **Data Pulse 1**: :math:`I_0 = \mu_{on}`, :math:`I_1 = \mu_{off}`
- **Monitoring Pulse**: :math:`I_0 = \mu_{on}`, :math:`I_1 = \mu_{on}`

**Detection Model**:
- Click probability: :math:`P_{click} = 1 - e^{-\eta I}`
- Where :math:`\eta` is detector efficiency and :math:`I` is intensity

**Sifting Process**:
- Keep bit if both Alice and Bob identify pulse as data
- Discard if either identifies as monitoring
- Check monitoring pulses for eavesdropping detection

Implementation
~~~~~~~~~~~~~

**Sender Implementation** (:class:`simulation.Sender.SenderCOW`):

.. code-block:: python

   class SenderCOW:
       def __init__(self, avg_photon_number=0.2, monitor_pulse_ratio=0.1, 
                    extinction_ratio_db=20.0):
           self.light_source = LightSource(avg_photon_number)
           self.intensity_modulator = IntensityModulator(extinction_ratio_db)
           self.mu = avg_photon_number
           self.monitor_pulse_ratio = monitor_pulse_ratio

       def prepare_pulse_train(self, num_total_pulses):
           self.raw_key_bits = []
           self.sent_pulses_info = []
           
           num_pairs = num_total_pulses // 2
           time_slot = 0
           
           mu_on = self.intensity_modulator.modulate(self.mu, 'on')
           mu_off = self.intensity_modulator.modulate(self.mu, 'off')
           
           for _ in range(num_pairs):
               r = random.random()
               
               if r < self.monitor_pulse_ratio:
                   # Monitoring pulse pair
                   self.sent_pulses_info.extend([
                       {
                           'time_slot': time_slot,
                           'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                           'phase': 0.0,
                           'intended_bit': None,
                           'pulse_type': 'monitor_first'
                       },
                       {
                           'time_slot': time_slot + 1,
                           'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                           'phase': 0.0,
                           'intended_bit': None,
                           'pulse_type': 'monitor_second'
                       }
                   ])
                   time_slot += 2
               else:
                   # Data pulse pair
                   bit = random.randint(0, 1)
                   self.raw_key_bits.append(bit)
                   
                   if bit == 0:
                       # Vacuum then coherent
                       self.sent_pulses_info.extend([
                           {
                               'time_slot': time_slot,
                               'photon_count': self.light_source.generate_single_pulse_photon_count(mu_off),
                               'phase': 0.0,
                               'intended_bit': bit,
                               'pulse_type': 'data_first'
                           },
                           {
                               'time_slot': time_slot + 1,
                               'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                               'phase': 0.0,
                               'intended_bit': bit,
                               'pulse_type': 'data_second'
                           }
                       ])
                   else:
                       # Coherent then vacuum
                       self.sent_pulses_info.extend([
                           {
                               'time_slot': time_slot,
                               'photon_count': self.light_source.generate_single_pulse_photon_count(mu_on),
                               'phase': 0.0,
                               'intended_bit': bit,
                               'pulse_type': 'data_first'
                           },
                           {
                               'time_slot': time_slot + 1,
                               'photon_count': self.light_source.generate_single_pulse_photon_count(mu_off),
                               'phase': 0.0,
                               'intended_bit': bit,
                               'pulse_type': 'data_second'
                           }
                       ])
                   time_slot += 2
           
           return self.sent_pulses_info
```

**Receiver Implementation** (:class:`simulation.Receiver.ReceiverCOW`):

.. code-block:: python

   class ReceiverCOW:
       def __init__(self, detector_efficiency=0.9, dark_count_rate=1e-7, 
                    detection_threshold_photons=0):
           self.data_detector = SinglePhotonDetector(detector_efficiency, dark_count_rate)
           self.detection_threshold_photons = detection_threshold_photons
           self.received_pulses_info = []

       def measure_pulse(self, time_slot, incident_photons, pulse_type):
           click = self.data_detector.detect(incident_photons)
           bob_inferred_bit = None
           is_monitoring_click = False
           
           if pulse_type.startswith('data'):
               # Data pulse - infer bit based on click
               if click:
                   bob_inferred_bit = 1
               else:
                   bob_inferred_bit = 0
           elif pulse_type.startswith('monitor'):
               # Monitoring pulse - check for eavesdropping
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
```

**Key Generation Process**:

.. code-block:: python

   def generate_and_share_key_cow(self, target_node, num_pulses, 
                                pulse_repetition_rate_ns, monitor_pulse_ratio=0.1,
                                detection_threshold_photons=0, phase_flip_prob=0.0,
                                bit_flip_error_prob=0.0):
       # Prepare pulse train
       alice_sent_pulses_info = self.cow_sender.prepare_pulse_train(num_pulses)
       
       # Transmit through channel
       bob_received_signals = []
       for i, sent_pulse in enumerate(alice_sent_pulses_info):
           received_photons = channel.transmit_pulse(sent_pulse['photon_count'])
           
           # Apply noise
           final_phase = sent_pulse['phase']
           if random.random() < phase_flip_prob:
               final_phase = (final_phase + math.pi) % (2 * math.pi)
           
           bob_received_signals.append({
               'time_slot': sent_pulse['time_slot'],
               'received_photons': received_photons,
               'pulse_type': sent_pulse['pulse_type'],
               'final_phase': final_phase
           })
       
       # Bob's measurements
       bob_measurements = []
       for received_signal in bob_received_signals:
           click, bob_inferred_bit, is_monitoring_click = \
               target_node.cow_receiver.measure_pulse(
                   received_signal['time_slot'],
                   received_signal['received_photons'],
                   received_signal['pulse_type']
               )
           
           bob_measurements.append({
               'time_slot': received_signal['time_slot'],
               'click': click,
               'bob_inferred_bit': bob_inferred_bit,
               'is_monitoring_click': is_monitoring_click,
               'pulse_type': received_signal['pulse_type']
           })
       
       # Sifting process
       alice_sifted_key = []
       bob_sifted_key = []
       
       for i in range(0, len(alice_sent_pulses_info), 2):
           if i + 1 >= len(alice_sent_pulses_info):
               break
           
           pulse1 = alice_sent_pulses_info[i]
           pulse2 = alice_sent_pulses_info[i + 1]
           
           bob_measurement1 = bob_measurements[i]
           bob_measurement2 = bob_measurements[i + 1]
           
           # Check if both pulses are data pulses
           if (pulse1['pulse_type'].startswith('data') and 
               pulse2['pulse_type'].startswith('data')):
               
               # Check if Bob agrees on data pulses
               if (bob_measurement1['bob_inferred_bit'] is not None and
                   bob_measurement2['bob_inferred_bit'] is not None):
                   
                   # Apply bit flip error
                   alice_bit = pulse1['intended_bit']
                   bob_bit = bob_measurement1['bob_inferred_bit']
                   
                   if random.random() < bit_flip_error_prob:
                       bob_bit = 1 - bob_bit
                   
                   alice_sifted_key.append(alice_bit)
                   bob_sifted_key.append(bob_bit)
       
       return alice_sifted_key, bob_sifted_key
```

Usage Example
~~~~~~~~~~~~

.. code-block:: python

   # Create network
   network = Network()
   alice = network.add_node('Alice', avg_photon_number=0.1)
   bob = network.add_node('Bob', detector_efficiency=0.9, dark_count_rate=1e-7)
   network.connect_nodes('Alice', 'Bob', distance_km=20)

   # Generate key with COW protocol
   alice_key, bob_key = alice.generate_and_share_key_cow(
       bob, num_pulses=10000, pulse_repetition_rate_ns=1,
       monitor_pulse_ratio=0.1, detection_threshold_photons=0,
       phase_flip_prob=0.05, bit_flip_error_prob=0.05
   )

   # Analyze results
   qber, num_errors = calculate_qber(alice_key, bob_key)
   final_key_len, postproc = postprocessing(len(alice_key), qber)

   print(f"COW-QKD Results:")
   print(f"QBER: {qber:.4f}")
   print(f"Sifted key length: {len(alice_key)}")
   print(f"Final key length: {final_key_len}")
```

Performance Characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Sifting Efficiency**: ~40% of raw bits
- **QBER Range**: 3-10% for practical systems
- **Key Rate**: High due to simple intensity modulation
- **Security**: Built-in eavesdropping detection
- **Hardware Requirements**: Standard optical components

BB84-QKD (Bennett-Brassard 1984)
--------------------------------

Overview
~~~~~~~~

BB84 is the original quantum key distribution protocol, proposed by Bennett and Brassard in 1984. It uses four quantum states in two conjugate bases to achieve secure key distribution based on the principles of quantum mechanics.

Theory
~~~~~~

**Principle**: Information is encoded in quantum states using two conjugate bases, with security based on the quantum uncertainty principle.

**Encoding Scheme**:
- **Rectilinear Basis (R)**: :math:`|0\rangle` (horizontal), :math:`|1\rangle` (vertical)
- **Diagonal Basis (D)**: :math:`|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)`, :math:`|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)`

**Detection Method**: Single photon detector with basis switching

**Key Features**:
- Original QKD protocol
- Information-theoretic security
- Basis reconciliation
- Proven security against various attacks

Mathematical Model
~~~~~~~~~~~~~~~~~

**State Preparation**:
- Random bit :math:`b \in \{0,1\}`
- Random basis :math:`B \in \{R,D\}`
- State: :math:`|\psi\rangle = |b\rangle_B`

**Measurement**:
- Random basis choice :math:`B' \in \{R,D\}`
- Measurement outcome: :math:`b' \in \{0,1\}` or no detection

**Sifting Process**:
- Keep bit if :math:`B = B'` and detection occurred
- Discard if :math:`B \neq B'` or no detection

**Security**: Based on quantum uncertainty principle - measuring in wrong basis disturbs the state

Implementation
~~~~~~~~~~~~~

**Sender Implementation** (:class:`simulation.Sender.SenderBB84`):

.. code-block:: python

   class SenderBB84:
       def __init__(self, avg_photon_number=0.2):
           self.light_source = LightSource(avg_photon_number)
           self.raw_key_bits = []
           self.chosen_bases = []
           self.sent_pulses_info = []

       def prepare_and_send_pulse(self, time_slot):
           chosen_bit = random.randint(0, 1)
           self.raw_key_bits.append(chosen_bit)
           
           chosen_basis = random.choice(['R', 'D'])
           self.chosen_bases.append(chosen_basis)
           
           if chosen_basis == 'R':
               encoded_state = '|0⟩' if chosen_bit == 0 else '|1⟩'
           else:
               encoded_state = '|+⟩' if chosen_bit == 0 else '|-⟩'
           
           photon_count = self.light_source.generate_single_pulse_photon_count()
           
           pulse_info = {
               'time_slot': time_slot,
               'photon_count': photon_count,
               'encoded_state': encoded_state,
               'chosen_bit': chosen_bit,
               'chosen_basis': chosen_basis
           }
           self.sent_pulses_info.append(pulse_info)
           
           return encoded_state, photon_count, chosen_bit, chosen_basis
```

**Receiver Implementation** (:class:`simulation.Receiver.ReceiverBB84`):

.. code-block:: python

   class ReceiverBB84:
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
                   # Measure in rectilinear basis
                   if encoded_state == '|0⟩':
                       measured_bit = 0 if random.random() > 0.02 else 1
                   elif encoded_state == '|1⟩':
                       measured_bit = 1 if random.random() > 0.02 else 0
                   else:
                       measured_bit = random.randint(0, 1)
               else:
                   # Measure in diagonal basis
                   if encoded_state == '|+⟩':
                       measured_bit = 0 if random.random() > 0.02 else 1
                   elif encoded_state == '|-⟩':
                       measured_bit = 1 if random.random() > 0.02 else 0
                   else:
                       measured_bit = random.randint(0, 1)
           
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
```

**Key Generation Process**:

.. code-block:: python

   def generate_and_share_key_bb84(self, target_node, num_pulses, 
                                 pulse_repetition_rate_ns, phase_flip_prob=0.0):
       # Generate pulse train
       for i in range(num_pulses):
           time_slot = i * pulse_repetition_rate_ns
           encoded_state, photon_count, chosen_bit, chosen_basis = \
               self.bb84_sender.prepare_and_send_pulse(time_slot)
       
       # Transmit through channel
       channel_processed_pulses = []
       for pulse in alice_pulses_sent_info:
           received_photons = channel.transmit_pulse(pulse['photon_count'])
           
           channel_processed_pulses.append({
               'time_slot': pulse['time_slot'],
               'received_photon_count': received_photons,
               'encoded_state': pulse['encoded_state']
           })
       
       # Bob's measurements
       bob_measurements = []
       for pulse in channel_processed_pulses:
           measured_bit, chosen_basis, click_occurred = \
               target_node.bb84_receiver.receive_and_measure(
                   pulse['time_slot'],
                   pulse['received_photon_count'],
                   pulse['encoded_state']
               )
           
           bob_measurements.append({
               'time_slot': pulse['time_slot'],
               'measured_bit': measured_bit,
               'chosen_basis': chosen_basis,
               'click_occurred': click_occurred
           })
       
       # Sifting process
       alice_sifted_key = []
       bob_sifted_key = []
       
       for i, alice_pulse in enumerate(alice_pulses_sent_info):
           bob_measurement = bob_measurements[i]
           
           # Check if bases match and detection occurred
           if (alice_pulse['chosen_basis'] == bob_measurement['chosen_basis'] and
               bob_measurement['click_occurred']):
               
               alice_sifted_key.append(alice_pulse['chosen_bit'])
               bob_sifted_key.append(bob_measurement['measured_bit'])
       
       return alice_sifted_key, bob_sifted_key
```

Usage Example
~~~~~~~~~~~~

.. code-block:: python

   # Create network
   network = Network()
   alice = network.add_node('Alice', avg_photon_number=0.2)
   bob = network.add_node('Bob', detector_efficiency=0.9, dark_count_rate=1e-7)
   network.connect_nodes('Alice', 'Bob', distance_km=20)

   # Generate key with BB84 protocol
   alice_key, bob_key = alice.generate_and_share_key_bb84(
       bob, num_pulses=10000, pulse_repetition_rate_ns=1, phase_flip_prob=0.05
   )

   # Analyze results
   qber, num_errors = calculate_qber(alice_key, bob_key)
   final_key_len, postproc = postprocessing(len(alice_key), qber)

   print(f"BB84-QKD Results:")
   print(f"QBER: {qber:.4f}")
   print(f"Sifted key length: {len(alice_key)}")
   print(f"Final key length: {final_key_len}")
```

Performance Characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Sifting Efficiency**: ~50% of raw bits
- **QBER Range**: 3-11% for practical systems
- **Key Rate**: Moderate due to basis reconciliation
- **Security**: Information-theoretic security
- **Hardware Requirements**: Polarization or phase encoding

Protocol Comparison
------------------

Performance Metrics
~~~~~~~~~~~~~~~~~~

| Protocol | Sifting Efficiency | QBER Range | Key Rate | Security Level | Hardware Complexity |
|----------|-------------------|------------|----------|----------------|-------------------|
| DPS-QKD  | ~25%              | 3-11%      | High     | High           | Low               |
| COW-QKD  | ~40%              | 3-10%      | High     | High           | Low               |
| BB84-QKD | ~50%              | 3-11%      | Moderate | Highest        | Medium            |

Use Case Recommendations
~~~~~~~~~~~~~~~~~~~~~~~

**DPS-QKD**:
- High-speed applications
- Simple hardware requirements
- Phase-stable environments
- Cost-sensitive deployments

**COW-QKD**:
- Security-critical applications
- Eavesdropping detection required
- Robust performance needed
- Monitoring capabilities desired

**BB84-QKD**:
- Maximum security requirements
- Research and development
- Educational purposes
- Standard QKD implementations

Implementation Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**DPS-QKD**:
- Requires phase stability
- Sensitive to phase noise
- Simple implementation
- High key rate potential

**COW-QKD**:
- Requires intensity control
- Monitoring pulse overhead
- Robust against attacks
- Built-in security features

**BB84-QKD**:
- Requires basis switching
- Basis reconciliation overhead
- Proven security
- Standard protocol

Future Protocol Extensions
-------------------------

The platform is designed to easily accommodate new QKD protocols:

1. **Protocol Interface**: Standard interface for new protocols
2. **Modular Design**: Separate sender/receiver implementations
3. **Parameter Configuration**: Flexible parameter system
4. **Analysis Integration**: Automatic QBER and key rate analysis

Adding a new protocol involves:

1. Implementing sender and receiver classes
2. Adding protocol-specific parameters
3. Integrating with the network model
4. Adding frontend support
5. Updating documentation 