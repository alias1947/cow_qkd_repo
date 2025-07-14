from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from simulation.Network import Network
from main import calculate_qber, postprocessing

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NodeModel(BaseModel):
    id: int
    detector_efficiency: float
    dark_count_rate: float
    mu: float
    num_pulses: int
    pulse_repetition_rate: float

class ChannelModel(BaseModel):
    id: int
    from_: int = Field(..., alias='from')
    to: int
    fiber_length_km: float
    fiber_attenuation_db_per_km: float
    wavelength_nm: int
    fiber_type: str
    phase_flip_prob: float = 0.05
    bit_flip_error_prob: Optional[float] = None  # Optional per-channel bit flip error for COW

class SimParams(BaseModel):
    protocol: str
    nodes: List[NodeModel]
    channels: List[ChannelModel]
    # COW-specific
    cow_monitor_pulse_ratio: float
    cow_detection_threshold_photons: float = 1
    cow_extinction_ratio_db: float

@app.get("/")
def read_root():
    return {"message": "QKD Simulation API"}

@app.post("/simulate")
def simulate(params: SimParams):
    """
    Multi-node DPS simulation endpoint.
    """
    net = Network()
    node_map = {}
    # Add all nodes
    for n in params.nodes:
        node = net.add_node(
            f"Node_{n.id}",
            avg_photon_number=n.mu,
            detector_efficiency=n.detector_efficiency,
            dark_count_rate=n.dark_count_rate
        )
        node_map[n.id] = node

    results = []
    if params.protocol == "dps":
        # For each channel, run DPS
        for ch in params.channels:
            node_a = node_map.get(ch.from_)
            node_b = node_map.get(ch.to)
            if not node_a or not node_b:
                continue
            net.connect_nodes(
                node_a.node_id, node_b.node_id,
                distance_km=ch.fiber_length_km,
                attenuation_db_per_km=ch.fiber_attenuation_db_per_km
            )
            # Use node-specific and channel-specific params
            alice_key, bob_key = node_a.generate_and_share_key(
                node_b,
                next(n.num_pulses for n in params.nodes if n.id == ch.from_),
                next(n.pulse_repetition_rate for n in params.nodes if n.id == ch.from_),
                phase_flip_prob=ch.phase_flip_prob
            )
            qber, num_errors = calculate_qber(alice_key, bob_key)
            final_key_len, postproc = postprocessing(len(alice_key), qber)
            total_time_s = (next(n.num_pulses for n in params.nodes if n.id == ch.from_) * next(n.pulse_repetition_rate for n in params.nodes if n.id == ch.from_)) / 1e9 if next(n.num_pulses for n in params.nodes if n.id == ch.from_) > 0 else 0
            secure_key_rate_bps = final_key_len / total_time_s if total_time_s > 0 else 0
            theory_compliance = (0.03 <= qber <= 0.10)
            theory_message = "QBER is within the practical range (3-10%) for QKD." if theory_compliance else f"WARNING: QBER ({qber:.4f}) is outside the practical range for QKD."
            
            # Find the original node and channel data to include in the results
            node_a_params = next((n for n in params.nodes if n.id == ch.from_), None)
            node_b_params = next((n for n in params.nodes if n.id == ch.to), None)

            results.append({
                "channel_id": ch.id,
                "from": ch.from_,
                "to": ch.to,
                "protocol": "dps",
                "qber": qber,
                "final_key_length": final_key_len,
                "secure_key_rate_bps": secure_key_rate_bps,
                "sifted_key_length": len(alice_key),
                "num_errors": num_errors,
                "postprocessing": postproc,
                "theory_compliance": theory_compliance,
                "theory_message": theory_message,
                "alice_key": alice_key,
                "bob_key": bob_key,
                "parameters": {
                    "node_a": node_a_params.dict() if node_a_params else {},
                    "node_b": node_b_params.dict() if node_b_params else {},
                    "channel": ch.dict()
                }
            })

    elif params.protocol == "cow":
        # Run COW simulation for each channel
        for ch in params.channels:
            node_a = node_map.get(ch.from_)
            node_b = node_map.get(ch.to)
            if not node_a or not node_b:
                continue

            net.connect_nodes(
                node_a.node_id, node_b.node_id,
                distance_km=ch.fiber_length_km,
                attenuation_db_per_km=ch.fiber_attenuation_db_per_km
            )

            # Use only per-channel bit_flip_error_prob (no global fallback)
            alice_key, bob_key = node_a.generate_and_share_key_cow(
                node_b,
                next(n.num_pulses for n in params.nodes if n.id == ch.from_),
                next(n.pulse_repetition_rate for n in params.nodes if n.id == ch.from_),
                monitor_pulse_ratio=params.cow_monitor_pulse_ratio,
                detection_threshold_photons=int(params.cow_detection_threshold_photons),
                phase_flip_prob=ch.phase_flip_prob,
                bit_flip_error_prob=ch.bit_flip_error_prob
            )

            qber, num_errors = calculate_qber(alice_key, bob_key)
            final_key_len, postproc = postprocessing(len(alice_key), qber)
            total_time_s = (next(n.num_pulses for n in params.nodes if n.id == ch.from_) * next(n.pulse_repetition_rate for n in params.nodes if n.id == ch.from_)) / 1e9 if next(n.num_pulses for n in params.nodes if n.id == ch.from_) > 0 else 0
            secure_key_rate_bps = final_key_len / total_time_s if total_time_s > 0 else 0
            theory_compliance = (0.03 <= qber <= 0.10)
            theory_message = "QBER is within the practical range (3-10%) for QKD." if theory_compliance else f"WARNING: QBER ({qber:.4f}) is outside the practical range for QKD."

            node_a_params = next((n for n in params.nodes if n.id == ch.from_), None)
            node_b_params = next((n for n in params.nodes if n.id == ch.to), None)

            results.append({
                "channel_id": ch.id,
                "from": ch.from_,
                "to": ch.to,
                "protocol": "cow",
                "qber": qber,
                "final_key_length": final_key_len,
                "secure_key_rate_bps": secure_key_rate_bps,
                "sifted_key_length": len(alice_key),
                "num_errors": num_errors,
                "postprocessing": postproc,
                "theory_compliance": theory_compliance,
                "theory_message": theory_message,
                "alice_key": alice_key,
                "bob_key": bob_key,
                "parameters": {
                    "node_a": node_a_params.dict() if node_a_params else {},
                    "node_b": node_b_params.dict() if node_b_params else {},
                    "channel": ch.dict(),
                    "cow_globals": {
                        "monitor_pulse_ratio": params.cow_monitor_pulse_ratio,
                        "detection_threshold_photons": params.cow_detection_threshold_photons,
                        "extinction_ratio_db": params.cow_extinction_ratio_db
                    }
                }
            })

    elif params.protocol == "bb84":
        # Run BB84 simulation for each channel
        for ch in params.channels:
            node_a = node_map.get(ch.from_)
            node_b = node_map.get(ch.to)
            if not node_a or not node_b:
                continue

            net.connect_nodes(
                node_a.node_id, node_b.node_id,
                distance_km=ch.fiber_length_km,
                attenuation_db_per_km=ch.fiber_attenuation_db_per_km
            )

            alice_key, bob_key = node_a.generate_and_share_key_bb84(
                node_b,
                next(n.num_pulses for n in params.nodes if n.id == ch.from_),
                next(n.pulse_repetition_rate for n in params.nodes if n.id == ch.from_),
                phase_flip_prob=ch.phase_flip_prob
            )
            qber, num_errors = calculate_qber(alice_key, bob_key)
            final_key_len, postproc = postprocessing(len(alice_key), qber)
            total_time_s = (next(n.num_pulses for n in params.nodes if n.id == ch.from_) * next(n.pulse_repetition_rate for n in params.nodes if n.id == ch.from_)) / 1e9 if next(n.num_pulses for n in params.nodes if n.id == ch.from_) > 0 else 0
            print("total time taken : ", total_time_s)
            secure_key_rate_bps = final_key_len / total_time_s if total_time_s > 0 else 0
            theory_compliance = (0.03 <= qber <= 0.10)
            theory_message = "QBER is within the practical range (3-10%) for QKD." if theory_compliance else f"WARNING: QBER ({qber:.4f}) is outside the practical range for QKD."

            node_a_params = next((n for n in params.nodes if n.id == ch.from_), None)
            node_b_params = next((n for n in params.nodes if n.id == ch.to), None)

            results.append({
                "channel_id": ch.id,
                "from": ch.from_,
                "to": ch.to,
                "protocol": "bb84",
                "qber": qber,
                "final_key_length": final_key_len,
                "secure_key_rate_bps": secure_key_rate_bps,
                "sifted_key_length": len(alice_key),
                "num_errors": num_errors,
                "postprocessing": postproc,
                "theory_compliance": theory_compliance,
                "theory_message": theory_message,
                "alice_key": alice_key,
                "bob_key": bob_key,
                "parameters": {
                    "node_a": node_a_params.dict() if node_a_params else {},
                    "node_b": node_b_params.dict() if node_b_params else {},
                    "channel": ch.dict()
                }
            })

    return {"results": results}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 