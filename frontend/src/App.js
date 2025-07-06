import React, { useState } from "react";
import QKDForm from "./components/QKDForm";
import QKDNetwork from "./components/QKDNetwork";
import Results from "./components/Results";
import axios from "axios";

function App() {
  const [params, setParams] = useState({ protocol: "dps", num_pulses: 10000, pulse_repetition_rate: 1, phase_flip_prob: 0.05, cow_monitor_pulse_ratio: 0.1, cow_detection_threshold_photons: 0, cow_extinction_ratio_db: 20 });
  const [network, setNetwork] = useState({ nodes: [ { id: 1, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 }, { id: 2, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 } ], channels: [] });
  const [results, setResults] = useState(null);
  const [networkKey, setNetworkKey] = useState(0); // Key to force network reset
  const [protocolChangeMessage, setProtocolChangeMessage] = useState("");

  const handleFormChange = (formParams) => {
    // Check if protocol has changed
    if (formParams.protocol !== params.protocol) {
      // Reset everything when protocol changes
      console.log(`Protocol changed from ${params.protocol} to ${formParams.protocol}`);
      
      // Reset network to default state
      setNetwork({ 
        nodes: [ 
          { id: 1, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 }, 
          { id: 2, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 } 
        ], 
        channels: [] 
      });
      
      // Force network component reset by changing key
      setNetworkKey(prev => prev + 1);
      
      // Clear results
      setResults(null);
      
      // Show protocol change message
      setProtocolChangeMessage(`Protocol changed to ${formParams.protocol.toUpperCase()}-QKD. Network topology and results have been reset.`);
      
      // Clear message after 3 seconds
      setTimeout(() => setProtocolChangeMessage(""), 3000);
    }
    
    setParams(formParams);
  };

  const handleNetworkChange = (net) => {
    setNetwork(net);
  };

  const handleSimulate = async () => {
    setResults(null);
    try {
      const payload = { ...params, ...network };
      console.log("Sending to backend:", payload);
      const res = await axios.post("http://localhost:8000/simulate", payload);
      if (res.data && Array.isArray(res.data.results)) {
        setResults(res.data.results);
      } else {
        setResults([{ error: "Invalid response from server." }]);
      }
    } catch (error) {
      console.error("Simulation request failed:", error);
      const errorMsg = error.response ? JSON.stringify(error.response.data) : error.message;
      setResults([{ error: `Request Failed: ${errorMsg}` }]);
    }
  };

  const handleReset = () => {
    // Reset everything to default state
    setParams({ 
      protocol: "dps", 
      num_pulses: 10000, 
      pulse_repetition_rate: 1, 
      phase_flip_prob: 0.05, 
      cow_monitor_pulse_ratio: 0.1, 
      cow_detection_threshold_photons: 0, 
      cow_extinction_ratio_db: 20 
    });
    setNetwork({ 
      nodes: [ 
        { id: 1, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 }, 
        { id: 2, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 } 
      ], 
      channels: [] 
    });
    setResults(null);
    setNetworkKey(prev => prev + 1);
    setProtocolChangeMessage("Application reset to default state.");
    setTimeout(() => setProtocolChangeMessage(""), 3000);
  };

  return (
    <div style={{ padding: 32 }}>
      <h1>QKD Simulator - IISERB</h1>
      <QKDForm params={params} onChange={handleFormChange} />
      
      {protocolChangeMessage && (
        <div style={{ 
          margin: '16px 0', 
          padding: '12px 16px', 
          backgroundColor: '#e3f2fd', 
          border: '1px solid #1976d2', 
          borderRadius: '4px', 
          color: '#1976d2',
          fontWeight: 500
        }}>
          {protocolChangeMessage}
        </div>
      )}
      
      <QKDNetwork key={networkKey} onNetworkChange={handleNetworkChange} />
      <div style={{ display: 'flex', gap: '16px', margin: '16px 0' }}>
        <button onClick={handleSimulate} className="qkd-btn" style={{ padding: '12px 32px', fontWeight: 600, fontSize: 18 }}>Run Simulation</button>
        <button onClick={handleReset} style={{ 
          padding: '12px 24px', 
          fontWeight: 600, 
          fontSize: 16,
          backgroundColor: '#f5f5f5',
          border: '1px solid #ccc',
          borderRadius: '4px',
          cursor: 'pointer'
        }}>Reset All</button>
      </div>
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
