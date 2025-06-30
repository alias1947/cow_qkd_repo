from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from Network import Network
from main import calculate_qber, postprocessing

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimParams(BaseModel):
    protocol: str
    num_pulses: int
    mu: float
    detector_efficiency: float
    dark_count_rate: float
    phase_flip_prob: float
    fiber_length_km: float
    fiber_attenuation_db_per_km: float
    pulse_repetition_rate: float
    # COW-specific
    cow_monitor_pulse_ratio: float
    cow_detection_threshold_photons: float
    cow_extinction_ratio_db: float = 20.0

@app.get("/")
def read_root():
    return {"message": "QKD Simulation API"}

@app.post("/simulate")
def simulate(params: SimParams):
    """
    Main simulation endpoint.
    Takes simulation parameters and returns results.
    """
    net = Network()
    results = {}

    if params.protocol == "dps":
        # Setup nodes for DPS
        alice = net.add_node('Alice', avg_photon_number=params.mu)
        bob = net.add_node('Bob', detector_efficiency=params.detector_efficiency, 
                           dark_count_rate=params.dark_count_rate)
        # Use fiber parameters for connection
        net.connect_nodes('Alice', 'Bob', distance_km=params.fiber_length_km,
                         attenuation_db_per_km=params.fiber_attenuation_db_per_km)
        
        # Generate key with phase flip probability
        alice_key, bob_key = alice.generate_and_share_key(
            bob, params.num_pulses, params.pulse_repetition_rate,
            phase_flip_prob=params.phase_flip_prob
        )
        qber, num_errors = calculate_qber(alice_key, bob_key)
        final_key_len, postproc = postprocessing(len(alice_key), qber)

        # Calculate secure key rate
        total_time_s = (params.num_pulses * params.pulse_repetition_rate) / 1e9 if params.num_pulses > 0 else 0
        secure_key_rate_bps = final_key_len / total_time_s if total_time_s > 0 else 0
        
        theory_compliance = (0.03 <= qber <= 0.11)
        theory_message = "QBER is within the practical range (3-11  %) for QKD." if theory_compliance else f"WARNING: QBER ({qber:.4f}) is outside the practical range (3-10%) for QKD!"

        results = {
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
        }

    elif params.protocol == "cow":
        alice = net.add_node('Alice', avg_photon_number=params.mu,
                             cow_monitor_pulse_ratio=params.cow_monitor_pulse_ratio,
                             cow_detection_threshold_photons=int(params.cow_detection_threshold_photons),
                             cow_extinction_ratio_db=params.cow_extinction_ratio_db)
        bob = net.add_node('Bob', detector_efficiency=params.detector_efficiency,
                           dark_count_rate=params.dark_count_rate,
                           cow_monitor_pulse_ratio=params.cow_monitor_pulse_ratio,
                           cow_detection_threshold_photons=int(params.cow_detection_threshold_photons))
        # Use fiber parameters for connection
        net.connect_nodes('Alice', 'Bob', distance_km=params.fiber_length_km,
                         attenuation_db_per_km=params.fiber_attenuation_db_per_km)
        alice_key, bob_key = alice.generate_and_share_key_cow(
            bob, params.num_pulses, params.pulse_repetition_rate,
            monitor_pulse_ratio=params.cow_monitor_pulse_ratio,
            detection_threshold_photons=int(params.cow_detection_threshold_photons),
            phase_flip_prob=params.phase_flip_prob
        )
        qber, num_errors = calculate_qber(alice_key, bob_key)
        final_key_len, postproc = postprocessing(len(alice_key), qber)
        
        # Calculate secure key rate
        total_time_s = (params.num_pulses * params.pulse_repetition_rate) / 1e9 if params.num_pulses > 0 else 0
        secure_key_rate_bps = final_key_len / total_time_s if total_time_s > 0 else 0

        # Monitoring/decoy results: get from traffic_log
        monitoring_info = None
        if alice.traffic_log:
            last_log = alice.traffic_log[-1]
            if last_log.get('type') == 'key_generation_cow':
                monitoring_info = {
                    "successful_monitor_pairs": last_log.get("successful_monitor_pairs"),
                    "attempted_monitor_pairs": last_log.get("attempted_monitor_pairs"),
                }

        theory_compliance = (0.03 <= qber <= 0.10)
        theory_message = "QBER is within the practical range (3-10%) for QKD." if theory_compliance else f"WARNING: QBER ({qber:.4f}) is outside the practical range (3-10%) for QKD!"

        results = {
            "protocol": "cow",
            "qber": qber,
            "final_key_length": final_key_len,
            "secure_key_rate_bps": secure_key_rate_bps,
            "sifted_key_length": len(alice_key),
            "num_errors": num_errors,
            "monitoring_info": monitoring_info,
            "postprocessing": postproc,
            "theory_compliance": theory_compliance,
            "theory_message": theory_message,
            "alice_key": alice_key,
            "bob_key": bob_key,
        }
    
    else:
        return {"error": "Invalid protocol specified. Choose 'dps' or 'cow'."}

    return results

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 