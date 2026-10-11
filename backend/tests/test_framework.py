import pytest
import asyncio
from backend.app.models.node import NodeTelemetry, NodeStatus, SecurityLevel, MapeKStage
from backend.app.models.threat import ThreatType
from backend.app.models.security import AdaptationMode
from backend.app.services.analyzer import analyzer_engine
from backend.app.services.security_manager import security_level_manager
from backend.app.services.global_controller import global_controller
from backend.app.services.heartbeat_manager import heartbeat_manager
from backend.app.services.monitor import monitor_engine
from backend.app.services.simulation_engine import simulation_engine
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(autouse=True)
def setup_topology():
    global_controller.initialize_topology()

def test_risk_score_and_threat_detection():
    # 1. Normal telemetry
    normal_telemetry = NodeTelemetry(
        cpu_percent=8.0,
        network_traffic_pps=85.0,
        connection_count=25,
        failed_auth_count=0
    )
    baseline = {"traffic": 85.0, "connections": 25.0, "cpu": 8.0}
    risk, th_type, sev, conf, desc, rec = analyzer_engine.analyze(normal_telemetry, baseline)
    assert risk < 25.0
    assert th_type == ThreatType.NORMAL
    assert security_level_manager.calculate_level_from_score(risk) == SecurityLevel.DEFCON_5

    # 2. ICMP flood
    flood_telemetry = NodeTelemetry(
        cpu_percent=75.0,
        network_traffic_pps=8500.0,
        connection_count=120,
        failed_auth_count=0
    )
    risk, th_type, sev, conf, desc, rec = analyzer_engine.analyze(flood_telemetry, baseline)
    assert risk >= 70.0
    assert th_type == ThreatType.ICMP_FLOOD
    sec_level = security_level_manager.calculate_level_from_score(risk)
    assert sec_level in (SecurityLevel.DEFCON_2, SecurityLevel.DEFCON_1)

def test_security_level_transitions_and_actions():
    assert security_level_manager.calculate_level_from_score(15) == SecurityLevel.DEFCON_5
    assert security_level_manager.calculate_level_from_score(35) == SecurityLevel.DEFCON_4
    assert security_level_manager.calculate_level_from_score(55) == SecurityLevel.DEFCON_3
    assert security_level_manager.calculate_level_from_score(75) == SecurityLevel.DEFCON_2
    assert security_level_manager.calculate_level_from_score(95) == SecurityLevel.DEFCON_1

    # Most restrictive check
    levels = [SecurityLevel.DEFCON_5, SecurityLevel.DEFCON_3, SecurityLevel.DEFCON_2]
    assert security_level_manager.get_most_restrictive(levels) == SecurityLevel.DEFCON_2

@pytest.mark.asyncio
async def test_mape_k_cycle():
    node = global_controller.nodes["EDGE-01"]
    node.network_traffic = 6000.0
    node.cpu_usage = 68.0

    updated = await monitor_engine.run_mape_k_cycle(node)
    assert updated.threat_score >= 50.0
    assert updated.security_level != SecurityLevel.DEFCON_5
    assert len(updated.active_restrictions) > 0

@pytest.mark.asyncio
async def test_heartbeat_failure_and_partial_adaptation():
    # Verify starting in FULL_ADAPTATION
    status = global_controller.get_system_status()
    assert status.global_mode == AdaptationMode.FULL_ADAPTATION

    # Trigger failure on EDGE-03
    await simulation_engine.fail_node("EDGE-03")
    edge3 = global_controller.nodes["EDGE-03"]
    assert edge3.status == NodeStatus.OFFLINE

    # System must transition to PARTIAL_ADAPTATION
    status_degraded = global_controller.get_system_status()
    assert status_degraded.global_mode == AdaptationMode.PARTIAL_ADAPTATION

    # Recover EDGE-03
    heartbeat_manager.recovery_delay = 0.1  # Fast test delay
    await heartbeat_manager.recover_node_sequence(edge3)
    assert edge3.status == NodeStatus.ONLINE

    # System must return to FULL_ADAPTATION
    status_recovered = global_controller.get_system_status()
    assert status_recovered.global_mode == AdaptationMode.FULL_ADAPTATION

@pytest.mark.asyncio
async def test_end_to_end_integration_flow():
    """
    Test scenario:
    1. attack EDGE-02 -> security level changes
    2. node failure -> partial adaptation
    3. node recovery -> full adaptation
    """
    await simulation_engine.reset_system()
    edge2 = global_controller.nodes["EDGE-02"]
    assert edge2.security_level == SecurityLevel.DEFCON_5
    assert global_controller.global_mode == AdaptationMode.FULL_ADAPTATION

    # 1. Attack EDGE-02
    await simulation_engine.trigger_attack("EDGE-02", ThreatType.ICMP_FLOOD)
    assert edge2.threat_score > 30.0
    assert edge2.security_level in (SecurityLevel.DEFCON_4, SecurityLevel.DEFCON_3, SecurityLevel.DEFCON_2)

    # 2. Node failure
    await simulation_engine.fail_node("EDGE-02")
    assert edge2.status == NodeStatus.OFFLINE
    assert global_controller.global_mode == AdaptationMode.PARTIAL_ADAPTATION

    # 3. Node recovery
    heartbeat_manager.recovery_delay = 0.1
    await heartbeat_manager.recover_node_sequence(edge2)
    assert edge2.status == NodeStatus.ONLINE
    assert global_controller.global_mode == AdaptationMode.FULL_ADAPTATION

def test_api_endpoints():
    with TestClient(app) as client:
        # GET /api/nodes
        res = client.get("/api/nodes")
        assert res.status_code == 200
        nodes = res.json()
        assert len(nodes) == 7

        # GET /api/system/status
        res_status = client.get("/api/system/status")
        assert res_status.status_code == 200
        data = res_status.json()
        assert data["total_nodes"] == 7

        # POST /api/nodes/EDGE-01/action
        res_act = client.post("/api/nodes/EDGE-01/action", json={"action": "rate_limit"})
        assert res_act.status_code == 200
        assert res_act.json()["node"]["security_level"] == "DEFCON_2"
