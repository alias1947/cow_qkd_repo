QKD Simulation Platform Documentation
====================================

Welcome to the Quantum Key Distribution (QKD) Simulation Platform documentation. This platform provides a comprehensive simulation environment for studying and analyzing various QKD protocols including DPS-QKD, COW-QKD, and BB84-QKD.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   quick-start
   user-guide
   api-reference
   simulation-models
   protocols
   hardware-models
   network-architecture
   frontend-guide
   examples
   contributing
   troubleshooting

Overview
--------

The QKD Simulation Platform is an open-source project that enables researchers, engineers, and students to simulate and analyze quantum key distribution protocols in realistic network environments. The platform consists of:

* **Backend Simulation Engine**: Python-based simulation core with modular architecture
* **Web-based Frontend**: React-based user interface for network configuration and visualization
* **REST API**: FastAPI-based interface for programmatic access
* **Multi-Protocol Support**: DPS-QKD, COW-QKD, and BB84-QKD implementations
* **Network Simulation**: Multi-node, multi-channel network configurations
* **Hardware Modeling**: Realistic optical components and channel models

Key Features
-----------

* **Protocol Diversity**: Support for three major QKD protocols with theory-compliant implementations
* **Network Scalability**: From point-to-point to multi-node trusted relay networks
* **Realistic Modeling**: Hardware components with realistic parameters and noise models
* **Interactive Interface**: Visual network topology builder and parameter configuration
* **Comprehensive Analysis**: QBER calculation, key rate analysis, and post-processing simulation
* **Extensible Architecture**: Modular design for easy protocol and hardware additions

Supported QKD Protocols
-----------------------

* **DPS-QKD (Differential Phase Shift)**: Phase difference encoding with Mach-Zehnder interferometer detection
* **COW-QKD (Coherent One-Way)**: Intensity modulation with monitoring pulse pairs for eavesdropping detection  
* **BB84-QKD (Bennett-Brassard 1984)**: Four quantum states in two bases with basis switching and sifting

Getting Started
--------------

* :doc:`installation` - How to install and set up the platform
* :doc:`quick-start` - Quick tutorial to run your first simulation
* :doc:`user-guide` - Comprehensive user guide for all features

For Developers
-------------

* :doc:`api-reference` - Complete API documentation
* :doc:`simulation-models` - Detailed simulation model descriptions
* :doc:`contributing` - How to contribute to the project

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

