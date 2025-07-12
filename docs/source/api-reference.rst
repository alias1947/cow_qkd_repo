API Reference
=============

This section provides comprehensive documentation for all classes, methods, and functions in the QKD Simulation Platform.

Core Classes
-----------

Network Management
~~~~~~~~~~~~~~~~~~

.. class:: simulation.Network.Network

   Main network management class that handles nodes, connections, and end-to-end key establishment.

   .. method:: __init__()

      Initialize an empty network.

   .. method:: add_node(node_id, avg_photon_number=0.2, detector_efficiency=0.9, dark_count_rate=1e-7, cow_monitor_pulse_ratio=0.1, cow_detection_threshold_photons=0, cow_extinction_ratio_db=20.0)

      Add a new node to the network.

      :param str node_id: Unique identifier for the node
      :param float avg_photon_number: Average photon number per pulse (0 < μ < 1)
      :param float detector_efficiency: Quantum efficiency of the detector (0-1)
      :param float dark_count_rate: Dark count rate per nanosecond
      :param float cow_monitor_pulse_ratio: COW monitoring pulse ratio (0-1)
      :param float cow_detection_threshold_photons: COW detection threshold in photons
      :param float cow_extinction_ratio_db: COW extinction ratio in dB
      :return: The created Node instance
      :rtype: :class:`simulation.Network.Node`

   .. method:: connect_nodes(node1_id, node2_id, distance_km, attenuation_db_per_km=0.2)

      Connect two nodes with an optical channel.

      :param str node1_id: ID of the first node
      :param str node2_id: ID of the second node
      :param float distance_km: Distance between nodes in kilometers
      :param float attenuation_db_per_km: Fiber attenuation in dB per kilometer

   .. method:: establish_end_to_end_raw_key(sender_id, receiver_id, path_nodes, num_pulses, pulse_repetition_rate_ns)

      Establish end-to-end raw sifted key through trusted relay nodes (DPS-QKD).

      :param str sender_id: ID of the sender node
      :param str receiver_id: ID of the receiver node
      :param list path_nodes: List of node IDs in the path from sender to receiver
      :param int num_pulses: Number of pulses to generate per link
      :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
      :return: Final end-to-end raw sifted key or None if failed
      :rtype: list or None

   .. method:: establish_end_to_end_raw_key_cow(sender_id, receiver_id, path_nodes, num_pulses, pulse_repetition_rate_ns, monitor_pulse_ratio=0.1, detection_threshold_photons=0)

      Establish end-to-end raw sifted key through trusted relay nodes (COW-QKD).

      :param str sender_id: ID of the sender node
      :param str receiver_id: ID of the receiver node
      :param list path_nodes: List of node IDs in the path from sender to receiver
      :param int num_pulses: Number of pulses to generate per link
      :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
      :param float monitor_pulse_ratio: COW monitoring pulse ratio
      :param float detection_threshold_photons: COW detection threshold
      :return: Final end-to-end raw sifted key or None if failed
      :rtype: list or None

   .. method:: establish_end_to_end_raw_key_bb84(sender_id, receiver_id, path_nodes, num_pulses, pulse_repetition_rate_ns)

      Establish end-to-end raw sifted key through trusted relay nodes (BB84-QKD).

      :param str sender_id: ID of the sender node
      :param str receiver_id: ID of the receiver node
      :param list path_nodes: List of node IDs in the path from sender to receiver
      :param int num_pulses: Number of pulses to generate per link
      :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
      :return: Final end-to-end raw sifted key or None if failed
      :rtype: list or None

