import React, { useState } from "react";

export default function QKDForm({ onSimulate }) {
  const [protocol, setProtocol] = useState("dps");
  const [num_pulses, setNumPulses] = useState(5000);
  const [distance_km, setDistanceKm] = useState(25);
  const [mu, setMu] = useState(0.18);
  const [detector_efficiency, setDetectorEfficiency] = useState(0.9);
  const [dark_count_rate, setDarkCountRate] = useState(1e-8);
  const [pulse_repetition_rate, setPulseRepetitionRate] = useState(1);
  const [cow_monitor_pulse_ratio, setCowMonitorPulseRatio] = useState(0.1);
  const [cow_detection_threshold_photons, setCowDetectionThresholdPhotons] = useState(0);

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
      <label>
        Distance (km):
        <input type="number" value={distance_km} onChange={e => setDistanceKm(e.target.value)} />
      </label>
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
      {protocol === "cow" && (
        <>
          <label>
            COW Monitor Pulse Ratio:
            <input type="number" step="0.01" value={cow_monitor_pulse_ratio} onChange={e => setCowMonitorPulseRatio(e.target.value)} />
          </label>
          <label>
            COW Detection Threshold Photons:
            <input type="number" value={cow_detection_threshold_photons} onChange={e => setCowDetectionThresholdPhotons(e.target.value)} />
          </label>
        </>
      )}
      <button type="submit">Run Simulation</button>
    </form>
  );
} 