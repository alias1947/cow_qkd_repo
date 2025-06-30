import React, { useState } from "react";

export default function QKDForm({ onSimulate }) {
  const [protocol, setProtocol] = useState("dps");
  const [num_pulses, setNumPulses] = useState(10000);
  const [distance_km, setDistanceKm] = useState(10);
  const [mu, setMu] = useState(0.20);
  const [detector_efficiency, setDetectorEfficiency] = useState(0.9);
  const [dark_count_rate, setDarkCountRate] = useState(1e-8);
  const [pulse_repetition_rate, setPulseRepetitionRate] = useState(1);
  const [cow_monitor_pulse_ratio, setCowMonitorPulseRatio] = useState(0.1);
  const [cow_detection_threshold_photons, setCowDetectionThresholdPhotons] = useState(0);
  const [phase_flip_prob, setPhaseFlipProb] = useState(0.05);
  
  // Fiber selection parameters with default values
  const [fiber_length_km, setFiberLengthKm] = useState(10);
  const [fiber_attenuation_db_per_km, setFiberAttenuationDbPerKm] = useState(0.2);
  const [wavelength_nm, setwavelength_nm]=useState(1550)
  const [fiber_type, setFiberType] = useState("standard_single_mode");
  const [cow_extinction_ratio_db, setCowExtinctionRatioDb] = useState(20);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSimulate({
      protocol,
      num_pulses: Number(num_pulses),
      distance_km: Number(distance_km),
      mu: Number(mu),
      detector_efficiency: Number(detector_efficiency),
      dark_count_rate: Number(dark_count_rate),
      pulse_repetition_rate: Number(pulse_repetition_rate),
      cow_monitor_pulse_ratio: Number(cow_monitor_pulse_ratio),
      cow_detection_threshold_photons: Number(cow_detection_threshold_photons),
      cow_extinction_ratio_db: Number(cow_extinction_ratio_db),
      // Fiber parameters
      fiber_length_km: Number(fiber_length_km),
      fiber_attenuation_db_per_km: Number(fiber_attenuation_db_per_km),
      wavelength_nm: Number(wavelength_nm),
      fiber_type: fiber_type,
      // Phase flip noise
      phase_flip_prob: Number(phase_flip_prob),
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 32 }}>
      <label>
        Protocol:
        <select value={protocol} onChange={e => setProtocol(e.target.value)}>
          <option value="dps">DPS-QKD</option>
          <option value="cow">COW-QKD</option>
        </select>
      </label>
      <label>
        Pulses:
        <input type="number" value={num_pulses} onChange={e => setNumPulses(e.target.value)} />
      </label>
      {/* <label>
        Distance (km):
        <input type="number" value={distance_km} onChange={e => setDistanceKm(e.target.value)} />
      </label> */}
      <label>
        Mu:
        <input type="number" step="0.01" value={mu} onChange={e => setMu(e.target.value)} />
      </label>
      <label>
        Detector Efficiency:
        <input type="number" step="0.01" value={detector_efficiency} onChange={e => setDetectorEfficiency(e.target.value)} />
      </label>
      <label>
        Dark Count Rate:
        <input type="number" step="any" value={dark_count_rate} onChange={e => setDarkCountRate(e.target.value)} />
      </label>
      <label>
        Pulse Repetition Rate (ns):
        <input type="number" value={pulse_repetition_rate} onChange={e => setPulseRepetitionRate(e.target.value)} />
      </label>
      
      {/* Fiber Selection Section */}
      <div style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px' }}>
        <h3>Fiber Configuration</h3>
        <label>
          Fiber Length (km):
          <input 
            type="number" 
            step="0.1" 
            value={fiber_length_km} 
            onChange={e => setFiberLengthKm(e.target.value)} 
          />
        </label>
        <label>
          Wavelength (nm):
          <input 
            type="number" 
            step="1" 
            value={wavelength_nm} 
            onChange={e => setwavelength_nm(e.target.value)} 
          />
        </label>
        <label>
          Fiber Attenuation (dB/km):
          <input 
            type="number" 
            step="0.01" 
            value={fiber_attenuation_db_per_km} 
            onChange={e => setFiberAttenuationDbPerKm(e.target.value)} 
          />
        </label>
        <label>
          Fiber Type:
          <select value={fiber_type} onChange={e => setFiberType(e.target.value)}>
            <option value="standard_single_mode">SMF-28</option>
            <option value="dispersion_shifted">Dispersion Shifted</option>
            <option value="non_zero_dispersion_shifted">Non-Zero Dispersion Shifted</option>
            <option value="photonic_crystal">Photonic Crystal Fiber</option>
          </select>
        </label>
      </div>
      
      {protocol === "cow" && (
        <>
          <label>
            COW Monitor Pulse Ratio:
            <input type="number" step="0.01" value={cow_monitor_pulse_ratio} onChange={e => setCowMonitorPulseRatio(e.target.value)} />
          </label>
          <div className="form-group">
            <label>COW Detection Threshold (Photons)</label>
            <input type="number" value={cow_detection_threshold_photons} onChange={e => setCowDetectionThresholdPhotons(e.target.value)} />
          </div>
          <div className="form-group">
            <label>COW Extinction Ratio (dB)</label>
            <input type="number" value={cow_extinction_ratio_db} onChange={e => setCowExtinctionRatioDb(e.target.value)} />
          </div>
        </>
      )}
      <label>
        Phase Flip Probability (0-1):
        <input type="number" step="0.001" min="0" max="1" value={phase_flip_prob} onChange={e => setPhaseFlipProb(e.target.value)} />
      </label>
      <button type="submit">Run Simulation</button>
    </form>
  );
} 