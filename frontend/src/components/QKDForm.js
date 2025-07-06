import React from "react";

export default function QKDForm({ params, onChange }) {
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    onChange({ ...params, [name]: type === 'number' ? Number(value) : value });
  };

  return (
    <form style={{ marginBottom: 32, display: 'flex', gap: 24, alignItems: 'center', flexWrap: 'wrap' }} onSubmit={e => e.preventDefault()}>
      <label>
        Protocol:
        <select name="protocol" value={params.protocol} onChange={handleChange}>
          <option value="dps">DPS-QKD</option>
          <option value="cow">COW-QKD</option>
          <option value="bb84">BB84-QKD</option>
        </select>
      </label>
      <label>
        Pulses:
        <input name="num_pulses" type="number" value={params.num_pulses} onChange={handleChange} />
      </label>
      <label>
        Pulse Repetition Rate (ns):
        <input name="pulse_repetition_rate" type="number" value={params.pulse_repetition_rate} onChange={handleChange} />
      </label>
      <label>
        Phase Flip Probability (0-1):
        <input name="phase_flip_prob" type="number" step="0.001" min="0" max="1" value={params.phase_flip_prob} onChange={handleChange} />
      </label>
      {params.protocol === "cow" && (
        <>
          <label>
            COW Monitor Pulse Ratio:
            <input name="cow_monitor_pulse_ratio" type="number" step="0.01" value={params.cow_monitor_pulse_ratio} onChange={handleChange} />
          </label>
          <label>
            COW Detection Threshold (Photons):
            <input name="cow_detection_threshold_photons" type="number" value={params.cow_detection_threshold_photons} onChange={handleChange} />
          </label>
          <label>
            COW Extinction Ratio (dB):
            <input name="cow_extinction_ratio_db" type="number" value={params.cow_extinction_ratio_db} onChange={handleChange} />
          </label>
        </>
      )}
    </form>
  );
} 