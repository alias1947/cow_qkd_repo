User Guide
==========

This comprehensive user guide covers all features and functionality of the QKD Simulation Platform.

Getting Started
--------------

After completing the :doc:`quick-start` tutorial, you should be familiar with the basic workflow. This guide will explore all features in detail.

Platform Overview
----------------

The QKD Simulation Platform consists of three main components:

1. **Web Frontend**: Interactive user interface for network configuration and simulation
2. **Backend API**: FastAPI server that handles simulation requests
3. **Simulation Engine**: Python-based simulation core with protocol implementations

Interface Layout
---------------

The main interface is divided into several sections:

.. figure:: _static/interface-layout.png
   :alt: QKD Simulation Platform Interface Layout
   :align: center
   :width: 80%

   Main interface layout showing protocol selection, network builder, and results

Protocol Selection
-----------------

Protocol Configuration
~~~~~~~~~~~~~~~~~~~~~

The protocol selection area allows you to choose between three QKD protocols:

**DPS-QKD (Differential Phase Shift)**:
- **Best for**: High-speed applications, simple hardware
- **Key features**: Phase difference encoding, Mach-Zehnder interferometer
- **Parameters**: Standard QKD parameters only

**COW-QKD (Coherent One-Way)**:
- **Best for**: Security-critical applications, eavesdropping detection
- **Key features**: Intensity modulation, monitoring pulses
- **Parameters**: Additional COW-specific parameters

**BB84-QKD (Bennett-Brassard 1984)**:
- **Best for**: Research, education, maximum security
- **Key features**: Four quantum states, two bases, information-theoretic security
- **Parameters**: Standard QKD parameters only

Protocol-Specific Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

COW-QKD includes additional parameters not available in other protocols:

**Monitor Pulse Ratio** (0.0 - 1.0):
- **What it is**: Fraction of pulses used for eavesdropping detection
- **Default**: 0.1 (10%)
- **Effect**: Higher values improve security but reduce key rate
- **Recommendation**: 0.1 for most applications

**Detection Threshold (Photons)**:
- **What it is**: Minimum photon count for detection
- **Default**: 0 (single photon detection)
- **Effect**: Higher values reduce sensitivity but improve noise immunity
- **Recommendation**: 0 for most applications

**Extinction Ratio (dB)**:
- **What it is**: Ratio between "on" and "off" states of intensity modulator
- **Default**: 20 dB
- **Effect**: Higher values improve contrast between states
- **Recommendation**: 20-30 dB for practical systems

**Bit Flip Error Probability** (0.0 - 1.0):
- **What it is**: Probability of bit errors in classical post-processing
- **Default**: 0.05 (5%)
- **Effect**: Higher values increase QBER
- **Recommendation**: 0.01-0.05 for realistic systems

Network Builder
--------------

The network builder provides a visual interface for creating and configuring QKD networks.

Node Management
~~~~~~~~~~~~~~~

**Adding Nodes**:
- Click the "Add Node" button to create a new node
- Nodes are automatically numbered and positioned
- You can add up to 50 nodes (practical limit)

**Node Positioning**:
- Drag nodes to reposition them
- Nodes snap to a grid for neat layouts
- Position nodes logically (e.g., in a chain or star topology)

**Node Selection**:
- Click on a node to select it
- Selected node appears highlighted
- Node parameters appear in the sidebar

**Node Deletion**:
- Select a node and click "Remove Node"
- All connected channels are also removed
- Operation cannot be undone (use Undo button)

Node Parameters
~~~~~~~~~~~~~~

Each node has configurable parameters:

**Detector Efficiency** (0.0 - 1.0):
- **What it is**: Quantum efficiency of the photon detector
- **Default**: 0.9 (90%)
- **Effect**: Higher values increase key rate
- **Typical range**: 0.7-0.95 for practical detectors

**Dark Count Rate** (scientific notation):
- **What it is**: Rate of spurious detector clicks per nanosecond
- **Default**: 1e-8 (10^-8 per ns)
- **Effect**: Higher values increase QBER
- **Typical range**: 1e-9 to 1e-7 per ns

**Mu (Average Photon Number)** (0.0 - 1.0):
- **What it is**: Average number of photons per pulse
- **Default**: 0.2
- **Effect**: Higher values increase key rate but also QBER
- **Optimal range**: 0.1-0.5 for most protocols

**Number of Pulses** (integer):
- **What it is**: Total number of pulses to generate
- **Default**: 10,000
- **Effect**: Higher values improve statistics but increase simulation time
- **Recommendation**: 1,000-100,000 for most simulations

