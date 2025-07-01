import React, { useState } from "react";
import QKDForm from "./QKDForm";
import QKDNetwork from "./QKDNetwork";
import Results from "./Results";
import axios from "axios";

function App() {
  const [params, setParams] = useState(null);
  const [results, setResults] = useState(null);

  const handleSimulate = async (formParams) => {
    setParams(formParams);
    setResults(null);
    try {
      console.log("Sending to backend:", formParams);
      const res = await axios.post("http://localhost:8000/simulate", formParams);
      console.log("Received from backend:", res.data);
      // Ensure we are setting the array to the results state
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
      <QKDForm onSimulate={handleSimulate} />
      {params && <QKDNetwork nodes={params.nodes} links={params.channels} protocol={params.protocol} />}
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
