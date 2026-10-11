# Adaptive Security Framework for Distributed Systems (Inspired by SAFER-D)

A complete, interactive runtime prototype of an **Adaptive Security Command Center** for distributed Edge/Fog/Cloud systems. Inspired by the SAFER-D architecture, this system executes real software representations of local and global **MAPE-K loops**, dynamic **DEFCON security posture escalations**, automatic **upstream threat propagation**, real-time **heartbeat fault detection**, and seamless transitions between **Full Adaptation** and partitioned **Partial Adaptation**.

---

## 1. Project Overview

Distributed edge/fog/cloud architectures face cascading threats, volatile networking conditions, and intermittent device failures. Rather than relying on static security policies, this framework provides:
- **Local MAPE-K Loops**: Every node independently monitors metrics, analyzes anomalies, plans responses, and executes simulated security postures.
- **Global Coordination**: A centralized Global Controller tracks cross-cluster threats, calculates the most restrictive security posture, and orchestrates network-wide adaptation.
- **Fault-Tolerant Adaptation**: Automatic heartbeat monitoring isolates offline nodes and shifts the network to **Partial Adaptation**, ensuring healthy nodes continue operating and adapting without interruption.
- **Interactive Command Center**: A real-time React Flow canvas connected to a FastAPI backend over bidirectional WebSockets.

---

## 2. Distributed Topology

```
                  CLOUD (Master Core)
                          |
             +------------+------------+
             |                         |
       FOG-01 (Gateway Alpha)    FOG-02 (Gateway Beta)
         /           \             /           \
   EDGE-01        EDGE-02       EDGE-03       EDGE-04
  (Sensor 1)   (Telemetry 2)  (Actuator 3)  (Gateway 4)
```

Each node exposes telemetry (CPU, network traffic in pps, socket connections, failed authentications), heartbeat state, active DEFCON level, risk score, and real-time MAPE-K execution stage.

---

## 3. Technology Stack

- **Backend**: Python 3.11+, FastAPI, WebSockets, Pydantic v2, asyncio, SQLite3.
- **Frontend**: React 18, TypeScript, Vite, `@xyflow/react` (React Flow), Tailwind CSS, Lucide Icons.
- **Containerization**: Docker, Docker Compose.
- **Testing**: Pytest, Pytest-AsyncIO, Starlette TestClient.

---

## 4. MAPE-K Implementation

The framework models MAPE-K as dedicated Python classes:
- **Monitor (`Monitor`)**: Ingests node telemetry (CPU %, network traffic pps, socket count, authentication attempts) and pulses heartbeat signals.
- **Analyze (`ThreatAnalyzer` / `RuleBasedAnalyzer`)**: Evaluates anomalous deviations against cluster baselines using a modular weighted risk engine:
  - Traffic Anomaly: 30%
  - Connection Rate: 20%
  - Authentication Anomaly: 15%
  - CPU Anomaly: 10%
  - Turbulence/Jitter: 25%
- **Plan (`Planner`)**: Maps risk scores to target DEFCON levels, assesses escalation necessity, formulates restriction sets, and flags upstream nodes if containment requires Fog/Cloud intervention.
- **Execute (`Executor`)**: Updates node state machines, enforces rate limiting or isolation, updates timestamps, and dispatches events to SQLite and WebSockets.
- **Knowledge (`KnowledgeBase`)**: Stores historical incursions, policy definitions, baseline profiles, and adaptation logs.

---

## 5. Security Levels (DEFCON State Machine)

| DEFCON Level | State | Risk Range | Applied Security Actions |
|---|---|---|---|
| **DEFCON 5** | NORMAL | 0 - 24 | Baseline monitoring, standard ingress/egress, default logging |
| **DEFCON 4** | ELEVATED | 25 - 49 | Polling interval reduced to 1s, deep packet inspection logging |
| **DEFCON 3** | GUARDED | 50 - 69 | Flag suspicious sources, SYN cookies, rate limit ceiling 1,500 pps |
| **DEFCON 2** | MODERATE | 70 - 89 | Aggressive traffic shaping (500 pps max), drop suspicious IPs |
| **DEFCON 1** | MAXIMUM | 90 - 100 | Simulated node isolation, block ingress, failover redirection |

---

## 6. Full vs. Partial Adaptation

- **Full Adaptation**: Active when all 7 nodes (Cloud, 2 Fog, 4 Edge) are healthy and reporting heartbeats. Threat intel and coordinated restrictions freely propagate across the hierarchy.
- **Partial Adaptation**: Triggered automatically when one or more nodes fail or disconnect (> 6.0s heartbeat timeout). The controller partitions remaining nodes into functional clusters (`Cluster Alpha`, `Cluster Beta`), allowing surviving nodes to continue adapting autonomously.
- **Recovery**: When an offline node pulses heartbeats, it transitions through `RECOVERING` (4.0s validation delay) to `ONLINE`. When all 7 nodes are verified, the system seamlessly transitions back to `FULL ADAPTATION`.

---

## 7. Installation & Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### Local Backend Setup
```bash
# Navigate to project root
cd "Distributed systems"

# Install Python requirements
pip install -r backend/requirements.txt

# Run the backend server
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Local Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Start development server
npm run dev
```

