# QKD Simulation Platform

This project simulates QKD protocols (DPS and COW) with a FastAPI backend and a React frontend.

## Backend (FastAPI)

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn pydantic
   ```
2. **Run the backend server:**
   ```bash
   uvicorn api:app --reload
   ```
   The backend will be available at `http://127.0.0.1:8000`.

## Frontend (React)

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
   The frontend will be available at `http://localhost:3000`.

## Usage
- Open the frontend in your browser and use the form to run QKD simulations.
- The frontend communicates with the backend API for results.

---

For any issues, please open an issue on GitHub. 