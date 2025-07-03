import React, { useState, useEffect } from "react";

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
      <h2>Simulation Results</h2>
      <div style={{ marginBottom: 16, borderBottom: "1px solid #eee", paddingBottom: 8 }}>
        <button onClick={() => setTab("summary")} disabled={tab === "summary"} style={{ marginRight: 8 }}>Summary</button>
        <button onClick={() => setTab("keys")} disabled={tab === "keys"} style={{ marginRight: 8 }}>Key Comparison</button>
        <button onClick={() => setTab("theory")} disabled={tab === "theory"}>Theory Details</button>
      </div>

      {(tab === "keys" || tab === "theory") && (
        <div style={{ marginBottom: 16 }}>
          <label>Select Channel: 
            <select value={selectedChannelId} onChange={e => setSelectedChannelId(Number(e.target.value))}>
              {results.map(r => (
                <option key={r.channel_id} value={r.channel_id}>
                  Channel {r.channel_id} (Node {r.from} to Node {r.to})
                </option>
              ))}
            </select>
          </label>
        </div>
      )}

      {tab === "summary" && (
         <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #000" }}>
                <th style={{ padding: 8, textAlign: "left" }}>Channel</th>
                <th style={{ padding: 8, textAlign: "left" }}>Protocol</th>
                <th style={{ padding: 8, textAlign: "left" }}>QBER</th>
                <th style={{ padding: 8, textAlign: "left" }}>Final Key Len</th>
                <th style={{ padding: 8, textAlign: "left" }}>SKR (bps)</th>
                <th style={{ padding: 8, textAlign: "left" }}>Compliance</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.channel_id} style={{ borderBottom: "1px solid #ccc" }}>
                  <td style={{ padding: 8 }}>{`Node ${result.from} -> Node ${result.to}`}</td>
                  <td style={{ padding: 8 }}>{result.protocol.toUpperCase()}</td>
                  <td style={{ padding: 8 }}>{formatPercent(result.qber)}</td>
                  <td style={{ padding: 8 }}>{result.final_key_length}</td>
                  <td style={{ padding: 8 }}>{result.secure_key_rate_bps ? result.secure_key_rate_bps.toFixed(2) : 'N/A'}</td>
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
          <h3>Key Comparison for Channel {selectedResult.channel_id} (First 100 bits)</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div><b>Alice's Key:</b><div style={{ wordBreak: "break-all", fontFamily: "monospace" }}>{formatKey(selectedResult.alice_key)}</div></div>
            <div><b>Bob's Key:</b><div style={{ wordBreak: "break-all", fontFamily: "monospace" }}>{formatKey(selectedResult.bob_key)}</div></div>
          </div>
        </div>
      )}

      {tab === "theory" && selectedResult && (
        <div>
          <h3>Theory Details for Channel {selectedResult.channel_id}</h3>
           <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
              <div>
                <h4>Protocol Details</h4>
                <div><b>Encoding:</b> Phase difference between consecutive pulses (0, π)</div>
                <div><b>Detection:</b> Mach-Zehnder interferometer</div>
              </div>
              <div>
                <h4>Channel Parameters</h4>
                <div><b>Fiber Length:</b> {selectedResult.parameters.channel.fiber_length_km} km</div>
                <div><b>Attenuation:</b> {selectedResult.parameters.channel.fiber_attenuation_db_per_km} dB/km</div>
              </div>
               <div>
                <h4>Node {selectedResult.from} (Alice) Parameters</h4>
                <div><b>Avg. Photon Number (μ):</b> {selectedResult.parameters.node_a.mu}</div>
              </div>
              <div>
                <h4>Node {selectedResult.to} (Bob) Parameters</h4>
                <div><b>Detector Efficiency:</b> {formatPercent(selectedResult.parameters.node_b.detector_efficiency)}</div>
                <div><b>Dark Count Rate:</b> {formatScientific(selectedResult.parameters.node_b.dark_count_rate)}</div>
              </div>
           </div>
        </div>
      )}
    </div>
  );
} 