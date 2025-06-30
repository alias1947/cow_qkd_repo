import React, { useState } from "react";

export default function Results({ results }) {
  const [tab, setTab] = useState("summary");
  if (results.error) return <div style={{ color: "red" }}>{results.error}</div>;

  // Helper to format key as string
  const formatKey = (key) => {
    if (!key) return "N/A (no key generated or returned)";
    return Array.isArray(key) ? key.slice(0, 100).join("") + (key.length > 100 ? "..." : "") : String(key);
  };

  // Helper to format percentage
  const formatPercent = (value) => (value * 100).toFixed(2) + "%";

  // Helper to format scientific notation
  const formatScientific = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return value.toExponential(2);
  };

  return (
    <div style={{ border: "1px solid #ccc", padding: 16, borderRadius: 8, backgroundColor: "#fff" }}>
      <h2>Simulation Results</h2>
      <div style={{ marginBottom: 16, borderBottom: "1px solid #eee", paddingBottom: 8 }}>
        <button 
          onClick={() => setTab("summary")} 
          disabled={tab === "summary"}
          style={{ 
            padding: "8px 16px",
            marginRight: 8,
            backgroundColor: tab === "summary" ? "#007bff" : "#f8f9fa",
            color: tab === "summary" ? "white" : "black",
            border: "1px solid #dee2e6",
            borderRadius: 4,
            cursor: "pointer"
          }}
        >
          Summary
        </button>
        <button 
          onClick={() => setTab("keys")} 
          disabled={tab === "keys"}
          style={{ 
            padding: "8px 16px",
            marginRight: 8,
            backgroundColor: tab === "keys" ? "#007bff" : "#f8f9fa",
            color: tab === "keys" ? "white" : "black",
            border: "1px solid #dee2e6",
            borderRadius: 4,
            cursor: "pointer"
          }}
        >
          Key Comparison
        </button>
        <button 
          onClick={() => setTab("theory")} 
          disabled={tab === "theory"}
          style={{ 
            padding: "8px 16px",
            backgroundColor: tab === "theory" ? "#007bff" : "#f8f9fa",
            color: tab === "theory" ? "white" : "black",
            border: "1px solid #dee2e6",
            borderRadius: 4,
            cursor: "pointer"
          }}
        >
          Theory Details
        </button>
      </div>

      {tab === "summary" && (
        <div>
          <div style={{ 
            padding: 16, 
            backgroundColor: "#f8f9fa", 
            borderRadius: 4, 
            marginBottom: 16 
          }}>
            <h3 style={{ marginTop: 0 }}>Protocol: {results.protocol.toUpperCase()}</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
              <div>
                <div><b>Sifted Key Length:</b> {results.sifted_key_length}</div>
                <div><b>QBER:</b> {formatPercent(results.qber)}</div>
                {/* <div><b>Errors:</b> {results.num_errors}</div> */}
                <div><b>Secret Key Length:</b> {results.final_key_length}</div>
                <div><b>Secure Key Rate (bps):</b> {results.secure_key_rate_bps ? results.secure_key_rate_bps.toFixed(2) : 'N/A'}</div>
              </div>
              <div style={{ 
                padding: 12, 
                backgroundColor: results.theory_compliance ? "#d4edda" : "#f8d7da",
                borderRadius: 4,
                border: `1px solid ${results.theory_compliance ? "#c3e6cb" : "#f5c6cb"}`
              }}>
                <b>{results.theory_message}</b>
              </div>
            </div>
          </div>

          {/* Fiber Information Section */}
          {results.fiber_type && (
            <div style={{ 
              padding: 16, 
              backgroundColor: "#e3f2fd", 
              borderRadius: 4, 
              marginBottom: 16,
              border: "1px solid #bbdefb"
            }}>
              <h3 style={{ marginTop: 0, color: "#1976d2" }}>Fiber Configuration</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
                <div>
                  <div><b>Fiber Type:</b> {results.fiber_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                  <div><b>Length:</b> {results.distance_km} km</div>
                  <div><b>Wavelength:</b> {results.wavelength_nm} nm</div>
                </div>
                <div>
                  <div><b>Attenuation:</b> {results.fiber_attenuation_db_per_km} dB/km</div>
                  <div><b>Total Loss:</b> {(results.distance_km * results.fiber_attenuation_db_per_km).toFixed(2)} dB</div>
                </div>
                <div>
                  <div><b>Transmission:</b> {formatPercent(Math.pow(10, -(results.distance_km * results.fiber_attenuation_db_per_km) / 10))}</div>
                </div>
              </div>
            </div>
          )}

          {results.postprocessing && (
            <div style={{ marginTop: 16 }}>
              <h3>Postprocessing Breakdown</h3>
              <div style={{ 
                display: "grid", 
                gridTemplateColumns: "repeat(3, 1fr)", 
                gap: 16,
                marginTop: 8 
              }}>
                <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
                  <div><b>Parameter Estimation</b></div>
                  <div>Key Length: {results.postprocessing.after_parameter_estimation}</div>
                  <div>DR: {formatPercent(results.postprocessing.dr)}</div>
                </div>
                <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
                  <div><b>Error Correction</b></div>
                  <div>Key Length: {results.postprocessing.after_error_correction}</div>
                  <div>EC Fraction: {formatPercent(results.postprocessing.ec_fraction)}</div>
                </div>
                <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
                  <div><b>Privacy Amplification</b></div>
                  <div>Key Length: {results.postprocessing.after_privacy_amplification}</div>
                  <div>PA Ratio: {formatPercent(results.postprocessing.privacy_amplification_ratio)}</div>
                </div>
              </div>
            </div>
          )}

          {results.monitoring_info && (
            <div style={{ marginTop: 16 }}>
              <h3>COW Monitoring Results</h3>
              <div style={{ 
                display: "grid", 
                gridTemplateColumns: "repeat(2, 1fr)", 
                gap: 16,
                marginTop: 8 
              }}>
                <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
                  <div><b>Monitor Pairs</b></div>
                  <div>Successful: {results.monitoring_info.successful_monitor_pairs}</div>
                  <div>Attempted: {results.monitoring_info.attempted_monitor_pairs}</div>
                  <div>Success Rate: {formatPercent(
                    results.monitoring_info.successful_monitor_pairs / 
                    results.monitoring_info.attempted_monitor_pairs
                  )}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === "keys" && (
        <div>
          <h3>Key Comparison (First 100 bits)</h3>
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(2, 1fr)", 
            gap: 16,
            marginTop: 8 
          }}>
            <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
              <b>Alice's Key:</b>
              <div style={{ 
                wordBreak: "break-all", 
                fontFamily: "monospace",
                fontSize: "14px",
                marginTop: 8,
                padding: 8,
                backgroundColor: "#fff",
                borderRadius: 4
              }}>
                {formatKey(results.alice_key)}
              </div>
            </div>
            <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
              <b>Bob's Key:</b>
              <div style={{ 
                wordBreak: "break-all", 
                fontFamily: "monospace",
                fontSize: "14px",
                marginTop: 8,
                padding: 8,
                backgroundColor: "#fff",
                borderRadius: 4
              }}>
                {formatKey(results.bob_key)}
              </div>
            </div>
          </div>
          <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>
            (Only the first 100 bits are shown for readability.)
          </div>
        </div>
      )}

      {tab === "theory" && (
        <div>
          <h3>Theory Details</h3>
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(2, 1fr)", 
            gap: 16,
            marginTop: 8 
          }}>
            <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
              <h4>Protocol Details</h4>
              {results.protocol === "dps" ? (
                <>
                  <div><b>Encoding:</b> Phase difference between consecutive pulses (0, π)</div>
                  <div><b>Detection:</b> Mach-Zehnder interferometer with two detectors</div>
                  <div><b>Sifting:</b> Based on detector clicks and phase difference</div>
                </>
              ) : (
                <>
                  <div><b>Encoding:</b> Vacuum + coherent pulse, intensity modulated</div>
                  <div><b>Detection:</b> Single detector with threshold</div>
                  <div><b>Sifting:</b> Keep bits where Alice and Bob agree on data pulses</div>
                  <div><b>Monitoring:</b> Pairs of monitoring pulses to detect eavesdropping</div>
                </>
              )}
            </div>
            <div style={{ padding: 12, backgroundColor: "#e9ecef", borderRadius: 4 }}>
              <h4>Physical Parameters</h4>
              <div><b>Average Photon Number (μ):</b> {results.mu}</div>
              <div><b>Detector Efficiency:</b> {formatPercent(results.detector_efficiency)}</div>
              <div><b>Dark Count Rate:</b> {formatScientific(results.dark_count_rate)} per ns</div>
              <div><b>Distance:</b> {results.distance_km} km</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 