Open your browser at `http://localhost:5173` (or `http://localhost:8000` when running the bundled build).

---

## 8. Docker Deployment

To launch the Global Controller, all 7 simulated node agents, and the frontend in isolated containers:
```bash
docker compose up --build
```
- Web UI: `http://localhost`
- Global Controller API & Docs: `http://localhost:8000/docs`

---

## 9. API Reference

### REST Endpoints
- `GET /api/nodes` - List all node states
- `GET /api/nodes/{node_id}` - Get individual node details
- `POST /api/nodes/{node_id}/attack` - Inject attack (`ICMP_FLOOD`, `PORT_SCAN`, `BRUTE_FORCE_AUTH`)
- `POST /api/nodes/{node_id}/fail` - Force node heartbeat failure
- `POST /api/nodes/{node_id}/recover` - Initiate node recovery sequence
- `POST /api/nodes/{node_id}/action` - Quick actions (`rate_limit`, `isolate`, `increase_monitoring`, `reset`)
- `GET /api/system/status` - Global adaptation mode, most restrictive level, node counts
- `GET /api/events` - Recent event timeline (SQLite/Memory)
- `GET /api/threats` - Detected threats log
- `POST /api/simulation/demo` - Trigger automated 11-step demo scenario
- `POST /api/simulation/reset` - Reset entire topology to nominal baseline

### WebSocket Endpoint
- `/ws` - Full-duplex JSON event stream:
  - `init_state`: Full initial state snapshot
  - `nodes_snapshot`: Periodic telemetry broadcast
  - `node_update`: Single node state change
  - `security_level_changed`: DEFCON escalation/de-escalation
  - `threat_detected`: Incursion detection payload
  - `heartbeat_lost`: Node timeout notification
  - `node_recovered`: Reintegrated node payload
  - `mode_changed`: Full <-> Partial adaptation transitions
  - `demo_progress`: Step-by-step automated demo updates

---

## 10. Automated Demo Scenario (11 Steps)

Click the **"RUN FULL ADAPTIVE SECURITY DEMO"** button on the dashboard to view the complete lifecycle:
1. **Baseline**: System resets to DEFCON 5 and `FULL ADAPTATION`.
2. **Monitoring Active**: MAPE-K loops engage across all 7 nodes.
3. **ICMP Flood**: Attack injected on `EDGE-02` (traffic spikes to 3,500+ pps).
4. **Risk Surge**: Telemetry anomalies calculate risk progression (30 -> 45 -> 62 -> 78).
5. **DEFCON Escalation**: `EDGE-02` adapts from DEFCON 5 -> DEFCON 2.
6. **Adaptation Enforced**: Simulated rate limiting is applied (500 pps ceiling).
7. **Threat Propagation**: Upstream notice sent to `FOG-01` (adapts to DEFCON 3) and `CLOUD`.
8. **Heartbeat Failure**: `EDGE-02` simulated failure (heartbeat terminated).
9. **Partial Adaptation**: Timeout confirmed (> 6s). Mode shifts to `PARTIAL ADAPTATION`.
10. **Recovery**: `EDGE-02` re-awakens: `OFFLINE` -> `RECOVERING` (validation delay).
11. **Reintegration**: All 7 nodes online. System returns to `FULL ADAPTATION`.

---

## 11. Automated Testing

Run the automated test suite covering all state transitions, risk calculations, heartbeat timeouts, and API routes:
```bash
python -m pytest backend/tests/test_framework.py -v
```

---

## 12. Future Machine Learning Extension

The analyzer uses an abstract base class `ThreatAnalyzer`:
```python
class ThreatAnalyzer(ABC):
    @abstractmethod
    def analyze(self, telemetry: NodeTelemetry, baseline: Dict[str, float]):
        pass
```
The system currently runs `RuleBasedAnalyzer(ThreatAnalyzer)`. It can easily be extended with machine-learning models (e.g. `IsolationForestAnalyzer`, `AutoencoderAnalyzer`, or `XGBoostClassifier`) by implementing the same interface without altering the MAPE-K pipeline or API endpoints.

## Audit, experiments, and enforcement boundaries

The suite requires `pytest-asyncio`, included in `backend/requirements.txt`. Run it with `python -m pytest -q`.

Structured adaptation decisions are available from `GET /api/audit/decisions`. Records include observed telemetry, baseline, risk components, selected posture, and explicit `enforcement_mode` / `execution_status` values.

Run a deterministic synthetic comparison with:

```bash
python -m backend.experiments.run_experiment --seed 7 --scenario icmp_flood --output experiment-results.json
```

The runner compares static, local-only, and coordinated adaptation and stores raw traces and metric definitions in JSON. Its scenarios are simulations, not real attack-detection benchmarks. The current project provides a safe simulated enforcement adapter only: it does not install firewall rules, block real traffic, isolate hosts, or represent real attack detection. Risk analysis validates non-negative finite telemetry; escalation is immediate, while de-escalation requires configurable consecutive normal observations and a cooldown.

Known limitations include single-process simulated nodes, timer-based recovery validation, lightweight SQLite error handling, and npm audit findings that should be reviewed before production use.
