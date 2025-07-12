Simulation Models
================

This section provides detailed documentation of the mathematical models, algorithms, and simulation methodologies used in the QKD Simulation Platform.

Overview
--------

The QKD Simulation Platform implements theory-compliant models of quantum key distribution protocols, optical components, and network behavior. The simulation follows a discrete-event approach with realistic modeling of quantum phenomena, optical hardware, and classical post-processing.

Quantum Models
-------------

Photon Statistics
~~~~~~~~~~~~~~~~~

The platform models weak coherent pulse (WCP) sources using Poissonian photon statistics:

.. math::

   P(n|\mu) = \frac{\mu^n e^{-\mu}}{n!}

where:
- :math:`P(n|\mu)` is the probability of :math:`n` photons given mean photon number :math:`\mu`
- :math:`\mu` is the average photon number per pulse (typically 0.1-0.5 for QKD)

Implementation in :class:`simulation.Hardware.LightSource`:

.. code-block:: python

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

Quantum State Representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

BB84 Protocol States
^^^^^^^^^^^^^^^^^^^

The BB84 protocol uses four quantum states in two conjugate bases:

**Rectilinear Basis (R)**:
- :math:`|0\rangle` = horizontal polarization
- :math:`|1\rangle` = vertical polarization

**Diagonal Basis (D)**:
- :math:`|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)`
- :math:`|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)`

DPS Protocol States
^^^^^^^^^^^^^^^^^^

DPS-QKD encodes information in the phase difference between consecutive pulses:

- **Bit 0**: Phase difference :math:`\Delta\phi = 0`
- **Bit 1**: Phase difference :math:`\Delta\phi = \pi`

COW Protocol States
^^^^^^^^^^^^^^^^^^

COW-QKD uses intensity modulation with three pulse types:

- **Data Pulse 0**: Vacuum pulse (intensity :math:`I_0`)
- **Data Pulse 1**: Coherent pulse (intensity :math:`I_1`)
- **Monitoring Pulse**: Coherent pulse for eavesdropping detection

Optical Component Models
-----------------------

Optical Channel Model
~~~~~~~~~~~~~~~~~~~~

The optical fiber channel is modeled with distance-dependent attenuation:

.. math::

   T = 10^{-\alpha L/10}

where:
- :math:`T` is the transmission probability
- :math:`\alpha` is the attenuation coefficient (dB/km)
- :math:`L` is the fiber length (km)

Implementation in :class:`simulation.Hardware.OpticalChannel`:

.. code-block:: python

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

Single Photon Detector Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The single photon detector model includes quantum efficiency and dark counts:

**Quantum Efficiency**: Probability of detecting a photon given one incident
**Dark Counts**: Spurious detections in the absence of photons

Detection probability for :math:`n` incident photons:

.. math::

   P_{detect} = 1 - (1 - \eta)^n

where :math:`\eta` is the quantum efficiency.

Dark count probability in time window :math:`\Delta t`:

.. math::

   P_{dark} = 1 - e^{-r_{dark} \Delta t}

where :math:`r_{dark}` is the dark count rate.

Implementation in :class:`simulation.Hardware.SinglePhotonDetector`:

.. code-block:: python

   def detect(self, incident_photons):
       click = False
       
       # Real photon detection
       if incident_photons > 0:
           prob_actual_detection = 1 - (1 - self.quantum_efficiency)**incident_photons
           if random.random() < prob_actual_detection:
               click = True
       
       # Dark count
       if not click:
           if random.random() < self.prob_dark_count_per_window:
               click = True
               
       return click

Mach-Zehnder Interferometer Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The MZI model calculates interference probabilities for phase difference measurement:

.. math::

   P_{DM1} = \cos^2(\Delta\phi/2)
   P_{DM2} = \sin^2(\Delta\phi/2)

where :math:`\Delta\phi` is the phase difference between consecutive pulses.

Implementation in :class:`simulation.Hardware.MachZehnderInterferometer`:

.. code-block:: python

   def interfere_pulses(self, phase_n_minus_1, phase_n):
       delta_phi = (phase_n - phase_n_minus_1) % (2 * math.pi)
       
       # Normalize to [-pi, pi]
       if delta_phi > math.pi:
           delta_phi -= 2 * math.pi
       elif delta_phi < -math.pi:
           delta_phi += 2 * math.pi

       prob_dm1 = math.cos(delta_phi / 2)**2
       prob_dm2 = math.sin(delta_phi / 2)**2
       
       return prob_dm1, prob_dm2

Intensity Modulator Model
~~~~~~~~~~~~~~~~~~~~~~~~

The intensity modulator model includes finite extinction ratio:

.. math::

   I_{off} = \frac{I_{on}}{ER}

