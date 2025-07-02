import React, { useState } from "react";
import QKDForm from "./QKDForm";
import QKDNetwork from "./QKDNetwork";
import Results from "./Results";
import axios from "axios";

function App() {
  const [params, setParams] = useState({ protocol: "dps", num_pulses: 10000, pulse_repetition_rate: 1, phase_flip_prob: 0.05, cow_monitor_pulse_ratio: 0.1, cow_detection_threshold_photons: 0, cow_extinction_ratio_db: 20 });
  const [network, setNetwork] = useState({ nodes: [ { id: 1, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 }, { id: 2, detector_efficiency: 0.9, dark_count_rate: 1e-8, mu: 0.2 } ], channels: [] });
  const [results, setResults] = useState(null);

  const handleFormChange = (formParams) => {
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

  return (
    <div style={{ padding: 32 }}>
      <h1>QKD Simulator - IISERB</h1>
      <QKDForm params={params} onChange={handleFormChange} />
      <QKDNetwork onNetworkChange={handleNetworkChange} />
      <button onClick={handleSimulate} className="qkd-btn" style={{ margin: '16px 0', padding: '12px 32px', fontWeight: 600, fontSize: 18 }}>Run Simulation</button>
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
