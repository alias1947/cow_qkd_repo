import React, { useState } from "react";
import QKDForm from "./components/QKDForm";
import QKDNetwork from "./components/QKDNetwork";
import Results from "./components/Results";
import axios from "axios";
import Button from '@mui/material/Button';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Box from '@mui/material/Box';

function App() {
  const [params, setParams] = useState({ protocol: "dps", cow_monitor_pulse_ratio: 0.1, cow_detection_threshold_photons: 1, cow_extinction_ratio_db: 20 });
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
      setTimeout(() => setProtocolChangeMessage(""), 500);
    }
    
    setParams(formParams);
  };

  const handleNetworkChange = (net) => {
    setNetwork(net);
  };

  const handleSimulate = async () => {
    setResults(null);
    try {
      let payload = { ...params, ...network };
      // For COW, ensure bit_flip_error_prob is set (default 0.05)
      if (payload.protocol === 'cow') {
        if (payload.bit_flip_error_prob === undefined || payload.bit_flip_error_prob === null) {
          payload.bit_flip_error_prob = 0.05;
        }
      }
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
      cow_monitor_pulse_ratio: 0.1, 
      cow_detection_threshold_photons: 1, 
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
    setTimeout(() => setProtocolChangeMessage(""), 500);
  };

  return (
    <div style={{ padding: 32 }}>
      <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
        <img src="/iiserBLogo.jpg" alt="IISERB Logo" style={{ height: 64, width: 64, marginRight: 20, borderRadius: '50%', boxShadow: '0 2px 8px #0002' }} />
        <Typography variant="h3" component="h1" fontWeight={700} color="text.primary" align="center">
          QKD Simulator - IISERB
        </Typography>
      </Box>
      <Divider sx={{ mb: 4 }} />
      <QKDForm params={params} onChange={handleFormChange} />
      
      {protocolChangeMessage && (
        <Typography variant="subtitle1" sx={{
          my: 2,
          px: 2,
          py: 1.5,
          backgroundColor: '#e3f2fd',
          border: '1px solid',
          borderColor: 'primary.main',
          borderRadius: 1,
          color: 'primary.main',
          fontWeight: 500
        }}>
          {protocolChangeMessage}
        </Typography>
      )}
      
      <QKDNetwork key={networkKey} onNetworkChange={handleNetworkChange} protocol={params.protocol} />
      <div style={{ display: 'flex', gap: '16px', margin: '16px 0' }}>
        <Button onClick={handleSimulate} variant="contained" color="primary" sx={{ px: 4, py: 1.5, fontWeight: 600, fontSize: 18 }} startIcon={<PlayArrowIcon />}>Run Simulation</Button>
        <Button onClick={handleReset} variant="outlined" color="secondary" sx={{ px: 3, py: 1.5, fontWeight: 600, fontSize: 16 }} startIcon={<RestartAltIcon />}>Reset All</Button>
      </div>
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