where:
- :math:`I_{on}` is the intensity in the "on" state
- :math:`I_{off}` is the intensity in the "off" state
- :math:`ER` is the extinction ratio (linear scale)

Implementation in :class:`simulation.Hardware.IntensityModulator`:

.. code-block:: python

   def modulate(self, base_mu, state):
       if state == 'on':
           return base_mu
       elif state == 'off':
           return base_mu / self.extinction_ratio_linear
       else:
           raise ValueError("Modulator state must be 'on' or 'off'")

Protocol-Specific Models
-----------------------

DPS-QKD Model
~~~~~~~~~~~~~

DPS-QKD Protocol Flow
^^^^^^^^^^^^^^^^^^^^

1. **Phase Encoding**: Alice encodes bits in phase differences between consecutive pulses
2. **Transmission**: Pulses are transmitted through the optical channel
3. **Interference**: Bob uses MZI to measure phase differences
4. **Detection**: Two detectors record interference patterns
5. **Sifting**: Alice and Bob publicly compare to establish shared key

Mathematical Model
^^^^^^^^^^^^^^^^^

**Phase Encoding**:
- Random bit :math:`b \in \{0,1\}`
- Phase difference :math:`\Delta\phi = b \cdot \pi`

**Interference Measurement**:
- Detector 1 click probability: :math:`P_1 = \cos^2(\Delta\phi/2)`
- Detector 2 click probability: :math:`P_2 = \sin^2(\Delta\phi/2)`

**Bit Inference**:
- DM1 click only: :math:`b_{inferred} = 0`
- DM2 click only: :math:`b_{inferred} = 1`
- Both or neither click: inconclusive measurement

COW-QKD Model
~~~~~~~~~~~~~

COW-QKD Protocol Flow
^^^^^^^^^^^^^^^^^^^^

1. **Pulse Train Generation**: Alice generates data and monitoring pulses
2. **Intensity Modulation**: Data bits encoded in pulse intensity
3. **Transmission**: Pulse train transmitted through channel
4. **Detection**: Bob measures pulse intensities
5. **Sifting**: Keep bits where Alice and Bob agree on data pulses
6. **Monitoring**: Check monitoring pulses for eavesdropping

Mathematical Model
^^^^^^^^^^^^^^^^^

**Pulse Types**:
- Data pulse 0: :math:`I_0 = \mu_{off}`
- Data pulse 1: :math:`I_1 = \mu_{on}`
- Monitoring pulse: :math:`I_m = \mu_{on}`

**Detection Model**:
- Click probability: :math:`P_{click} = 1 - e^{-\eta I}`
- Where :math:`\eta` is detector efficiency and :math:`I` is intensity

**Sifting Process**:
- Keep bit if both Alice and Bob identify pulse as data
- Discard if either identifies as monitoring

BB84-QKD Model
~~~~~~~~~~~~~~

BB84-QKD Protocol Flow
^^^^^^^^^^^^^^^^^^^^^

1. **State Preparation**: Alice prepares one of four quantum states
2. **Basis Selection**: Alice randomly chooses encoding basis
3. **Transmission**: Quantum state transmitted through channel
4. **Measurement**: Bob randomly chooses measurement basis
5. **Sifting**: Keep bits where Alice and Bob used same basis
6. **Error Estimation**: Estimate QBER from disclosed bits

Mathematical Model
^^^^^^^^^^^^^^^^^

**State Preparation**:
- Random bit :math:`b \in \{0,1\}`
- Random basis :math:`B \in \{R,D\}`
- State: :math:`|\psi\rangle = |b\rangle_B`

**Measurement**:
- Random basis choice :math:`B' \in \{R,D\}`
- Measurement outcome: :math:`b' \in \{0,1\}` or no detection

**Sifting**:
- Keep bit if :math:`B = B'` and detection occurred
- Discard if :math:`B \neq B'` or no detection

Noise Models
-----------

Phase Flip Noise
~~~~~~~~~~~~~~~

Models phase errors in the optical channel:

.. math::

   P_{phase\_flip} = p_{flip}

Implementation:

.. code-block:: python

   if random.random() < phase_flip_prob:
       modulated_phase = (modulated_phase + math.pi) % (2 * math.pi)
```

Bit Flip Noise
~~~~~~~~~~~~~

Models bit errors in classical post-processing:

.. math::

   P_{bit\_flip} = p_{error}

Implementation:

.. code-block:: python

   if random.random() < bit_flip_error_prob:
       bit = 1 - bit  # Flip the bit
```

Channel Attenuation
~~~~~~~~~~~~~~~~~~

Models photon loss in optical fiber:

.. math::

   P_{survival} = 10^{-\alpha L/10}

where :math:`\alpha` is attenuation coefficient and :math:`L` is distance.

Dark Counts
~~~~~~~~~~

