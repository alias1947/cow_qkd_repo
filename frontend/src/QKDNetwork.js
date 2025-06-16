import React from "react";
import ReactFlow, { MiniMap, Controls } from "react-flow-renderer";

export default function QKDNetwork({ protocol }) {
  // Just Alice and Bob for now
  const nodes = [
    { id: "1", data: { label: "Alice" }, position: { x: 0, y: 100 }, style: { background: "#aaf" } },
    { id: "2", data: { label: "Bob" }, position: { x: 300, y: 100 }, style: { background: "#faa" } },
  ];
  const edges = [
    { id: "e1-2", source: "1", target: "2", label: protocol === "dps" ? "DPS-QKD" : "COW-QKD" }
  ];
  return (
    <div style={{ height: 200, marginBottom: 32 }}>
      <ReactFlow nodes={nodes} edges={edges}>
        <MiniMap />
        <Controls />
      </ReactFlow>
    </div>
  );
} 