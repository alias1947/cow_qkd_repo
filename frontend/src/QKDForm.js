import React, { useState } from "react";

function NodeForm({ node, onChange, onRemove }) {
  return (
    <div style={{ border: '1px solid #ccc', padding: 10, margin: 8, borderRadius: 5 }}>
      <b>Node {node.id}</b>
      <button type="button" onClick={() => onRemove(node.id)} style={{ marginLeft: 8 }}>Remove</button>
      <div>
        <label>Detector Efficiency:
          <input type="number" step="0.01" value={node.detector_efficiency} onChange={e => onChange(node.id, { ...node, detector_efficiency: e.target.value })} />
        </label>
        <label>Dark Count Rate:
          <input type="number" step="any" value={node.dark_count_rate} onChange={e => onChange(node.id, { ...node, dark_count_rate: e.target.value })} />
        </label>
        <label>Mu:
          <input type="number" step="0.01" value={node.mu} onChange={e => onChange(node.id, { ...node, mu: e.target.value })} />
        </label>
      </div>
    </div>
  );
}

function ChannelForm({ channel, nodes, onChange, onRemove }) {
  return (
    <div style={{ border: '1px solid #aaa', padding: 10, margin: 8, borderRadius: 5 }}>
      <b>Channel {channel.id}</b>
      <button type="button" onClick={() => onRemove(channel.id)} style={{ marginLeft: 8 }}>Remove</button>
      <div>
        <label>From:
          <select value={channel.from} onChange={e => onChange(channel.id, { ...channel, from: Number(e.target.value) })}>
            {nodes.map(n => <option key={n.id} value={n.id}>Node {n.id}</option>)}
          </select>
        </label>
        <label>To:
          <select value={channel.to} onChange={e => onChange(channel.id, { ...channel, to: Number(e.target.value) })}>
            {nodes.map(n => <option key={n.id} value={n.id}>Node {n.id}</option>)}
          </select>
        </label>
        <label>Fiber Length (km):
          <input type="number" step="0.1" value={channel.fiber_length_km} onChange={e => onChange(channel.id, { ...channel, fiber_length_km: e.target.value })} />
        </label>
        <label>Attenuation (dB/km):
          <input type="number" step="0.01" value={channel.fiber_attenuation_db_per_km} onChange={e => onChange(channel.id, { ...channel, fiber_attenuation_db_per_km: e.target.value })} />
        </label>
        <label>Wavelength (nm):
          <input type="number" step="1" value={channel.wavelength_nm} onChange={e => onChange(channel.id, { ...channel, wavelength_nm: e.target.value })} />
        </label>
        <label>Fiber Type:
          <select value={channel.fiber_type} onChange={e => onChange(channel.id, { ...channel, fiber_type: e.target.value })}>
            <option value="standard_single_mode">SMF-28</option>
            <option value="dispersion_shifted">Dispersion Shifted</option>
            <option value="non_zero_dispersion_shifted">Non-Zero Dispersion Shifted</option>
            <option value="photonic_crystal">Photonic Crystal Fiber</option>
          </select>
        </label>
        <label>Phase Flip Probability (0-1):
          <input type="number" step="0.001" min="0" max="1" value={channel.phase_flip_prob} onChange={e => onChange(channel.id, { ...channel, phase_flip_prob: e.target.value })} />
        </label>
      </div>
    </div>
  );
}