Models spurious detector clicks:

.. math::

   P_{dark} = 1 - e^{-r_{dark} \Delta t}

where :math:`r_{dark}` is dark count rate and :math:`\Delta t` is time window.

Performance Analysis Models
--------------------------

QBER Calculation
~~~~~~~~~~~~~~~

Quantum Bit Error Rate is calculated using a random sample:

.. math::

   QBER = \frac{N_{errors}}{N_{sample}}

where:
- :math:`N_{errors}` is the number of bit errors
- :math:`N_{sample}` is the sample size (typically 10% of key)

Implementation in :func:`main.calculate_qber`:

.. code-block:: python

   def calculate_qber(alice_sifted_key, bob_sifted_key, dr=0.10, seed=None):
       key_length = len(alice_sifted_key)
       sample_size = max(1, int(dr * key_length))
       indices = list(range(key_length))
       if seed is not None:
           random.seed(seed)
       sample_indices = random.sample(indices, sample_size)

       num_errors = 0
       for idx in sample_indices:
           if alice_sifted_key[idx] != bob_sifted_key[idx]:
               num_errors += 1

       qber = num_errors / sample_size
       return qber, num_errors
```

Post-Processing Model
~~~~~~~~~~~~~~~~~~~~

The post-processing model includes three steps:

1. **Parameter Estimation**:
   .. math::
      N_{est} = N_{raw} \cdot (1 - DR)

2. **Error Correction**:
   .. math::
      N_{ec} = N_{est} \cdot (1 - f_{ec} \cdot h(QBER))

3. **Privacy Amplification**:
   .. math::
      N_{final} = N_{ec} \cdot (1 - PA_{ratio})

where:
- :math:`DR` is the disclose rate
- :math:`f_{ec}` is the error correction efficiency
- :math:`h(x)` is the binary entropy function
- :math:`PA_{ratio}` is the privacy amplification ratio

Implementation in :func:`main.postprocessing`:

.. code-block:: python

   def postprocessing(raw_key_length, qber, dr=0.10, error_correction_efficiency=1.2, privacy_amplification_ratio=0.5):
       # Parameter estimation
       key_after_dr = raw_key_length * (1 - dr)
       
       # Error correction
       def binary_entropy(x):
           if x == 0 or x == 1:
               return 0.0
           return -x * log2(x) - (1 - x) * log2(1 - x)
       
       ec_fraction = error_correction_efficiency * binary_entropy(qber)
       key_after_ec = key_after_dr * (1 - ec_fraction)
       
       # Privacy amplification
       key_after_pa = key_after_ec * (1 - privacy_amplification_ratio)
       
       final_key_length = max(0, int(key_after_pa))
       
       return final_key_length, {
           'after_parameter_estimation': int(key_after_dr),
           'after_error_correction': int(key_after_ec),
           'after_privacy_amplification': int(key_after_pa),
           'dr': dr,
           'ec_fraction': ec_fraction,
           'privacy_amplification_ratio': privacy_amplification_ratio
       }
```

Key Rate Analysis
~~~~~~~~~~~~~~~~

Secure key rate calculation:

.. math::

   R_{secure} = \frac{N_{final}}{T_{total}}

where:
- :math:`N_{final}` is the final key length
- :math:`T_{total}` is the total simulation time

Raw key rate:

.. math::

   R_{raw} = \frac{N_{sifted}}{T_{total}}

where :math:`N_{sifted}` is the sifted key length.

Network Models
-------------

Trusted Relay Model
~~~~~~~~~~~~~~~~~~

For multi-node networks, the platform implements a trusted relay model:

1. **Key Generation**: Generate keys on each link independently
2. **Key Relay**: Trusted nodes relay keys using classical communication
3. **Key Combination**: Final key is the XOR of all link keys

Mathematical Model:
- Link :math:`i` generates key :math:`K_i`
- Final key: :math:`K_{final} = K_1 \oplus K_2 \oplus ... \oplus K_n`

Implementation in :class:`simulation.Network.Network`:

.. code-block:: python

   def establish_end_to_end_raw_key(self, sender_id, receiver_id, path_nodes, num_pulses, pulse_repetition_rate_ns):
       # Generate keys on each link
       link_keys = []
       for i in range(len(path_nodes) - 1):
           node1 = self.nodes[path_nodes[i]]
           node2 = self.nodes[path_nodes[i+1]]
           key1, key2 = node1.generate_and_share_key(node2, num_pulses, pulse_repetition_rate_ns)
           link_keys.append(key1)
       
       # XOR all link keys
       final_key = link_keys[0]
       for key in link_keys[1:]:
           final_key = [a ^ b for a, b in zip(final_key, key)]
       
       return final_key