**Pulse Repetition Rate (ns)** (float):
- **What it is**: Time between pulses in nanoseconds
- **Default**: 1.0 ns
- **Effect**: Affects key rate calculation
- **Typical range**: 0.1-10 ns

Channel Management
~~~~~~~~~~~~~~~~~

**Creating Channels**:
- Click and drag from one node to another
- A blue animated line appears between nodes
- Channels are automatically numbered

**Channel Selection**:
- Click on a channel line to select it
- Selected channel appears highlighted
- Channel parameters appear in the sidebar

**Channel Deletion**:
- Select a channel and click "Remove Channel"
- Operation cannot be undone (use Undo button)

Channel Parameters
~~~~~~~~~~~~~~~~~

Each channel has configurable parameters:

**Fiber Length (km)** (float):
- **What it is**: Physical length of the optical fiber
- **Default**: 10.0 km
- **Effect**: Longer distances increase attenuation and QBER
- **Typical range**: 1-100 km for QKD

**Attenuation (dB/km)** (float):
- **What it is**: Fiber loss per kilometer
- **Default**: 0.2 dB/km
- **Effect**: Higher values increase photon loss
- **Typical range**: 0.15-0.25 dB/km for standard fiber

**Wavelength (nm)** (integer):
- **What it is**: Operating wavelength of the system
- **Default**: 1550 nm
- **Effect**: Affects fiber attenuation and detector efficiency
- **Common values**: 850 nm, 1310 nm, 1550 nm

**Fiber Type** (dropdown):
- **Standard Single Mode**: SMF-28, most common
- **Dispersion Shifted**: Optimized for specific wavelengths
- **Non-Zero Dispersion Shifted**: Enhanced for DWDM
- **Photonic Crystal**: Advanced fiber with unique properties

**Phase Flip Probability** (0.0 - 1.0):
- **What it is**: Probability of phase errors in the channel
- **Default**: 0.05 (5%)
- **Effect**: Higher values increase QBER
- **Typical range**: 0.01-0.1 for realistic channels

Network Topologies
~~~~~~~~~~~~~~~~~

The platform supports various network topologies:

**Point-to-Point**:
- Two nodes connected by a single channel
- Simplest configuration for basic QKD analysis
- Good for protocol comparison and parameter optimization

**Linear Chain**:
- Multiple nodes connected in sequence
- Useful for trusted relay networks
- Each node acts as both sender and receiver

**Star Topology**:
- Central node connected to multiple peripheral nodes
- Useful for hub-and-spoke networks
- Central node can act as trusted relay

**Mesh Topology**:
- Multiple connections between nodes
- Provides redundancy and multiple paths
- Complex but robust network design

**Custom Topologies**:
- Create any arbitrary network structure
- Limited only by practical constraints
- Useful for research and analysis

Network Operations
~~~~~~~~~~~~~~~~~

**Undo/Redo**:
- Click the Undo button to revert the last operation
- History is maintained for the current session
- Useful for experimenting with different configurations

**Network Validation**:
- The system automatically validates network configurations
- Errors are displayed in the interface
- Common issues include disconnected nodes or invalid parameters

**Network Export/Import**:
- Save network configurations for later use
- Share configurations with other users
- Useful for reproducible research

Simulation Execution
-------------------

Running Simulations
~~~~~~~~~~~~~~~~~~~

**Starting a Simulation**:
1. Configure protocol and parameters
2. Build and configure the network
3. Click "Run Simulation" button
4. Wait for results to appear

**Simulation Progress**:
- Progress indicator shows simulation status
- Time estimates for completion
- Cancel option for long simulations

**Simulation Results**:
- Results appear in the results section
- Per-channel breakdown of performance
- Summary statistics and analysis

Simulation Parameters
~~~~~~~~~~~~~~~~~~~~

**Global Parameters**:
- Applied to all nodes and channels
- Can be overridden by individual settings
- Useful for consistent parameter sets

**Node-Specific Parameters**:
- Override global settings for specific nodes
- Useful for heterogeneous networks
- Allows realistic modeling of different hardware

**Channel-Specific Parameters**:
- Override global settings for specific channels
- Useful for different fiber types or distances
- Allows detailed network modeling

Results Analysis
---------------

Understanding Results
~~~~~~~~~~~~~~~~~~~~

**QBER (Quantum Bit Error Rate)**:
- **Definition**: Fraction of bits that differ between Alice and Bob
- **Calculation**: Number of errors / Number of compared bits
- **Good range**: 3-11% for practical QKD systems
- **Interpretation**: Lower is better, indicates channel quality