.. class:: simulation.Network.Node

   Represents a network node that can act as sender, receiver, or trusted relay.

   .. method:: __init__(node_id, avg_photon_number=0.2, detector_efficiency=0.9, dark_count_rate=1e-7, cow_monitor_pulse_ratio=0.1, cow_detection_threshold_photons=0, cow_extinction_ratio_db=20.0)

      Initialize a node with protocol-specific components.

      :param str node_id: Unique identifier for the node
      :param float avg_photon_number: Average photon number per pulse
      :param float detector_efficiency: Quantum efficiency of the detector
      :param float dark_count_rate: Dark count rate per nanosecond
      :param float cow_monitor_pulse_ratio: COW monitoring pulse ratio
      :param float cow_detection_threshold_photons: COW detection threshold
      :param float cow_extinction_ratio_db: COW extinction ratio in dB

   .. method:: add_link(neighbor_node_id, channel_instance)

      Add an optical channel link to a neighbor node.

      :param str neighbor_node_id: ID of the neighbor node
      :param OpticalChannel channel_instance: Optical channel instance

   .. method:: generate_and_share_key(target_node, num_pulses, pulse_repetition_rate_ns, phase_flip_prob=0.0)

      Generate and share key using DPS-QKD protocol.

      :param Node target_node: Target node for key generation
      :param int num_pulses: Number of pulses to generate
      :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
      :param float phase_flip_prob: Probability of phase flip noise
      :return: Tuple of (alice_key, bob_key)
      :rtype: tuple

   .. method:: generate_and_share_key_cow(target_node, num_pulses, pulse_repetition_rate_ns, monitor_pulse_ratio=0.1, detection_threshold_photons=0, phase_flip_prob=0.0, bit_flip_error_prob=0.0)

      Generate and share key using COW-QKD protocol.

      :param Node target_node: Target node for key generation
      :param int num_pulses: Number of pulses to generate
      :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
      :param float monitor_pulse_ratio: COW monitoring pulse ratio
      :param float detection_threshold_photons: COW detection threshold
      :param float phase_flip_prob: Probability of phase flip noise
      :param float bit_flip_error_prob: Probability of bit flip error
      :return: Tuple of (alice_key, bob_key)
      :rtype: tuple

   .. method:: generate_and_share_key_bb84(target_node, num_pulses, pulse_repetition_rate_ns, phase_flip_prob=0.0)

      Generate and share key using BB84-QKD protocol.

      :param Node target_node: Target node for key generation
      :param int num_pulses: Number of pulses to generate
      :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
      :param float phase_flip_prob: Probability of phase flip noise
      :return: Tuple of (alice_key, bob_key)
      :rtype: tuple

   .. method:: get_raw_sifted_key_with_neighbor(neighbor_id)

      Get the raw sifted key shared with a specific neighbor.

      :param str neighbor_id: ID of the neighbor node
      :return: Raw sifted key or None if not found
      :rtype: list or None

   .. method:: relay_key_classically(sender_node_id, receiver_node_id, key_to_relay)

      Relay a key classically between two nodes (for trusted relay networks).

      :param str sender_node_id: ID of the sender node
      :param str receiver_node_id: ID of the receiver node
      :param list key_to_relay: Key to relay
      :return: Relayed key
      :rtype: list

Hardware Components
~~~~~~~~~~~~~~~~~~

.. class:: simulation.Hardware.LightSource

   Models a weak coherent pulse (WCP) light source with Poissonian photon statistics.

   .. method:: __init__(average_photon_number=0.2)

      Initialize the light source.

      :param float average_photon_number: Average photon number per pulse (0 < μ < 1)
      :raises ValueError: If average_photon_number is not between 0 and 1

   .. method:: generate_single_pulse_photon_count(mu=None)

      Generate photon count for a single pulse using Poissonian statistics.

      :param float mu: Average photon number (uses instance value if None)
      :return: Number of photons in the pulse
      :rtype: int

   .. method:: get_initial_phase()

      Get the initial phase of the light source.

      :return: Initial phase in radians
      :rtype: float

.. class:: simulation.Hardware.PhaseModulator

   Models a phase modulator for phase encoding in QKD protocols.

   .. method:: modulate_phase(current_phase, desired_phase_shift)

      Modulate the phase of an optical signal.

      :param float current_phase: Current phase in radians
      :param float desired_phase_shift: Desired phase shift in radians
      :return: New phase in radians (modulo 2π)
      :rtype: float

