# QKD Simulation Platform

This project simulates Quantum Key Distribution (QKD) protocols (DPS and COW) with a FastAPI backend and a React frontend. It supports multi-node, multi-channel network configurations and provides detailed per-channel simulation results.

---

## Project Structure

```
cow_qkd_repo/
├── api.py                # FastAPI entry point (backend API)
├── main.py               # Backend entry script and simulation runner
├── simulation/           # Core simulation logic (Python package)
│   ├── __init__.py
│   ├── Network.py        # Network and node management
│   ├── Source.py         # Light source and sender logic
│   └── Hardware.py       # Receiver and channel hardware logic
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
- Open the frontend in your browser and use the form to configure and run QKD simulations.
- The frontend communicates with the backend API and displays detailed results for each channel.

---

## Main Files and Folders
- `simulation/Network.py`: Manages the QKD network, nodes, and connections.
- `simulation/Source.py`: Implements light source and sender logic for QKD protocols.
- `simulation/Hardware.py`: Models receiver and optical channel hardware.
- `api.py`: FastAPI app exposing simulation endpoints.
- `main.py`: Script for running simulations directly or as part of the API.
- `frontend/src/components/`: Contains main React components (`QKDForm.js`, `QKDNetwork.js`, `Results.js`).

---

## Contributing & Extending
- Add new QKD protocols by extending the simulation package.
- Add new frontend features by creating additional React components in `src/components/`.
- Please open issues or pull requests for bugs, questions, or contributions.

---

For any issues, please open an issue on GitHub. 