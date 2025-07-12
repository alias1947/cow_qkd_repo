Quick Start Guide
================

This guide will walk you through setting up and running your first QKD simulation in just a few minutes.

Prerequisites
------------

Before starting, ensure you have:

1. **Python 3.8+** installed and accessible from command line
2. **Node.js 14+** installed for the frontend
3. **Git** installed for cloning the repository

If you haven't installed these yet, please follow the :doc:`installation` guide first.

Getting Started
--------------

Step 1: Clone and Setup
~~~~~~~~~~~~~~~~~~~~~~~

1. **Clone the repository**:

   .. code-block:: bash

      git clone https://github.com/your-username/qkd-simulation-platform.git
      cd qkd-simulation-platform

2. **Install Python dependencies**:

   .. code-block:: bash

      pip install -r requirements.txt

3. **Install frontend dependencies**:

   .. code-block:: bash

      cd frontend
      npm install
      cd ..

Step 2: Start the Backend
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Start the FastAPI backend server**:

   .. code-block:: bash

      uvicorn api:app --reload

   You should see output similar to:

   .. code-block:: text

      INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
      INFO:     Started reloader process [12345] using StatReload
      INFO:     Started server process [12346]
      INFO:     Listening on http://127.0.0.1:8000
      INFO:     Waiting for application startup.
      INFO:     Application startup complete.

2. **Verify the backend is running**:
   - Open a web browser and navigate to `http://127.0.0.1:8000`
   - You should see: `{"message": "QKD Simulation API"}`

Step 3: Start the Frontend
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Open a new terminal window** (keep the backend running)

2. **Navigate to the frontend directory**:

   .. code-block:: bash

      cd frontend

3. **Start the React development server**:

   .. code-block:: bash

      npm start

   You should see output similar to:

   .. code-block:: text

      Compiled successfully!

      You can now view qkd-simulation-platform in the browser.

        Local:            http://localhost:3000
        On Your Network:  http://192.168.1.100:3000

      Note that the development build is not optimized.
      To create a production build, use npm run build.

4. **Open the application**:
   - Your browser should automatically open to `http://localhost:3000`
   - If not, manually navigate to that URL

Your First Simulation
---------------------

Now let's run a simple QKD simulation to see how the platform works.

Step 1: Configure the Protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Select a Protocol**:
   - In the frontend, you'll see a "Protocol" dropdown
   - Select "DPS-QKD" for your first simulation
   - This is the simplest protocol to start with

2. **Verify Protocol Parameters**:
   - The default parameters should be suitable for a first run
   - You can leave them as-is for now

Step 2: Build the Network
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Add Nodes**:
   - In the network builder area, you should see two nodes (Node 1 and Node 2)
   - These represent Alice and Bob in the QKD protocol
   - The nodes are already positioned and ready to use

2. **Connect the Nodes**:
   - Click and drag from Node 1 to Node 2 to create a connection
   - This represents the optical fiber channel between Alice and Bob
   - A blue animated line should appear between the nodes

3. **Configure Channel Parameters**:
   - Click on the channel line to select it
   - In the sidebar, you'll see channel parameters
   - Set the fiber length to 20 km (a typical QKD distance)
   - Leave other parameters at their default values

Step 3: Run the Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Start Simulation**:
   - Click the "Run Simulation" button
   - You should see a loading indicator while the simulation runs

2. **View Results**:
   - Once complete, results will appear in the results section
   - You should see metrics like:
     - QBER (Quantum Bit Error Rate)
     - Sifted key length
     - Final key length
     - Secure key rate

Example Results
~~~~~~~~~~~~~~

For a typical DPS-QKD simulation with default parameters, you might see:

.. code-block:: text

   Channel 1 Results:
   - Protocol: DPS-QKD
   - QBER: 0.045 (4.5%)
   - Sifted Key Length: 2,500 bits
   - Final Key Length: 2,345 bits
   - Secure Key Rate: 2,345 bps
   - Theory Compliance: ✅ QBER is within practical range

Understanding the Results
------------------------

QBER (Quantum Bit Error Rate)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **What it is**: The fraction of bits that differ between Alice and Bob
- **Good range**: 3-11% for practical QKD systems
- **Your result**: 4.5% is excellent - indicates good channel quality

Sifted Key Length
~~~~~~~~~~~~~~~~~

- **What it is**: Number of bits after the sifting process
- **Process**: Alice and Bob publicly compare to establish shared bits
- **Your result**: 2,500 bits from 10,000 pulses = 25% efficiency (typical for DPS)

Final Key Length
~~~~~~~~~~~~~~~

- **What it is**: Number of secure bits after post-processing
- **Process**: Error correction and privacy amplification
- **Your result**: 2,345 bits (about 94% of sifted key)

Secure Key Rate
~~~~~~~~~~~~~~

- **What it is**: Rate of secure key generation in bits per second
- **Calculation**: Final key length / total simulation time
- **Your result**: 2,345 bps (good for a 20 km link)

Theory Compliance
~~~~~~~~~~~~~~~~~

- **What it is**: Verification that results are within theoretical bounds
- **Your result**: ✅ indicates the simulation is working correctly

Exploring Different Protocols
----------------------------

Now let's try the other protocols to see how they compare.

COW-QKD Simulation
~~~~~~~~~~~~~~~~~~

1. **Switch Protocol**:
   - Change the protocol dropdown to "COW-QKD"
   - Notice the additional COW-specific parameters appear