.. class:: simulation.Hardware.IntensityModulator

   Models an intensity modulator with finite extinction ratio.

   .. method:: __init__(extinction_ratio_db=20.0)

      Initialize the intensity modulator.

      :param float extinction_ratio_db: Extinction ratio in dB
      :raises ValueError: If extinction ratio is not positive

   .. method:: modulate(base_mu, state)

      Modulate the intensity of an optical signal.

      :param float base_mu: Base average photon number
      :param str state: Modulation state ('on' or 'off')
      :return: Modulated average photon number
      :rtype: float
      :raises ValueError: If state is not 'on' or 'off'

.. class:: simulation.Hardware.OpticalChannel

   Models an optical fiber channel with distance-dependent attenuation.

   .. method:: __init__(distance_km, attenuation_db_per_km=0.2)

      Initialize the optical channel.

      :param float distance_km: Distance in kilometers
      :param float attenuation_db_per_km: Attenuation in dB per kilometer

   .. method:: transmit_pulse(photon_count)

      Transmit a pulse through the channel.

      :param int photon_count: Number of photons to transmit
      :return: Number of photons received after transmission
      :rtype: int

.. class:: simulation.Hardware.MachZehnderInterferometer

   Models a Mach-Zehnder interferometer for phase difference measurement.

   .. method:: __init__(ideal_split_ratio=0.5)

      Initialize the Mach-Zehnder interferometer.

      :param float ideal_split_ratio: Ideal beam splitter ratio (default 0.5)

   .. method:: interfere_pulses(phase_n_minus_1, phase_n)

      Calculate interference probabilities for two consecutive pulses.

      :param float phase_n_minus_1: Phase of the previous pulse
      :param float phase_n: Phase of the current pulse
      :return: Tuple of (prob_dm1, prob_dm2) detection probabilities
      :rtype: tuple

.. class:: simulation.Hardware.SinglePhotonDetector

   Models a single-photon detector with quantum efficiency and dark counts.

   .. method:: __init__(quantum_efficiency=0.9, dark_count_rate_per_ns=1e-7, time_window_ns=1)

      Initialize the single-photon detector.

      :param float quantum_efficiency: Quantum efficiency (0-1)
      :param float dark_count_rate_per_ns: Dark count rate per nanosecond
      :param float time_window_ns: Detection time window in nanoseconds

   .. method:: detect(incident_photons)

      Simulate photon detection.

      :param int incident_photons: Number of incident photons
      :return: True if a click occurs, False otherwise
      :rtype: bool

.. class:: simulation.Hardware.SMF

   Models a single-mode fiber with configurable parameters.

   .. method:: __init__(length_km=20.0, attenuation_db_per_km=0.2, fiber_type="single_mode_fiber")

      Initialize the fiber.

      :param float length_km: Fiber length in kilometers
      :param float attenuation_db_per_km: Attenuation in dB per kilometer
      :param str fiber_type: Type of fiber

   .. method:: total_attenuation_db()

      Calculate total attenuation in dB.

      :return: Total attenuation in dB
      :rtype: float

   .. method:: transmission_probability()

      Calculate photon transmission probability.

      :return: Transmission probability (0-1)
      :rtype: float

Protocol Implementations
~~~~~~~~~~~~~~~~~~~~~~~

DPS-QKD Sender
^^^^^^^^^^^^^

.. class:: simulation.Sender.SenderDPS

   Implements the sender side of DPS-QKD protocol.

   .. method:: __init__(avg_photon_number=0.2)

      Initialize the DPS sender.

      :param float avg_photon_number: Average photon number per pulse

   .. method:: prepare_and_send_pulse(time_slot)

      Prepare and send a single pulse with phase encoding.

      :param float time_slot: Time slot for the pulse
      :return: Tuple of (modulated_phase, photon_count)
      :rtype: tuple

   .. method:: get_pulse_info(time_slot)

      Get information about a sent pulse.

      :param float time_slot: Time slot of the pulse
      :return: Pulse information dictionary or None
      :rtype: dict or None

COW-QKD Sender
^^^^^^^^^^^^^

