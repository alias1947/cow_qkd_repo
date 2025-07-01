import React from "react";
import ReactFlow, { MiniMap, Controls } from "react-flow-renderer";

export default function QKDNetwork({ nodes: nodeData, links: linkData, protocol }) {
  // Spread nodes horizontally for clarity
  const nodes = nodeData.map((node, i) => ({
    id: String(node.id),
    data: { label: `Node ${node.id}` },
    position: { x: i * 200, y: 100 },
    style: { background: "#aaf", border: '2px solid #333', borderRadius: 8, width: 80, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center' }
  }));

  const edges = linkData.map(link => ({
    id: `e${link.from}-${link.to}`,
    source: String(link.from),
    target: String(link.to),
    label: `${protocol.toUpperCase()}-QKD (Ch ${link.id})`,
    animated: true,
    style: { stroke: '#333', strokeWidth: 2 },
    labelStyle: { fill: '#333', fontWeight: 600 }
  }));

  return (
    <div style={{ height: 400, marginBottom: 32, border: '1px solid #ccc', borderRadius: 8 }}>
      <h3>Network Topology</h3>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <MiniMap />
        <Controls />
      </ReactFlow>
    </div>
  );
} 