2. **Configure COW Parameters**:
   - Monitor Pulse Ratio: 0.1 (10% monitoring pulses)
   - Detection Threshold: 0 photons
   - Extinction Ratio: 20 dB
   - Bit Flip Error Probability: 0.05

3. **Run Simulation**:
   - Click "Run Simulation"
   - Compare results with DPS-QKD

Expected COW-QKD Results:
- QBER: 3-10%
- Sifting efficiency: ~40% (higher than DPS)
- Key rate: Similar or higher than DPS

BB84-QKD Simulation
~~~~~~~~~~~~~~~~~~~

1. **Switch Protocol**:
   - Change the protocol dropdown to "BB84-QKD"
   - Notice the simpler parameter set

2. **Run Simulation**:
   - Click "Run Simulation"
   - Compare results with other protocols

Expected BB84-QKD Results:
- QBER: 3-11%
- Sifting efficiency: ~50% (highest of the three)
- Key rate: May be lower due to basis reconciliation

Comparing Results
~~~~~~~~~~~~~~~~

Create a table to compare your results:

+------------+--------+----------------+----------------+----------------+
| Protocol   | QBER   | Sifted Length  | Final Length   | Key Rate (bps) |
+============+========+================+================+================+
| DPS-QKD    | 4.5%   | 2,500          | 2,345          | 2,345          |
+------------+--------+----------------+----------------+----------------+
| COW-QKD    | 4.2%   | 4,000          | 3,800          | 3,800          |
+------------+--------+----------------+----------------+----------------+
| BB84-QKD   | 4.8%   | 5,000          | 4,700          | 4,700          |
+------------+--------+----------------+----------------+----------------+

Experimenting with Parameters
----------------------------

Now let's experiment with different parameters to see their effects.

Distance Effects
~~~~~~~~~~~~~~~

1. **Increase Distance**:
   - Select the channel and change fiber length to 50 km
   - Run simulation again
   - Notice how QBER increases and key rate decreases

2. **Compare Results**:
   - 20 km: QBER ~4.5%, Key Rate ~2,345 bps
   - 50 km: QBER ~8.2%, Key Rate ~1,200 bps

Photon Number Effects
~~~~~~~~~~~~~~~~~~~~

1. **Modify Photon Number**:
   - Select Node 1 and change "Mu" to 0.5
   - Run simulation
   - Notice changes in key rate and QBER

2. **Compare Results**:
   - μ = 0.2: QBER ~4.5%, Key Rate ~2,345 bps
   - μ = 0.5: QBER ~6.8%, Key Rate ~3,100 bps

Detector Efficiency Effects
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Modify Detector Efficiency**:
   - Select Node 2 and change "Detector Efficiency" to 0.7
   - Run simulation
   - Notice decrease in key rate

2. **Compare Results**:
   - η = 0.9: Key Rate ~2,345 bps
   - η = 0.7: Key Rate ~1,800 bps

Multi-Node Networks
-------------------

Let's create a more complex network with multiple nodes.

Step 1: Add More Nodes
~~~~~~~~~~~~~~~~~~~~~~

1. **Add a Third Node**:
   - Click the "Add Node" button
   - Position the new node between the existing nodes
   - This will be a trusted relay node

2. **Connect the Nodes**:
   - Connect Node 1 to the new node
   - Connect the new node to Node 2
   - You now have a three-node chain

Step 2: Configure the Network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Set Channel Parameters**:
   - Set both channels to 10 km length
   - This creates a 20 km total distance with a relay

2. **Run Simulation**:
   - Click "Run Simulation"
   - The system will simulate key generation on each link

Step 3: Analyze Results
~~~~~~~~~~~~~~~~~~~~~~~

You should see results for both channels:
- Channel 1: Node 1 → Relay
- Channel 2: Relay → Node 2

The system will also calculate the end-to-end key through the trusted relay.

Troubleshooting
--------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Backend Won't Start**:
- Check if port 8000 is already in use
- Try: `uvicorn api:app --reload --port 8001`
- Verify Python dependencies are installed

**Frontend Won't Start**:
- Check if port 3000 is already in use
- Try: `PORT=3001 npm start`
- Verify Node.js dependencies are installed

**Simulation Fails**:
- Check browser console for errors
- Verify backend is running
- Check network configuration

**No Results Displayed**:
- Check if nodes are properly connected
- Verify all parameters are valid
- Check browser console for errors

**High QBER (>11%)**:
- Reduce fiber length
- Check detector parameters
- Verify photon number is reasonable

**Low Key Rate**:
- Increase photon number (but not too much)
- Check detector efficiency
- Verify pulse repetition rate

Getting Help
-----------

If you encounter issues:

1. **Check the FAQ**: Common questions and solutions
2. **Search Issues**: Look for similar problems on GitHub
3. **Create an Issue**: Report bugs or request help
4. **Community Support**: Join the discussion forum

Next Steps
----------

Now that you've completed your first simulation:

1. **Read the User Guide**: Learn about all features in :doc:`user-guide`
2. **Explore Examples**: Check out practical examples in :doc:`examples`
3. **Study the API**: Learn programmatic access in :doc:`api-reference`
4. **Contribute**: Help improve the platform (see :doc:`contributing`)

Advanced Topics
--------------

Once you're comfortable with the basics:

1. **Custom Protocols**: Learn how to implement new QKD protocols
2. **Hardware Models**: Understand the optical component models
3. **Network Analysis**: Study multi-node network behavior
4. **Security Analysis**: Explore QKD security aspects
5. **Performance Optimization**: Learn to optimize simulation parameters

Congratulations! You've successfully run your first QKD simulation. The platform is now ready for your research, education, or development needs. 