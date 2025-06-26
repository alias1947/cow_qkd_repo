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
    const res = await axios.post("http://localhost:8000/simulate", formParams);
    setResults(res.data);
  };

  return (
    <div style={{ padding: 32 }}>
      <h1>QKD Simulator - IISERB</h1>
      <QKDForm onSimulate={handleSimulate} />
      {params && <QKDNetwork protocol={params.protocol} />}
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
