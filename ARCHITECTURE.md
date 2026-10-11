# System Architecture Specification

## 1. Edge/Fog/Cloud Distributed Hierarchy

```mermaid
graph TD
    classDef cloud fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef fog fill:#083344,stroke:#06b6d4,stroke-width:2px,color:#fff;
    classDef edge fill:#1e1b4b,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef controller fill:#312e81,stroke:#6366f1,stroke-width:3px,color:#fff;

    GC["GLOBAL CONTROLLER<br/>(FastAPI / WebSocket Core)"]:::controller

    CLOUD["CLOUD<br/>Master Core Node<br/>DEFCON 5..1"]:::cloud

    FOG1["FOG-01<br/>Fog Gateway Alpha"]:::fog
    FOG2["FOG-02<br/>Fog Gateway Beta"]:::fog

    EDGE1["EDGE-01<br/>Sensor Hub 1"]:::edge
    EDGE2["EDGE-02<br/>Telemetry Hub 2"]:::edge
    EDGE3["EDGE-03<br/>Actuator Hub 3"]:::edge
    EDGE4["EDGE-04<br/>Gateway Hub 4"]:::edge

    GC -.->|Telemetry & Adaptation| CLOUD
    GC -.->|Heartbeat & Policy| FOG1
    GC -.->|Heartbeat & Policy| FOG2
    
    CLOUD --> FOG1
    CLOUD --> FOG2

    FOG1 --> EDGE1
    FOG1 --> EDGE2

    FOG2 --> EDGE3
    FOG2 --> EDGE4
```

---

## 2. MAPE-K Autonomous Feedback Loop

```mermaid
flowchart LR
    classDef kbase fill:#1e293b,stroke:#64748b,stroke-width:2px,color:#e2e8f0;
    classDef loop fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#f8fafc;

    subgraph Node_Agent ["Node Local MAPE-K Loop"]
        M["MONITOR<br/>• CPU & Traffic<br/>• Connections & Auth<br/>• Heartbeat Status"]:::loop
        A["ANALYZE<br/>• Risk Engine (30/20/15/10/25)<br/>• Threat Classifier<br/>• Severity Grading"]:::loop
        P["PLAN<br/>• Target DEFCON Calc<br/>• Restriction Synthesis<br/>• Upstream Flagging"]:::loop
        E["EXECUTE<br/>• Apply Rate Limiting/Isolation<br/>• State Machine Update<br/>• Dispatch Events"]:::loop
    end

    KB[("KNOWLEDGE BASE<br/>• Telemetry Baselines<br/>• DEFCON Thresholds<br/>• Historical Events<br/>• Active Restrictions")]:::kbase

    M --> A
    A --> P
    P --> E
    E --> M

    M <--> KB
    A <--> KB
    P <--> KB
    E <--> KB
```

---

## 3. Full Adaptation State Machine

```mermaid
stateDiagram-v2
    [*] --> FullAdaptation: All 7 Nodes Online & Healthy
    
    state FullAdaptation {
        [*] --> BaselineMonitoring
        BaselineMonitoring --> ThreatDetected: Anomaly Discovered
        ThreatDetected --> LocalAdaptation: Local MAPE-K Escalation
        LocalAdaptation --> ThreatPropagation: Notify Fog / Cloud
        ThreatPropagation --> BaselineMonitoring: Threat Cleared
    }

    FullAdaptation --> PartialAdaptation: Heartbeat Lost (> 6.0s timeout)
    PartialAdaptation --> Recovering: Heartbeat Restored
    Recovering --> FullAdaptation: Validation Complete
```

---

## 4. Partial Adaptation Architecture (Degraded Partitioning)

```mermaid
flowchart TD
    classDef normal fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef degraded fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#fff;
    classDef cluster fill:#0f172a,stroke:#3b82f6,stroke-width:1px,color:#cbd5e1;

    subgraph Alpha_Cluster ["Cluster Alpha (Degraded)"]
        F1["FOG-01<br/>Status: ONLINE"]:::normal
        E1["EDGE-01<br/>Status: ONLINE"]:::normal
        E2["EDGE-02<br/>Status: OFFLINE (Isolated)"]:::degraded
        F1 --> E1
        F1 -.->|Severed Link| E2
    end

    subgraph Beta_Cluster ["Cluster Beta (Healthy)"]
        F2["FOG-02<br/>Status: ONLINE"]:::normal
        E3["EDGE-03<br/>Status: ONLINE"]:::normal
        E4["EDGE-04<br/>Status: ONLINE"]:::normal
        F2 --> E3
        F2 --> E4
    end

    CLOUD["CLOUD MASTER<br/>Mode: PARTIAL ADAPTATION"]:::normal
    CLOUD --> F1
    CLOUD --> F2
```

---

## 5. Attack Response Flow (e.g. ICMP Flood)

```mermaid
sequenceDiagram
    autonumber
    actor Attacker
    participant EDGE02 as Node: EDGE-02
    participant FOG01 as Node: FOG-01
    participant Controller as Global Controller
    participant UI as Command Center UI

    Attacker->>EDGE02: Injects ICMP Flood (8,000+ pps)
    EDGE02->>EDGE02: Monitor: Detects traffic spike (3.5x baseline)
    EDGE02->>EDGE02: Analyze: Calculates Risk Score = 78 (High)
    EDGE02->>EDGE02: Plan: Escalates DEFCON 5 -> DEFCON 2
    EDGE02->>EDGE02: Execute: Applies Rate Limiting (500 pps ceiling)
    EDGE02->>Controller: Dispatches security_level_changed & threat_detected
    Controller->>UI: Broadcasts WebSocket event: DEFCON 2 (Edge-02)
    EDGE02->>FOG01: Propagates Upstream Threat Notice
    FOG01->>FOG01: Adapts Stance -> DEFCON 3 (Guarded)
    FOG01->>Controller: Dispatches upstream adaptation notice
    Controller->>UI: Updates Topology & Event Timeline
```

---

## 6. Node Recovery & Reintegration Flow

```mermaid
sequenceDiagram
    autonumber
    participant EDGE02 as Node: EDGE-02
    participant HB as Heartbeat Manager
    participant Controller as Global Controller
    participant UI as Command Center UI

    Note over EDGE02,HB: Node previously marked OFFLINE (Timeout > 6s)
    EDGE02->>HB: First Recovery Heartbeat Pulse
    HB->>Controller: Mark node status = RECOVERING
    Controller->>UI: Broadcast node_update (Status: RECOVERING)
    Note over HB: Validates connection stability (4.0s window)
    HB->>Controller: Heartbeat validated. Mark ONLINE.
    Controller->>Controller: Re-evaluate Active Nodes: 7 / 7 Online
    Controller->>Controller: Transition Mode: PARTIAL -> FULL ADAPTATION
    Controller->>UI: Broadcast mode_changed (FULL_ADAPTATION)
    Controller->>UI: Broadcast node_recovered (EDGE-02 Online)
```
