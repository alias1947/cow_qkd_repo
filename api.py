from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Network import Network
from main import calculate_qber, postprocessing

app = FastAPI()

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimParams(BaseModel):
    protocol: str  # "dps" or "cow"
    num_pulses: int
    distance_km: float
    mu: float
    detector_efficiency: float
    dark_count_rate: float
    pulse_repetition_rate: float
    cow_monitor_pulse_ratio: float = 0.2
    cow_detection_threshold_photons: int = 0

@app.post("/simulate")
def simulate(params: SimParams):
    net = Network()
    if params.protocol == "dps":
        alice = net.add_node('Alice', avg_photon_number=params.mu)
        bob = net.add_node('Bob', detector_efficiency=params.detector_efficiency,
                           dark_count_rate=params.dark_count_rate)
        net.connect_nodes('Alice', 'Bob', distance_km=params.distance_km)
        alice_key, bob_key = alice.generate_and_share_key(
            bob, params.num_pulses, params.pulse_repetition_rate
        )
        qber, num_errors = calculate_qber(alice_key, bob_key)
        final_key_len, postproc = postprocessing(len(alice_key), qber)
        theory_compliance = (0.03 <= qber <= 0.10)
        return {
            "protocol": "dps",
            "alice_key": alice_key,
            "bob_key": bob_key,
            "sifted_key_length": len(alice_key),
            "qber": qber,
            "num_errors": num_errors,
            "final_key_length": final_key_len,
            "postprocessing": postproc,
            "theory_compliance": theory_compliance,
            "theory_message": "QBER is within the practical range (3-10%) for QKD." if theory_compliance else f"WARNING: QBER ({qber:.4f}) is outside the practical range (3-10%) for QKD!",
            "mu": params.mu,
            "detector_efficiency": params.detector_efficiency,
            "dark_count_rate": params.dark_count_rate,
            "distance_km": params.distance_km
        }
    elif params.protocol == "cow":
        alice = net.add_node('Alice', avg_photon_number=params.mu,
                             cow_monitor_pulse_ratio=params.cow_monitor_pulse_ratio,
                             cow_detection_threshold_photons=params.cow_detection_threshold_photons)
        bob = net.add_node('Bob', detector_efficiency=params.detector_efficiency,
                           dark_count_rate=params.dark_count_rate,
                           cow_monitor_pulse_ratio=params.cow_monitor_pulse_ratio,
                           cow_detection_threshold_photons=params.cow_detection_threshold_photons)
        net.connect_nodes('Alice', 'Bob', distance_km=params.distance_km)
        alice_key, bob_key = alice.generate_and_share_key_cow(
            bob, params.num_pulses, params.pulse_repetition_rate,
            monitor_pulse_ratio=params.cow_monitor_pulse_ratio,
            detection_threshold_photons=params.cow_detection_threshold_photons
        )
        qber, num_errors = calculate_qber(alice_key, bob_key)
        final_key_len, postproc = postprocessing(len(alice_key), qber)
        # Monitoring/decoy results: get from traffic_log
        monitoring_info = None
        if alice.traffic_log:
            for entry in alice.traffic_log[::-1]:
                if entry.get('type') == 'key_generation_cow':
                    monitoring_info = {
                        'successful_monitor_pairs': entry.get('successful_monitor_pairs'),
                        'attempted_monitor_pairs': entry.get('attempted_monitor_pairs')
                    }
                    break
        theory_compliance = (0.03 <= qber <= 0.10)
        return {
            "protocol": "cow",
            "alice_key": alice_key,
            "bob_key": bob_key,
            "sifted_key_length": len(alice_key),
            "qber": qber,
            "num_errors": num_errors,
            "final_key_length": final_key_len,
            "postprocessing": postproc,
            "monitoring_info": monitoring_info,
            "theory_compliance": theory_compliance,
            "theory_message": "QBER is within the practical range (3-10%) for QKD." if theory_compliance else f"WARNING: QBER ({qber:.4f}) is outside the practical range (3-10%) for QKD!",
            "mu": params.mu,
            "detector_efficiency": params.detector_efficiency,
            "dark_count_rate": params.dark_count_rate,
            "distance_km": params.distance_km
        }
    else:
        return {"error": "Unknown protocol"} 