```

Simulation Algorithm
-------------------

Discrete Event Simulation
~~~~~~~~~~~~~~~~~~~~~~~~

The platform uses a discrete event simulation approach:

1. **Event Generation**: Generate pulse events at regular intervals
2. **Event Processing**: Process each event through the simulation pipeline
3. **State Updates**: Update system state based on event outcomes
4. **Data Collection**: Collect statistics and results

Simulation Pipeline
~~~~~~~~~~~~~~~~~~

For each protocol, the simulation follows this pipeline:

**DPS-QKD Pipeline**:
1. Generate pulse train with random phases
2. Apply phase encoding based on random bits
3. Transmit through optical channel
4. Apply phase flip noise
5. Measure with MZI
6. Record detector clicks
7. Perform sifting process

**COW-QKD Pipeline**:
1. Generate pulse train with data and monitoring pulses
2. Apply intensity modulation
3. Transmit through optical channel
4. Detect pulses with single photon detector
5. Perform sifting based on pulse types
6. Check monitoring pulses for eavesdropping

**BB84-QKD Pipeline**:
1. Generate random bits and bases
2. Prepare quantum states
3. Transmit through optical channel
4. Randomly choose measurement bases
5. Perform measurements
6. Sift based on basis agreement

Random Number Generation
~~~~~~~~~~~~~~~~~~~~~~~

The simulation uses Python's `random` module for random number generation:

- **Reproducibility**: Seeds can be set for reproducible results
- **Quality**: Uses Mersenne Twister algorithm
- **Independence**: Different random streams for different components

Implementation:

.. code-block:: python

   import random
   import math

   # Set seed for reproducibility
   random.seed(42)

   # Generate random bits
   bit = random.randint(0, 1)

   # Generate random phases
   phase = random.uniform(0, 2 * math.pi)

   # Generate random bases
   basis = random.choice(['R', 'D'])
```

Validation and Verification
--------------------------

Theory Compliance
~~~~~~~~~~~~~~~~~

The simulation models are validated against theoretical predictions:

**DPS-QKD**:
- Expected sifting efficiency: ~25%
- QBER range: 3-11% for practical systems

**COW-QKD**:
- Expected sifting efficiency: ~40%
- QBER range: 3-10% for practical systems

**BB84-QKD**:
- Expected sifting efficiency: ~50%
- QBER range: 3-11% for practical systems

Implementation Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~

Key verification checks:

1. **Photon Conservation**: Total photons in = total photons out + losses
2. **Probability Normalization**: All probabilities sum to 1
3. **Phase Continuity**: Phase values are properly wrapped to [0, 2π]
4. **Bit Consistency**: Alice and Bob keys have same length after sifting

Error Handling
~~~~~~~~~~~~~

The simulation includes comprehensive error handling:

- **Parameter Validation**: All parameters checked for valid ranges
- **State Consistency**: System state verified at each step
- **Exception Handling**: Graceful handling of simulation errors
- **Logging**: Detailed logging for debugging and analysis

Performance Optimization
-----------------------

Computational Efficiency
~~~~~~~~~~~~~~~~~~~~~~~

The simulation is optimized for performance:

1. **Vectorized Operations**: Use NumPy for large arrays when possible
2. **Memory Management**: Efficient memory usage for large simulations
3. **Parallel Processing**: Support for parallel simulation runs
4. **Caching**: Cache frequently used calculations

Scalability
~~~~~~~~~~~

The platform scales to large networks:

- **Node Count**: Support for hundreds of nodes
- **Channel Count**: Support for thousands of channels
- **Pulse Count**: Support for millions of pulses
- **Memory Usage**: Efficient memory usage for large simulations

Accuracy Considerations
----------------------

Numerical Precision
~~~~~~~~~~~~~~~~~~

The simulation uses double-precision floating-point arithmetic:

- **Phase Calculations**: 64-bit precision for phase values
- **Probability Calculations**: 64-bit precision for probabilities
- **Statistical Accuracy**: Sufficient precision for QKD analysis

Approximations
~~~~~~~~~~~~~

The simulation makes several approximations for computational efficiency:

1. **Poissonian Photons**: Approximates true quantum statistics
2. **Classical Interference**: Approximates quantum interference
3. **Independent Events**: Assumes independence between pulses
4. **Markovian Process**: Assumes memoryless channel behavior

These approximations are valid for typical QKD parameters and provide accurate results for practical analysis.

Future Enhancements
-------------------

Planned improvements to the simulation models:

1. **Full Quantum Simulation**: Implementation of true quantum state evolution
2. **Advanced Noise Models**: More sophisticated noise and decoherence models
3. **Security Analysis**: Integration of security analysis tools
4. **Real-time Simulation**: Real-time simulation capabilities
5. **Hardware Integration**: Integration with real QKD hardware 