.. class:: simulation.Sender.SenderCOW

   Implements the sender side of COW-QKD protocol.

   .. method:: __init__(avg_photon_number=0.2, monitor_pulse_ratio=0.1, extinction_ratio_db=20.0)

      Initialize the COW sender.

      :param float avg_photon_number: Average photon number per pulse
      :param float monitor_pulse_ratio: Ratio of monitoring pulses
      :param float extinction_ratio_db: Extinction ratio in dB
      :raises ValueError: If avg_photon_number is not between 0 and 1

   .. method:: prepare_pulse_train(num_total_pulses)

      Prepare a complete pulse train with data and monitoring pulses.

      :param int num_total_pulses: Total number of pulses to generate
      :return: List of pulse information dictionaries
      :rtype: list

   .. method:: get_sent_pulse_info(time_slot)

      Get information about a sent pulse.

      :param float time_slot: Time slot of the pulse
      :return: Pulse information dictionary or None
      :rtype: dict or None

   .. method:: get_intended_key_bits()

      Get the intended key bits for data pulses.

      :return: List of intended key bits
      :rtype: list

BB84-QKD Sender
^^^^^^^^^^^^^^

.. class:: simulation.Sender.SenderBB84

   Implements the sender side of BB84-QKD protocol.

   .. method:: __init__(avg_photon_number=0.2)

      Initialize the BB84 sender.

      :param float avg_photon_number: Average photon number per pulse
      :raises ValueError: If avg_photon_number is not between 0 and 1

   .. method:: prepare_and_send_pulse(time_slot)

      Prepare and send a single pulse with basis and bit encoding.

      :param float time_slot: Time slot for the pulse
      :return: Tuple of (encoded_state, photon_count, chosen_bit, chosen_basis)
      :rtype: tuple

   .. method:: get_pulse_info(time_slot)

      Get information about a sent pulse.

      :param float time_slot: Time slot of the pulse
      :return: Pulse information dictionary or None
      :rtype: dict or None

   .. method:: get_raw_key_bits()

      Get the raw key bits.

      :return: List of raw key bits
      :rtype: list

   .. method:: get_chosen_bases()

      Get the chosen measurement bases.

      :return: List of chosen bases
      :rtype: list

DPS-QKD Receiver
^^^^^^^^^^^^^^^

.. class:: simulation.Receiver.ReceiverDPS

   Implements the receiver side of DPS-QKD protocol.

   .. method:: __init__(detector_efficiency=0.9, dark_count_rate=1e-7)

      Initialize the DPS receiver.

      :param float detector_efficiency: Quantum efficiency of detectors
      :param float dark_count_rate: Dark count rate per nanosecond

   .. method:: receive_and_measure(time_slot, current_pulse_photons, current_pulse_phase, previous_pulse_photons, previous_pulse_phase)

      Receive and measure a pulse using Mach-Zehnder interferometer.

      :param float time_slot: Time slot of the pulse
      :param int current_pulse_photons: Photons in current pulse
      :param float current_pulse_phase: Phase of current pulse
      :param int previous_pulse_photons: Photons in previous pulse
      :param float previous_pulse_phase: Phase of previous pulse
      :return: Tuple of (click_dm1, click_dm2, measured_phase_diff, bob_bit)
      :rtype: tuple

COW-QKD Receiver
^^^^^^^^^^^^^^^

.. class:: simulation.Receiver.ReceiverCOW

   Implements the receiver side of COW-QKD protocol.

   .. method:: __init__(detector_efficiency=0.9, dark_count_rate=1e-7, detection_threshold_photons=0)

      Initialize the COW receiver.

      :param float detector_efficiency: Quantum efficiency of detector
      :param float dark_count_rate: Dark count rate per nanosecond
      :param float detection_threshold_photons: Detection threshold in photons

   .. method:: measure_pulse(time_slot, incident_photons, pulse_type)

      Measure a received pulse.

      :param float time_slot: Time slot of the pulse
      :param int incident_photons: Number of incident photons
      :param str pulse_type: Type of pulse ('data_first', 'data_second', 'monitor_first', 'monitor_second')
      :return: Tuple of (click, bob_inferred_bit, is_monitoring_click)
      :rtype: tuple

   .. method:: get_received_pulse_info(time_slot)

      Get information about a received pulse.

      :param float time_slot: Time slot of the pulse
      :return: Pulse information dictionary or None
      :rtype: dict or None

   .. method:: get_all_received_info()

      Get all received pulse information.

      :return: List of all received pulse information
      :rtype: list