export default function QKDForm({ onSimulate }) {
  const [protocol, setProtocol] = useState("dps");
  const [num_pulses, setNumPulses] = useState(10000);
  const [pulse_repetition_rate, setPulseRepetitionRate] = useState(1);
  const [phase_flip_prob, setPhaseFlipProb] = useState(0.05);
  const [cow_monitor_pulse_ratio, setCowMonitorPulseRatio] = useState(0.1);
  const [cow_detection_threshold_photons, setCowDetectionThresholdPhotons] = useState(0);
  const [cow_extinction_ratio_db, setCowExtinctionRatioDb] = useState(20);

  // Multi-node state
  const [nodes, setNodes] = useState([
    { id: 1, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 },
    { id: 2, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 }
  ]);
  const [nextNodeId, setNextNodeId] = useState(3);
  const [channels, setChannels] = useState([
    { id: 1, from: 1, to: 2, fiber_length_km: 10, fiber_attenuation_db_per_km: 0.2, wavelength_nm: 1550, fiber_type: "standard_single_mode", phase_flip_prob: 0.05 }
  ]);
  const [nextChannelId, setNextChannelId] = useState(2);

  // Node handlers
  const addNode = () => {
    setNodes([...nodes, { id: nextNodeId, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 }]);
    setNextNodeId(nextNodeId + 1);
  };
  const updateNode = (id, updated) => setNodes(nodes.map(n => n.id === id ? updated : n));
  const removeNode = (id) => {
    setNodes(nodes.filter(n => n.id !== id));
    setChannels(channels.filter(c => c.from !== id && c.to !== id));
  };

  // Channel handlers
  const addChannel = () => {
    if (nodes.length < 2) return;
    setChannels([...channels, { id: nextChannelId, from: nodes[0].id, to: nodes[1].id, fiber_length_km: 10, fiber_attenuation_db_per_km: 0.2, wavelength_nm: 1550, fiber_type: "standard_single_mode", phase_flip_prob: 0.05 }]);
    setNextChannelId(nextChannelId + 1);
  };
  const updateChannel = (id, updated) => setChannels(channels.map(c => c.id === id ? updated : c));
  const removeChannel = (id) => setChannels(channels.filter(c => c.id !== id));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSimulate({
      protocol,
      num_pulses: Number(num_pulses),
      pulse_repetition_rate: Number(pulse_repetition_rate),
      phase_flip_prob: Number(phase_flip_prob),
      cow_monitor_pulse_ratio: Number(cow_monitor_pulse_ratio),
      cow_detection_threshold_photons: Number(cow_detection_threshold_photons),
      cow_extinction_ratio_db: Number(cow_extinction_ratio_db),
      nodes: nodes.map(n => ({ ...n, detector_efficiency: Number(n.detector_efficiency), dark_count_rate: Number(n.dark_count_rate), mu: Number(n.mu) })),
      channels: channels.map(c => ({ ...c, fiber_length_km: Number(c.fiber_length_km), fiber_attenuation_db_per_km: Number(c.fiber_attenuation_db_per_km), wavelength_nm: Number(c.wavelength_nm), phase_flip_prob: Number(c.phase_flip_prob) }))
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
        Pulse Repetition Rate (ns):
        <input type="number" value={pulse_repetition_rate} onChange={e => setPulseRepetitionRate(e.target.value)} />
      </label>
      <label>
        Phase Flip Probability (0-1):
        <input type="number" step="0.001" min="0" max="1" value={phase_flip_prob} onChange={e => setPhaseFlipProb(e.target.value)} />
      </label>
      
      {protocol === "cow" && (
        <div style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px' }}>
          <h3>COW Protocol Parameters</h3>
          <label>
            COW Monitor Pulse Ratio:
            <input type="number" step="0.01" value={cow_monitor_pulse_ratio} onChange={e => setCowMonitorPulseRatio(e.target.value)} />
          </label>
          <label>
            COW Detection Threshold (Photons):
            <input type="number" value={cow_detection_threshold_photons} onChange={e => setCowDetectionThresholdPhotons(e.target.value)} />
          </label>
          <label>
            COW Extinction Ratio (dB):
            <input type="number" value={cow_extinction_ratio_db} onChange={e => setCowExtinctionRatioDb(e.target.value)} />
          </label>
        </div>
      )}

      <hr />
      <h3>Nodes</h3>
      {nodes.map(node => (
        <NodeForm key={node.id} node={node} onChange={updateNode} onRemove={removeNode} />
      ))}
      <button type="button" onClick={addNode} style={{ marginTop: 8 }}>Add Node</button>
      <hr />
      <h3>Channels</h3>
      {channels.map(channel => (
        <ChannelForm key={channel.id} channel={channel} nodes={nodes} onChange={updateChannel} onRemove={removeChannel} />
      ))}
      <button type="button" onClick={addChannel} style={{ marginTop: 8 }}>Add Channel</button>
      <hr />
      <button type="submit">Run Simulation</button>
    </form>
  );
} 