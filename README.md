# QKD Simulation Platform

This project simulates Quantum Key Distribution (QKD) protocols (DPS, COW, and BB84) with a FastAPI backend and a React frontend. It supports multi-node, multi-channel network configurations and provides detailed per-channel simulation results.

---

## Project Structure

```
cow_qkd_repo/
├── api.py                # FastAPI entry point (backend API)
├── main.py               # Backend entry script and simulation runner
├── simulation/           # Core simulation logic (Python package)
│   ├── __init__.py
│   ├── Network.py        # Network and node management
│   ├── Hardware.py       # All hardware components (light source, modulators, channel, etc.)
│   ├── Sender.py         # Sender logic for all QKD protocols
│   ├── Receiver.py       # Receiver logic for all QKD protocols
│   └── ...               # Other simulation files
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # Main React components
│   │   │   ├── QKDForm.js
│   │   │   ├── QKDNetwork.js
│   │   │   └── Results.js
│   │   └── ...           # Other React files
│   └── ...               # Frontend config and public assets
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## Supported QKD Protocols

### DPS-QKD (Differential Phase Shift)
- **Encoding**: Phase difference between consecutive pulses (0, π)
- **Detection**: Mach-Zehnder interferometer with two detectors
- **Sifting**: Based on detector clicks and phase difference
- **Key Rate**: ~25% of raw bits after sifting
- **Hardware**: Fiber Mach-Zehnder interferometer with delay line

### COW-QKD (Coherent One-Way)
- **Encoding**: Intensity modulation (vacuum + coherent pulse)
- **Detection**: Single photon detector with intensity monitoring
- **Sifting**: Keep bits where Alice and Bob agree on data pulses
- **Monitoring**: Pairs of monitoring pulses for eavesdropping detection
- **Key Rate**: ~40% of raw bits after sifting
- **Hardware**: Single photon detector with optical switching

### BB84-QKD (Bennett-Brassard 1984)
- **Encoding**: Four quantum states in two bases (rectilinear and diagonal)
- **States**: |0⟩, |1⟩ (rectilinear) and |+⟩, |-⟩ (diagonal)
- **Detection**: Single photon detector with basis switching
- **Sifting**: Keep bits where Alice and Bob used the same basis
- **Security**: Based on quantum uncertainty principle
- **Key Rate**: ~50% of raw bits after sifting
- **Hardware**: Polarizing beam splitter with basis switching

---

## Architecture Overview

- **Backend (FastAPI, Python):**
  - Exposes REST API endpoints for running QKD simulations.
  - Core simulation logic is modularized in the `simulation/` package.
  - Accepts network structure and parameters, runs simulations, and returns results.

- **Frontend (React):**
  - User interface for configuring nodes, channels, and simulation parameters.
  - Sends requests to the backend and displays results per channel.
  - Main components are organized in `src/components/`.

---

## Getting Started

### Backend (FastAPI)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the backend server:**
   ```bash
   uvicorn api:app --reload
   ```
   The backend will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Frontend (React)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Start the frontend:**
   ```bash
   npm start
   ```
   The frontend will be available at [http://localhost:3000](http://localhost:3000).

---

## Usage

### Protocol Selection
- Choose from three QKD protocols: DPS, COW, or BB84
- Each protocol has different encoding schemes and detection methods
- Protocol switching automatically resets network topology and results

### Network Configuration
- Add/remove nodes and channels using the interactive network topology
- Configure node parameters (detector efficiency, dark count rate, photon number)
- Set channel parameters (fiber length, attenuation, phase flip probability)

### Simulation Features
- **Multi-node Support**: Simulate networks with multiple nodes and channels
- **Per-channel Results**: Detailed results for each channel in the network
- **QBER Calculation**: Quantum Bit Error Rate calculation for each protocol
- **Key Rate Analysis**: Secure key rate and final key length estimation
- **Protocol-specific Parameters**: Each protocol has its own parameter set

### Results Display
- QBER (Quantum Bit Error Rate) for each channel
- Sifted key length and final secure key length
- Secure key rate in bits per second
- Theory compliance warnings
- Detailed parameter breakdown

---

## Main Files and Folders

### Backend Implementation
- `simulation/Network.py`: Manages the QKD network, nodes, and connections. Implements protocol-specific key generation methods.
- `simulation/Hardware.py`: Contains all hardware components (light source, modulators, optical channels, detectors, etc.).
- `simulation/Sender.py`: Implements sender logic for QKD protocols (DPS, COW, BB84).
- `simulation/Receiver.py`: Implements receiver logic for QKD protocols (DPS, COW, BB84).
- `api.py`: FastAPI app exposing simulation endpoints with protocol-specific handling.
- `main.py`: Script for running simulations directly or as part of the API.

### Frontend Implementation
- `frontend/src/components/QKDForm.js`: Protocol selection and parameter configuration
- `frontend/src/components/QKDNetwork.js`: Interactive network topology builder
- `frontend/src/components/Results.js`: Simulation results display
- `frontend/src/App.js`: Main application with protocol switching and state management

### Protocol Implementation Details
- **DPS**: Phase difference encoding with Mach-Zehnder interferometer detection
- **COW**: Intensity modulation with monitoring pulse pairs for eavesdropping detection
- **BB84**: Four quantum states in two bases with basis switching and sifting

---

## Contributing & Extending
- Add new QKD protocols by extending the simulation package.
- Add new frontend features by creating additional React components in `src/components/`.
- Please open issues or pull requests for bugs, questions, or contributions.

---

For any issues, please open an issue on GitHub. 