BB84-QKD Receiver
^^^^^^^^^^^^^^^^

.. class:: simulation.Receiver.ReceiverBB84

   Implements the receiver side of BB84-QKD protocol.

   .. method:: __init__(detector_efficiency=0.9, dark_count_rate=1e-7)

      Initialize the BB84 receiver.

      :param float detector_efficiency: Quantum efficiency of detector
      :param float dark_count_rate: Dark count rate per nanosecond

   .. method:: receive_and_measure(time_slot, incident_photons, encoded_state)

      Receive and measure a pulse in a randomly chosen basis.

      :param float time_slot: Time slot of the pulse
      :param int incident_photons: Number of incident photons
      :param str encoded_state: Encoded quantum state
      :return: Tuple of (measured_bit, chosen_basis, click_occurred)
      :rtype: tuple

   .. method:: get_measurement_info(time_slot)

      Get information about a measurement.

      :param float time_slot: Time slot of the measurement
      :return: Measurement information dictionary or None
      :rtype: dict or None

   .. method:: get_raw_measurements()

      Get all raw measurement results.

      :return: List of raw measurements
      :rtype: list

   .. method:: get_chosen_bases()

      Get all chosen measurement bases.

      :return: List of chosen bases
      :rtype: list

Analysis Functions
~~~~~~~~~~~~~~~~~

.. function:: main.calculate_qber(alice_sifted_key, bob_sifted_key, dr=0.10, seed=None)

   Calculate the Quantum Bit Error Rate (QBER) using a random sample.

   :param list alice_sifted_key: Alice's sifted key
   :param list bob_sifted_key: Bob's sifted key
   :param float dr: Disclose rate for QBER estimation (0-1)
   :param int seed: Random seed for reproducible results
   :return: Tuple of (qber, num_errors)
   :rtype: tuple
   :raises ValueError: If keys have different lengths

.. function:: main.postprocessing(raw_key_length, qber, dr=0.10, error_correction_efficiency=1.2, privacy_amplification_ratio=0.5)

   Simulate QKD post-processing steps.

   :param int raw_key_length: Length of raw sifted key
   :param float qber: Quantum Bit Error Rate
   :param float dr: Disclose rate for parameter estimation
   :param float error_correction_efficiency: Error correction efficiency factor
   :param float privacy_amplification_ratio: Privacy amplification compression ratio
   :return: Tuple of (final_key_length, postprocessing_breakdown)
   :rtype: tuple

Simulation Functions
~~~~~~~~~~~~~~~~~~~

.. function:: main.run_point_to_point_simulation(num_pulses_per_link=10000, distance_km=20, mu=0.2, detector_efficiency=0.9, dark_count_rate_per_ns=1e-7, pulse_repetition_rate_ns=1)

   Run a point-to-point QKD simulation.

   :param int num_pulses_per_link: Number of pulses per link
   :param float distance_km: Distance between nodes in kilometers
   :param float mu: Average photon number per pulse
   :param float detector_efficiency: Quantum efficiency of detector
   :param float dark_count_rate_per_ns: Dark count rate per nanosecond
   :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
   :return: Tuple of (final_key_length, qber)
   :rtype: tuple

.. function:: main.run_multi_node_trusted_relay_simulation(num_pulses_per_link=10000, link_distance_km=10, num_relays=1, mu=0.2, detector_efficiency=0.9, dark_count_rate_per_ns=1e-7, pulse_repetition_rate_ns=1)

   Run a multi-node trusted relay QKD simulation.

   :param int num_pulses_per_link: Number of pulses per link
   :param float link_distance_km: Distance per link in kilometers
   :param int num_relays: Number of relay nodes
   :param float mu: Average photon number per pulse
   :param float detector_efficiency: Quantum efficiency of detector
   :param float dark_count_rate_per_ns: Dark count rate per nanosecond
   :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
   :return: Final end-to-end raw sifted key
   :rtype: list or None