**Sifted Key Length**:
- **Definition**: Number of bits after sifting process
- **Process**: Alice and Bob publicly compare to establish shared bits
- **Efficiency**: Protocol-dependent (25-50% of raw bits)
- **Interpretation**: Higher is better, indicates protocol efficiency

**Final Key Length**:
- **Definition**: Number of secure bits after post-processing
- **Process**: Error correction and privacy amplification
- **Reduction**: Typically 80-95% of sifted key
- **Interpretation**: Final secure key available for use

**Secure Key Rate (bps)**:
- **Definition**: Rate of secure key generation in bits per second
- **Calculation**: Final key length / Total simulation time
- **Units**: Bits per second (bps)
- **Interpretation**: Higher is better, indicates system performance

**Theory Compliance**:
- **Definition**: Verification that results are within theoretical bounds
- **Check**: QBER within acceptable range for the protocol
- **Status**: ✅ (compliant) or ❌ (non-compliant)
- **Interpretation**: Indicates simulation validity

Per-Channel Results
~~~~~~~~~~~~~~~~~~

**Channel Identification**:
- Each channel is numbered and labeled
- Shows source and destination nodes
- Protocol used for the channel

**Performance Metrics**:
- QBER for each channel
- Key generation statistics
- Error analysis and breakdown

**Parameter Summary**:
- Node parameters for source and destination
- Channel parameters and configuration
- Protocol-specific parameters

**Theory Analysis**:
- Compliance with theoretical predictions
- Warnings for non-compliant results
- Recommendations for improvement

Advanced Features
----------------

Multi-Protocol Networks
~~~~~~~~~~~~~~~~~~~~~~

**Protocol Selection**:
- Different protocols can be used on different channels
- Useful for protocol comparison studies
- Allows heterogeneous network analysis

**Protocol Parameters**:
- Each protocol maintains its own parameter set
- Parameters are preserved when switching protocols
- Useful for comparative analysis

**Results Comparison**:
- Compare performance across protocols
- Identify optimal protocols for different scenarios
- Analyze protocol trade-offs

Trusted Relay Networks
~~~~~~~~~~~~~~~~~~~~~

**Relay Configuration**:
- Add intermediate nodes as trusted relays
- Configure relay parameters and behavior
- Model realistic network topologies

**End-to-End Key Generation**:
- Calculate secure key through multiple hops
- Account for relay overhead and delays
- Analyze network scalability

**Security Considerations**:
- Trusted relay security model
- Key management and distribution
- Network security analysis

Parameter Optimization
~~~~~~~~~~~~~~~~~~~~~

**Systematic Parameter Sweeps**:
- Vary parameters systematically
- Identify optimal parameter combinations
- Analyze parameter sensitivity

**Performance Optimization**:
- Find maximum key rate configurations
- Optimize for specific constraints
- Balance performance and security

**Sensitivity Analysis**:
- Analyze parameter impact on performance
- Identify critical parameters
- Understand system robustness

Data Export and Analysis
~~~~~~~~~~~~~~~~~~~~~~~

**Results Export**:
- Export simulation results in various formats
- Save data for external analysis
- Share results with collaborators

**Performance Plots**:
- Generate performance vs. parameter plots
- Analyze trends and relationships
- Visualize optimization results

**Statistical Analysis**:
- Calculate confidence intervals
- Analyze result variability
- Perform statistical tests

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Simulation Won't Start**:
- Check network connectivity
- Verify all parameters are valid
- Ensure backend is running

**High QBER (>11%)**:
- Reduce fiber length
- Check detector parameters
- Verify photon number is reasonable
- Check for parameter conflicts

**Low Key Rate**:
- Increase photon number (but not too much)
- Check detector efficiency
- Verify pulse repetition rate
- Check channel attenuation

**No Results Displayed**:
- Check if nodes are properly connected
- Verify all parameters are valid
- Check browser console for errors
- Ensure simulation completed successfully

**Network Validation Errors**:
- Check for disconnected nodes
- Verify parameter ranges
- Ensure logical network structure
- Check for parameter conflicts

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~

**Simulation Speed**:
- Reduce number of pulses for quick tests
- Use fewer nodes for initial testing
- Optimize parameter ranges
- Use appropriate simulation parameters

**Memory Usage**:
- Limit network size for large simulations
- Use appropriate pulse counts
- Monitor system resources
- Optimize parameter storage

