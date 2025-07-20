import React, { useCallback, useState } from "react";
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  addEdge,
  useNodesState,
  useEdgesState,
} from "react-flow-renderer";
import { v4 as uuidv4 } from 'uuid';
import Button from '@mui/material/Button';
import AddIcon from '@mui/icons-material/Add';
import UndoIcon from '@mui/icons-material/Undo';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Typography from '@mui/material/Typography';

const defaultNodeParams = () => ({
  detector_efficiency: 0.9,
  dark_count_rate: 1e-8,
  mu: 0.2,
  num_pulses: 10000,
  pulse_repetition_rate: 1,
});
const defaultEdgeParams = (protocol) => {
  const params = {
    fiber_length_km: 10,
    fiber_attenuation_db_per_km: 0.2,
    wavelength_nm: 1550,
    fiber_type: "standard_single_mode",
    phase_flip_prob: 0.05,
  };
  if (protocol === 'cow') {
    params.bit_flip_error_prob = 0.05;
  }
  return params;
};

const nodeStyle = {
  background: "#e3f2fd",
  border: "2px solid #1976d2",
  borderRadius: 10,
  width: 90,
  height: 50,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontWeight: 600,
  fontSize: 16,
  color: "#1976d2",
};

function Sidebar({ selected, onChange, onRemove, type, edges, setSelected, setSelectedType, protocol }) {
  if (!selected) {
    return (
      <div style={{ padding: 16, color: '#888' }}>
        <div>Select a node or channel to edit parameters.</div>
        {edges && edges.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <b>Channels:</b>
            <ul style={{ paddingLeft: 16 }}>
              {edges.map(e => (
                <li key={e.id} style={{ marginBottom: 4 }}>
                  Channel {e.id} (Node {e.source} → Node {e.target})
                  <Button variant="outlined" size="small" sx={{ ml: 1 }} onClick={() => { setSelected(e); setSelectedType('edge'); }} startIcon={<EditIcon />}>Edit</Button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }
  if (type === 'node') {
    return (
      <div style={{ padding: 16 }}>
        <Typography variant="subtitle1" fontWeight={600} color="primary.main" gutterBottom>Node {selected.data.label}</Typography>
        <label>Detector Efficiency:<br/>
          <input type="number" step="0.01" value={selected.data.detector_efficiency}
            onChange={e => onChange({ ...selected, data: { ...selected.data, detector_efficiency: Number(e.target.value) } })} />
        </label><br/>
        <label>Dark Count Rate:<br/>
          <input type="number" step="any" value={selected.data.dark_count_rate}
            onChange={e => onChange({ ...selected, data: { ...selected.data, dark_count_rate: Number(e.target.value) } })} />
        </label><br/>
        <label>Mu:<br/>
          <input type="number" step="0.01" value={selected.data.mu}
            onChange={e => onChange({ ...selected, data: { ...selected.data, mu: Number(e.target.value) } })} />
        </label><br/>
        <label>Pulses:<br/>
          <input type="number" step="1" min="1" value={selected.data.num_pulses}
            onChange={e => onChange({ ...selected, data: { ...selected.data, num_pulses: Number(e.target.value) } })} />
        </label><br/>
        <label>Pulse Repetition Rate (ns):<br/>
          <input type="number" step="any" min="0.0001" value={selected.data.pulse_repetition_rate}
            onChange={e => onChange({ ...selected, data: { ...selected.data, pulse_repetition_rate: Number(e.target.value) } })} />
        </label><br/>
        <Button variant="contained" color="error" sx={{ mt: 1 }} onClick={() => onRemove(selected.id)} startIcon={<DeleteIcon />}>Remove Node</Button>
      </div>
    );
  }
  if (type === 'edge') {
    return (
      <div style={{ padding: 16 }}>
        <Typography variant="subtitle1" fontWeight={600} color="primary.main" gutterBottom>Channel {selected.id}</Typography>
        <label>Fiber Length (km):<br/>
          <input type="number" step="0.1" value={selected.data.fiber_length_km}
            onChange={e => onChange({ ...selected, data: { ...selected.data, fiber_length_km: Number(e.target.value) } })} />
        </label><br/>
        <label>Attenuation (dB/km):<br/>
          <input type="number" step="0.01" value={selected.data.fiber_attenuation_db_per_km}
            onChange={e => onChange({ ...selected, data: { ...selected.data, fiber_attenuation_db_per_km: Number(e.target.value) } })} />
        </label><br/>
        <label>Wavelength (nm):<br/>
          <input type="number" step="1" value={selected.data.wavelength_nm}
            onChange={e => onChange({ ...selected, data: { ...selected.data, wavelength_nm: Number(e.target.value) } })} />
        </label><br/>
        <label>Fiber Type:<br/>
          <select value={selected.data.fiber_type} onChange={e => onChange({ ...selected, data: { ...selected.data, fiber_type: e.target.value } })}>
            <option value="standard_single_mode">SMF-28</option>
            <option value="dispersion_shifted">Dispersion Shifted</option>
            <option value="non_zero_dispersion_shifted">Non-Zero Dispersion Shifted</option>
            <option value="photonic_crystal">Photonic Crystal Fiber</option>
          </select>
        </label><br/>
        <label>Phase Flip Probability (0-1):<br/>
          <input type="number" step="0.001" min="0" max="1" value={selected.data.phase_flip_prob}
            onChange={e => onChange({ ...selected, data: { ...selected.data, phase_flip_prob: Number(e.target.value) } })} />
        </label><br/>
        {protocol === 'cow' && (
          <>
            <label>Bit Flip Error Probability (0-1):<br/>
              <input type="number" step="0.01" min="0" max="1" value={selected.data.bit_flip_error_prob ?? 0.05}
                onChange={e => onChange({ ...selected, data: { ...selected.data, bit_flip_error_prob: e.target.value === '' ? 0.05 : Number(e.target.value) } })} />
            </label>
            <br />
            <Button variant="contained" color="error" sx={{ mt: 1 }} onClick={() => onRemove(selected.id)} startIcon={<DeleteIcon />}>Remove Channel</Button>
          </>
        )}
        {protocol !== 'cow' && (
          <Button variant="contained" color="error" sx={{ mt: 1 }} onClick={() => onRemove(selected.id)} startIcon={<DeleteIcon />}>Remove Channel</Button>
        )}
      </div>
    );
  }
  return null;
}

export default function QKDNetwork({ onNetworkChange, protocol }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([
    { id: '1', position: { x: 0, y: 100 }, data: { label: '1', ...defaultNodeParams() }, style: nodeStyle },
    { id: '2', position: { x: 200, y: 100 }, data: { label: '2', ...defaultNodeParams() }, style: nodeStyle },
  ]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selected, setSelected] = useState(null);
  const [selectedType, setSelectedType] = useState(null);
  const [history, setHistory] = useState([]);

  // Helper to push current state to history
  const pushHistory = useCallback(() => {
    setHistory(h => [...h, { nodes: JSON.parse(JSON.stringify(nodes)), edges: JSON.parse(JSON.stringify(edges)) }]);
  }, [nodes, edges]);

  // Undo handler
  const handleUndo = () => {
    setHistory(h => {
      if (h.length === 0) return h;
      const prev = h[h.length - 1];
      setNodes(prev.nodes);
      setEdges(prev.edges);
      return h.slice(0, -1);
    });
    setSelected(null);
    setSelectedType(null);
  };

  // Add node
  const addNode = useCallback(() => {
    pushHistory();
    const newId = uuidv4().slice(0, 8);
    setNodes((nds) => [
      ...nds,
      {
        id: newId,
        position: { x: nds.length * 200, y: 100 },
        data: { label: String(nds.length + 1), ...defaultNodeParams() },
        style: nodeStyle,
      },
    ]);
  }, [setNodes, pushHistory]);

  // Remove node and its edges
  const removeNode = useCallback((id) => {
    pushHistory();
    setNodes((nds) => nds.filter((n) => n.id !== id));
    setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id));
    setSelected(null);
    setSelectedType(null);
  }, [setNodes, setEdges, pushHistory]);

  // Remove edge
  const removeEdge = useCallback((id) => {
    pushHistory();
    setEdges((eds) => eds.filter((e) => e.id !== id));
    setSelected(null);
    setSelectedType(null);
  }, [setEdges, pushHistory]);

  // On connect (draw edge)
  const onConnect = useCallback((params) => {
    pushHistory();
    setEdges((eds) => addEdge({ ...params, id: uuidv4().slice(0, 8), data: { ...defaultEdgeParams(protocol) }, animated: true, style: { stroke: '#333', strokeWidth: 2 } }, eds));
  }, [setEdges, pushHistory, protocol]);

  // On element click
  const onElementClick = useCallback((event, element) => {
    if (element.source) {
      setSelected(edges.find(e => e.id === element.id));
      setSelectedType('edge');
    } else {
      setSelected(nodes.find(n => n.id === element.id));
      setSelectedType('node');
    }
  }, [nodes, edges]);

  // On node/edge parameter change
  const onSidebarChange = (updated) => {
    pushHistory();
    if (selectedType === 'node') {
      setNodes((nds) => nds.map(n => n.id === updated.id ? updated : n));
      setSelected(updated);
    } else if (selectedType === 'edge') {
      setEdges((eds) => eds.map(e => e.id === updated.id ? updated : e));
      setSelected(updated);
    }
  };

  // Notify parent of network change
  React.useEffect(() => {
    if (onNetworkChange) {
      // Convert nodes/edges to simulation format
      onNetworkChange({
        nodes: nodes.map(n => ({
          id: Number(n.data.label),
          detector_efficiency: n.data.detector_efficiency,
          dark_count_rate: n.data.dark_count_rate,
          mu: n.data.mu,
          num_pulses: n.data.num_pulses,
          pulse_repetition_rate: n.data.pulse_repetition_rate,
        })),
        channels: edges.map((e, idx) => {
          const channel = {
            id: idx + 1,
            from: Number(nodes.find(n => n.id === e.source).data.label),
            to: Number(nodes.find(n => n.id === e.target).data.label),
            fiber_length_km: e.data.fiber_length_km,
            fiber_attenuation_db_per_km: e.data.fiber_attenuation_db_per_km,
            wavelength_nm: e.data.wavelength_nm,
            fiber_type: e.data.fiber_type,
            phase_flip_prob: e.data.phase_flip_prob,
          };
          if (protocol === 'cow' && e.data.bit_flip_error_prob !== undefined) {
            channel.bit_flip_error_prob = e.data.bit_flip_error_prob;
          }
          return channel;
        }),
      });
    }
  }, [nodes, edges, onNetworkChange, protocol]);

  return (
    <div style={{ display: 'flex', height: 420, marginBottom: 32, border: '1px solid #ccc', borderRadius: 8, background: '#f7fafd' }}>
      <div style={{ flex: 1, position: 'relative' }}>
        <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 10, display: 'flex', gap: 8 }}>
          <Button onClick={addNode} variant="contained" color="primary" startIcon={<AddIcon />}>Add Node</Button>
          <Button onClick={handleUndo} variant="contained" color="secondary" disabled={history.length === 0} startIcon={<UndoIcon />}>Undo</Button>
        </div>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onElementClick}
          onEdgeClick={onElementClick}
          fitView
        >
          <MiniMap />
          <Controls />
          <Background color="#e3f2fd" gap={16} />
        </ReactFlow>
      </div>
      <div style={{ width: 320, borderLeft: '1px solid #bbb', background: '#fff', borderRadius: '0 8px 8px 0', boxShadow: '-2px 0 8px #0001' }}>
        <Sidebar
          selected={selected}
          onChange={onSidebarChange}
          onRemove={selectedType === 'node' ? removeNode : removeEdge}
          type={selectedType}
          edges={edges}
          setSelected={setSelected}
          setSelectedType={setSelectedType}
          protocol={protocol}
        />
      </div>
    </div>
  );
} 