.. function:: main.run_point_to_point_cow_simulation(num_pulses_per_link=10000, distance_km=20, mu=0.1, detector_efficiency=0.9, dark_count_rate_per_ns=1e-7, pulse_repetition_rate_ns=1, cow_monitor_pulse_ratio=0.1, cow_detection_threshold_photons=0, cow_extinction_ratio_db=20.0, bit_flip_error_prob=0.05)

   Run a point-to-point COW-QKD simulation.

   :param int num_pulses_per_link: Number of pulses per link
   :param float distance_km: Distance between nodes in kilometers
   :param float mu: Average photon number per pulse
   :param float detector_efficiency: Quantum efficiency of detector
   :param float dark_count_rate_per_ns: Dark count rate per nanosecond
   :param float pulse_repetition_rate_ns: Pulse repetition rate in nanoseconds
   :param float cow_monitor_pulse_ratio: COW monitoring pulse ratio
   :param float cow_detection_threshold_photons: COW detection threshold
   :param float cow_extinction_ratio_db: COW extinction ratio in dB
   :param float bit_flip_error_prob: Bit flip error probability
   :return: Tuple of (final_key_length, qber)
   :rtype: tuple

REST API
--------

The platform provides a REST API for programmatic access to simulations.

Base URL
~~~~~~~~

* **Development**: `http://127.0.0.1:8000`
* **Production**: Configure as needed

Endpoints
~~~~~~~~~

.. http:get:: /

   Get API information and status.

   **Response**:
   
   .. sourcecode:: json

      {
        "message": "QKD Simulation API"
      }

.. http:post:: /simulate

   Run a QKD simulation with specified parameters.

   **Request Body**:
   
   .. sourcecode:: json

      {
        "protocol": "dps",
        "nodes": [
          {
            "id": 1,
            "detector_efficiency": 0.9,
            "dark_count_rate": 1e-8,
            "mu": 0.2,
            "num_pulses": 10000,
            "pulse_repetition_rate": 1
          }
        ],
        "channels": [
          {
            "id": 1,
            "from": 1,
            "to": 2,
            "fiber_length_km": 20,
            "fiber_attenuation_db_per_km": 0.2,
            "wavelength_nm": 1550,
            "fiber_type": "standard_single_mode",
            "phase_flip_prob": 0.05
          }
        ],
        "cow_monitor_pulse_ratio": 0.1,
        "cow_detection_threshold_photons": 0,
        "cow_extinction_ratio_db": 20.0,
        "bit_flip_error_prob": 0.05
      }

   **Response**:
   
   .. sourcecode:: json

      [
        {
          "channel_id": 1,
          "from": 1,
          "to": 2,
          "protocol": "dps",
          "qber": 0.045,
          "final_key_length": 2345,
          "secure_key_rate_bps": 2345.0,
          "sifted_key_length": 2500,
          "num_errors": 112,
          "postprocessing": {
            "after_parameter_estimation": 2250,
            "after_error_correction": 2345,
            "after_privacy_amplification": 2345
          },
          "theory_compliance": true,
          "theory_message": "QBER is within the practical range (3-11%) for QKD.",
          "alice_key": [0, 1, 0, ...],
          "bob_key": [0, 1, 0, ...],
          "parameters": {
            "node_a": {...},
            "node_b": {...},
            "channel": {...}
          }
        }
      ]

Data Models
-----------

.. class:: api.NodeModel

   Pydantic model for node configuration.

   .. attribute:: id

      Node identifier (int)

   .. attribute:: detector_efficiency

      Quantum efficiency of detector (float, 0-1)

   .. attribute:: dark_count_rate

      Dark count rate per nanosecond (float)

   .. attribute:: mu

      Average photon number per pulse (float, 0-1)

   .. attribute:: num_pulses

      Number of pulses to generate (int)

   .. attribute:: pulse_repetition_rate

      Pulse repetition rate in nanoseconds (float)