**Accuracy vs. Speed**:
- Balance simulation accuracy with speed
- Use appropriate parameter ranges
- Consider statistical significance
- Validate results with multiple runs

Best Practices
-------------

Simulation Design
~~~~~~~~~~~~~~~~

**Parameter Selection**:
- Use realistic parameter values
- Consider hardware limitations
- Account for practical constraints
- Validate against theoretical bounds

**Network Design**:
- Design logical network topologies
- Consider practical constraints
- Plan for scalability
- Account for security requirements

**Protocol Selection**:
- Choose appropriate protocols for your use case
- Consider performance requirements
- Account for security needs
- Evaluate hardware requirements

Data Management
~~~~~~~~~~~~~~

**Result Organization**:
- Organize results systematically
- Use consistent naming conventions
- Document parameter sets
- Maintain result history

**Data Validation**:
- Verify result consistency
- Check for outliers
- Validate against theory
- Cross-check with literature

**Data Sharing**:
- Export results in standard formats
- Document experimental conditions
- Share parameter configurations
- Maintain reproducibility

Research Workflows
~~~~~~~~~~~~~~~~~

**Exploratory Analysis**:
- Start with simple configurations
- Gradually increase complexity
- Document parameter effects
- Identify interesting regions

**Systematic Studies**:
- Plan parameter sweeps carefully
- Use appropriate statistical methods
- Account for multiple comparisons
- Validate results thoroughly

**Comparative Analysis**:
- Use consistent parameter sets
- Account for protocol differences
- Consider practical constraints
- Document comparison methodology

Advanced Topics
--------------

Custom Protocols
~~~~~~~~~~~~~~~

**Protocol Implementation**:
- Extend the platform with new protocols
- Implement custom sender/receiver classes
- Add protocol-specific parameters
- Integrate with analysis tools

**Protocol Validation**:
- Validate against theoretical predictions
- Compare with literature results
- Test with known parameter sets
- Verify security properties

**Protocol Optimization**:
- Optimize protocol parameters
- Analyze performance trade-offs
- Identify optimal configurations
- Consider practical constraints

Hardware Integration
~~~~~~~~~~~~~~~~~~~

**Real Hardware**:
- Interface with real QKD hardware
- Validate simulation models
- Calibrate simulation parameters
- Test with real-world conditions

**Hardware Modeling**:
- Improve component models
- Add realistic noise sources
- Model hardware imperfections
- Account for environmental effects

**Performance Validation**:
- Compare simulation with hardware
- Validate model accuracy
- Identify model limitations
- Improve simulation fidelity

Security Analysis
~~~~~~~~~~~~~~~~~

**Attack Modeling**:
- Model various attack scenarios
- Analyze security vulnerabilities
- Evaluate countermeasures
- Assess security margins

**Security Metrics**:
- Calculate security parameters
- Analyze key security
- Evaluate privacy amplification
- Assess information leakage

**Security Optimization**:
- Optimize for security
- Balance security and performance
- Consider practical constraints
- Evaluate security trade-offs

Future Enhancements
------------------

Planned Features
~~~~~~~~~~~~~~~

**Additional Protocols**:
- More QKD protocol implementations
- Hybrid protocol support
- Protocol switching capabilities
- Custom protocol framework

**Advanced Analysis**:
- More sophisticated analysis tools
- Statistical analysis packages
- Machine learning integration
- Automated optimization

**User Interface**:
- Enhanced visualization tools
- Real-time monitoring
- Advanced network builder
- Improved result display

**Performance Improvements**:
- Faster simulation engine
- Parallel processing support
- GPU acceleration
- Distributed computing

Getting Help
-----------

Documentation
~~~~~~~~~~~~

**User Documentation**:
- This user guide
- API reference documentation
- Example tutorials
- Best practices guide

**Developer Documentation**:
- Code documentation
- Architecture guide
- Contributing guidelines
- Development setup

**Research Documentation**:
- Protocol descriptions
- Mathematical models
- Validation studies
- Performance analysis

Community Support
~~~~~~~~~~~~~~~~

**GitHub Issues**:
- Report bugs and problems
- Request new features
- Ask questions
- Share experiences

**Discussion Forum**:
- Community discussions
- User support
- Feature requests
- Best practices sharing

**Mailing List**:
- Announcements
- Technical discussions
- Community updates
- Research collaboration

**Contributing**:
- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions

The QKD Simulation Platform is designed to be a comprehensive tool for QKD research, education, and development. This user guide covers the main features, but the platform is constantly evolving. Stay updated with the latest releases and contribute to the community to help improve the platform for everyone. 