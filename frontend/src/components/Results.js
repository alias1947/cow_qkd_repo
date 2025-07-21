import React, { useState, useEffect } from "react";
import Button from '@mui/material/Button';
import ListAltIcon from '@mui/icons-material/ListAlt';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import ScienceIcon from '@mui/icons-material/Science';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';

// Helper to format key as string
const formatKey = (key) => {
  if (!key) return "N/A";
  return Array.isArray(key) ? key.slice(0, 100).join("") + (key.length > 100 ? "..." : "") : String(key);
};

// Helper to format percentage
const formatPercent = (value) => (value * 100).toFixed(2) + "%";

// Helper for scientific notation
const formatScientific = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return value.toExponential(2);
};

 // Helper to format SKR in k, M, or G units
function formatSKR(value) {
  if (value === undefined || value === null) return 'N/A';
  if (value >= 1e9) return (value / 1e9).toFixed(2) + ' Gbps';
  if (value >= 1e6) return (value / 1e6).toFixed(2) + ' Mbps';
  if (value >= 1e3) return (value / 1e3).toFixed(2) + ' kbps';
  return value + ' bps';
}

export default function Results({ results }) {
  const [tab, setTab] = useState("summary");
  const [selectedChannelId, setSelectedChannelId] = useState(null);

  useEffect(() => {
    if (results && results.length > 0) {
      setSelectedChannelId(results[0].channel_id);
    }
  }, [results]);

  if (!results || results.length === 0) {
    return <div style={{ color: "red" }}>No results to display.</div>;
  }
  if (results[0].error) return <div style={{ color: "red" }}>{results[0].error}</div>;

  const selectedResult = results.find(r => r.channel_id === selectedChannelId);

  return (
    <div style={{ border: "1px solid #ccc", padding: 16, borderRadius: 8, backgroundColor: "#fff" }}>
      <Typography variant="h4" component="h2" gutterBottom fontWeight={700} color="primary.main">
        Simulation Results
      </Typography>
      <div style={{ marginBottom: 16, borderBottom: "1px solid #eee", paddingBottom: 8 }}>
        <Button onClick={() => setTab("summary")} disabled={tab === "summary"} variant="contained" color="primary" sx={{ mr: 1 }} startIcon={<ListAltIcon />}>Summary</Button>
        <Button onClick={() => setTab("keys")} disabled={tab === "keys"} variant="contained" color="primary" sx={{ mr: 1 }} startIcon={<VpnKeyIcon />}>Key Comparison</Button>
        <Button onClick={() => setTab("theory")} disabled={tab === "theory"} variant="contained" color="primary" startIcon={<ScienceIcon />}>Theory Details</Button>
      </div>

      {(tab === "keys" || tab === "theory") && (
        <Box mb={2}>
          <FormControl size="small" sx={{ minWidth: 240 }}>
            <InputLabel id="channel-select-label">Select Channel</InputLabel>
            <Select
              labelId="channel-select-label"
              value={selectedChannelId}
              label="Select Channel"
              onChange={e => setSelectedChannelId(Number(e.target.value))}
            >
              {results.map(r => (
                <MenuItem key={r.channel_id} value={r.channel_id}>
                  Channel {r.channel_id} (Node {r.from} to Node {r.to})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      )}

      {tab === "summary" && (
         <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #000" }}>
                <th style={{ padding: 8, textAlign: "left" }}>Channel</th>
                <th style={{ padding: 8, textAlign: "left" }}>Protocol</th>
                <th style={{ padding: 8, textAlign: "left" }}>QBER</th>
                <th style={{ padding: 8, textAlign: "left" }}>Final Key Len</th>
                <th style={{ padding: 8, textAlign: "left" }}>SKR</th>
                <th style={{ padding: 8, textAlign: "left" }}>Compliance</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.channel_id} style={{ borderBottom: "1px solid #ccc" }}>
                  <td style={{ padding: 8 }}>{`Channel ${result.channel_id} (Node ${result.from} -> Node ${result.to})`}</td>
                  <td style={{ padding: 8 }}>{result.protocol.toUpperCase()}</td>
                  <td style={{ padding: 8 }}>{formatPercent(result.qber)}</td>
                  <td style={{ padding: 8 }}>{result.final_key_length}</td>
                  <td style={{ padding: 8 }}>{formatSKR(result.secure_key_rate_bps)}</td>
                  <td style={{ padding: 8, color: result.theory_compliance ? "green" : "red" }}>
                    {result.theory_message}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
      )}

      {tab === "keys" && selectedResult && (
        <div>
          <Typography variant="h6" component="h3" gutterBottom fontWeight={600} color="secondary.main">
            Key Comparison for Channel {selectedResult.channel_id} (First 100 bits)
          </Typography>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div><b>Alice's Key:</b><div style={{ wordBreak: "break-all", fontFamily: "monospace" }}>{formatKey(selectedResult.alice_key)}</div></div>
            <div><b>Bob's Key:</b><div style={{ wordBreak: "break-all", fontFamily: "monospace" }}>{formatKey(selectedResult.bob_key)}</div></div>
          </div>
        </div>
      )}

      {tab === "theory" && selectedResult && (
        <div>
          <Typography variant="h6" component="h3" gutterBottom fontWeight={600} color="secondary.main">
            Theory Details for Channel {selectedResult.channel_id}
          </Typography>
           <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
              <div>
                <Typography variant="subtitle1" fontWeight={600} color="primary.main">Protocol Details</Typography>
                <div><b>Encoding:</b> Phase difference between consecutive pulses (0, π)</div>
                <div><b>Detection:</b> Mach-Zehnder interferometer</div>
              </div>
              <div>
                <Typography variant="subtitle1" fontWeight={600} color="primary.main">Channel Parameters</Typography>
                <div><b>Fiber Length:</b> {selectedResult.parameters.channel.fiber_length_km} km</div>
                <div><b>Attenuation:</b> {selectedResult.parameters.channel.fiber_attenuation_db_per_km} dB/km</div>
              </div>
               <div>
                <Typography variant="subtitle1" fontWeight={600} color="primary.main">Node {selectedResult.from} (Alice) Parameters</Typography>
                <div><b>Avg. Photon Number (μ):</b> {selectedResult.parameters.node_a.mu}</div>
              </div>
              <div>
                <Typography variant="subtitle1" fontWeight={600} color="primary.main">Node {selectedResult.to} (Bob) Parameters</Typography>
                <div><b>Detector Efficiency:</b> {formatPercent(selectedResult.parameters.node_b.detector_efficiency)}</div>
                <div><b>Dark Count Rate:</b> {formatScientific(selectedResult.parameters.node_b.dark_count_rate)}</div>
              </div>
           </div>
        </div>
      )}
    </div>
  );
} 