.. class:: api.ChannelModel

   Pydantic model for channel configuration.

   .. attribute:: id

      Channel identifier (int)

   .. attribute:: from_

      Source node ID (int, alias 'from')

   .. attribute:: to

      Destination node ID (int)

   .. attribute:: fiber_length_km

      Fiber length in kilometers (float)

   .. attribute:: fiber_attenuation_db_per_km

      Fiber attenuation in dB per kilometer (float)

   .. attribute:: wavelength_nm

      Operating wavelength in nanometers (int)

   .. attribute:: fiber_type

      Type of fiber (str)

   .. attribute:: phase_flip_prob

      Probability of phase flip noise (float, 0-1, default 0.05)

.. class:: api.SimParams

   Pydantic model for simulation parameters.

   .. attribute:: protocol

      QKD protocol to use (str: "dps", "cow", or "bb84")

   .. attribute:: nodes

      List of node configurations (List[NodeModel])

   .. attribute:: channels

      List of channel configurations (List[ChannelModel])

   .. attribute:: cow_monitor_pulse_ratio

      COW monitoring pulse ratio (float, 0-1)

   .. attribute:: cow_detection_threshold_photons

      COW detection threshold in photons (float)

   .. attribute:: cow_extinction_ratio_db

      COW extinction ratio in dB (float)

   .. attribute:: bit_flip_error_prob

      Bit flip error probability (float, 0-1, default 0.05)

Error Handling
-------------

The API uses standard HTTP status codes:

* **200 OK**: Successful simulation
* **400 Bad Request**: Invalid parameters
* **422 Unprocessable Entity**: Validation errors
* **500 Internal Server Error**: Simulation errors

Error responses include detailed error messages:

.. sourcecode:: json

   {
     "detail": "Error message describing the issue"
   }

CORS Support
-----------

The API includes CORS middleware to support web frontend integration:

* **Allowed Origins**: `http://localhost:3000`, `http://localhost:3001`
* **Allowed Methods**: All HTTP methods
* **Allowed Headers**: All headers
* **Credentials**: Supported

Frontend Components
------------------

React Components
~~~~~~~~~~~~~~~

.. class:: QKDForm

   Protocol selection and parameter configuration component.

   **Props**:
   
   * `params` (object): Current simulation parameters
   * `onChange` (function): Callback for parameter changes

   **Features**:
   
   * Protocol selection (DPS, COW, BB84)
   * Protocol-specific parameter configuration
   * Real-time parameter validation

.. class:: QKDNetwork

   Interactive network topology builder component.

   **Props**:
   
   * `onNetworkChange` (function): Callback for network changes

   **Features**:
   
   * Drag-and-drop node placement
   * Visual channel connections
   * Node and channel parameter editing
   * Undo/redo functionality
   * Network topology export/import

.. class:: Results

   Simulation results display and analysis component.

   **Props**:
   
   * `results` (array): Simulation results
   * `loading` (boolean): Loading state

   **Features**:
   
   * Per-channel result display
   * QBER visualization
   * Key rate analysis
   * Theory compliance warnings
   * Detailed parameter breakdown

Configuration
------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

* `QKD_API_HOST`: API host address (default: "127.0.0.1")
* `QKD_API_PORT`: API port (default: 8000)
* `QKD_FRONTEND_PORT`: Frontend port (default: 3000)
* `QKD_LOG_LEVEL`: Logging level (default: "INFO")

Configuration Files
~~~~~~~~~~~~~~~~~~

* `requirements.txt`: Python dependencies
* `package.json`: Node.js dependencies
* `conf.py`: Sphinx documentation configuration

Performance Considerations
-------------------------

* **Memory Usage**: Large simulations may require significant memory
* **CPU Usage**: Multi-core processing for parallel simulations
* **Network I/O**: API calls for real-time simulation control
* **Storage**: Results caching and logging

Security Considerations
----------------------

* **Input Validation**: All parameters are validated before processing
* **Error Handling**: Comprehensive error handling prevents information leakage
* **CORS**: Proper CORS configuration for web integration
* **Rate Limiting**: Consider implementing rate limiting for production use 