import asyncio
import time
import random
from typing import Optional, Dict, Any
from ..models.node import NodeState, NodeStatus, SecurityLevel, MapeKStage
from ..models.threat import ThreatType
from ..models.event import SystemEvent, SystemEventType
from ..core.websocket_manager import websocket_manager
from ..core.database import log_event_db
from .global_controller import global_controller
from .heartbeat_manager import heartbeat_manager
from .monitor import monitor_engine
from .knowledge import knowledge_base

class SimulationEngine:
    def __init__(self):
        self.is_running = False
        self._ticker_task: Optional[asyncio.Task] = None
        self._demo_task: Optional[asyncio.Task] = None
        self.demo_in_progress = False
        self.demo_current_step = 0
        self.demo_total_steps = 11
        self.demo_status_text = "Idle"
        self.active_attacks: Dict[str, Dict[str, Any]] = {}

    def start_simulation(self):
        if not self.is_running:
            self.is_running = True
            self._ticker_task = asyncio.create_task(self._simulation_tick_loop())

    def stop_simulation(self):
        self.is_running = False
        if self._ticker_task:
            self._ticker_task.cancel()
            self._ticker_task = None

    async def _simulation_tick_loop(self):
        while self.is_running:
            try:
                # 1. Heartbeat check
                await heartbeat_manager.check_heartbeats(global_controller.nodes)

                # 2. Update telemetry for all online nodes
                for node_id, node in global_controller.nodes.items():
                    if node.status != NodeStatus.ONLINE:
                        continue

                    # If node is under attack, sustain/advance attack metrics
                    if node_id in self.active_attacks:
                        attack = self.active_attacks[node_id]
                        a_type = attack["type"]
                        if a_type == ThreatType.ICMP_FLOOD:
                            node.network_traffic = min(12000.0, node.network_traffic + random.uniform(800.0, 1600.0))
                            node.cpu_usage = min(92.0, node.cpu_usage + random.uniform(4.0, 9.0))
                            node.connections = min(2500, node.connections + random.randint(50, 150))
                        elif a_type == ThreatType.PORT_SCAN:
                            node.connections = min(3500, node.connections + random.randint(250, 600))
                            node.network_traffic = min(4500.0, node.network_traffic + random.uniform(200.0, 500.0))
                        elif a_type == ThreatType.BRUTE_FORCE_AUTH:
                            node.failed_auths = min(80, node.failed_auths + random.randint(3, 8))
                            node.cpu_usage = min(65.0, node.cpu_usage + random.uniform(2.0, 5.0))
                    else:
                        # Natural jitter around baseline
                        base = knowledge_base.get_baseline(node.node_type.value)
                        node.cpu_usage = max(4.0, base["cpu"] + random.uniform(-1.5, 2.5))
                        node.network_traffic = max(20.0, base["traffic"] + random.uniform(-10.0, 15.0))
                        node.connections = max(10, int(base["connections"] + random.uniform(-4, 6)))
                        node.failed_auths = max(0, node.failed_auths - 1)

                    # Pulse heartbeat if not blocked
                    if not heartbeat_manager.is_heartbeat_blocked(node_id):
                        await heartbeat_manager.pulse(node)

                    # Local MAPE-K execution
                    await monitor_engine.run_mape_k_cycle(
                        node=node,
                        adaptation_mode=global_controller.global_mode,
                        propagate_callback=global_controller.propagate_threat_upstream
                    )

                # Broadcast node state updates
                await websocket_manager.broadcast("nodes_snapshot", {
                    node_id: n.model_dump() for node_id, n in global_controller.nodes.items()
                })
                await websocket_manager.broadcast("system_status", global_controller.get_system_status().model_dump())

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Simulation loop error: {e}")

            await asyncio.sleep(1.8)

    async def trigger_attack(self, node_id: str, attack_type: ThreatType):
        if node_id not in global_controller.nodes:
            return False
        node = global_controller.nodes[node_id]
        if node.status != NodeStatus.ONLINE:
            return False

        self.active_attacks[node_id] = {
            "type": attack_type,
            "started_at": time.time()
        }

        # Seed initial spike
        if attack_type == ThreatType.ICMP_FLOOD:
            node.network_traffic = 3500.0
            node.cpu_usage = 45.0
        elif attack_type == ThreatType.PORT_SCAN:
            node.connections = 600
            node.network_traffic = 1200.0
        elif attack_type == ThreatType.BRUTE_FORCE_AUTH:
            node.failed_auths = 15

        attack_evt = SystemEvent(
            event_type=SystemEventType.SIMULATION_STEP,
            node_id=node_id,
            message=f"Simulation attack injected: {attack_type.value} targeting node {node_id}.",
            severity="WARNING",
            details={"attack_type": attack_type.value, "target": node_id}
        )
        knowledge_base.record_event(attack_evt)
        log_event_db(
            attack_evt.id, attack_evt.timestamp, attack_evt.formatted_time,
            attack_evt.event_type.value, attack_evt.node_id, attack_evt.message,
            attack_evt.severity, attack_evt.details
        )
        await websocket_manager.broadcast("simulation_event", attack_evt.model_dump())

        # Trigger immediate MAPE-K cycle on attacked node
        await monitor_engine.run_mape_k_cycle(
            node=node,
            adaptation_mode=global_controller.global_mode,
            propagate_callback=global_controller.propagate_threat_upstream
        )
        await websocket_manager.broadcast("node_update", node.model_dump())
        return True

    def stop_attack(self, node_id: str):
        if node_id in self.active_attacks:
            del self.active_attacks[node_id]
            if node_id in global_controller.nodes:
                node = global_controller.nodes[node_id]
                node.current_threat = "NORMAL"
                node.threat_score = 5.0
                node.failed_auths = 0

    async def fail_node(self, node_id: str):
        """Immediately blocks node heartbeat to trigger timeout & partial adaptation"""
        if node_id not in global_controller.nodes:
            return False
        heartbeat_manager.simulate_fail_heartbeat(node_id)
        node = global_controller.nodes[node_id]
        node.last_heartbeat = time.time() - (heartbeat_manager.timeout + 1.0)
        await heartbeat_manager.check_heartbeats(global_controller.nodes)
        await websocket_manager.broadcast("node_update", node.model_dump())
        await websocket_manager.broadcast("system_status", global_controller.get_system_status().model_dump())
        return True

    async def recover_node(self, node_id: str):
        if node_id not in global_controller.nodes:
            return False
        node = global_controller.nodes[node_id]
        if node.status == NodeStatus.ONLINE:
            return True
        self.stop_attack(node_id)
        asyncio.create_task(heartbeat_manager.recover_node_sequence(node))
        return True

    async def reset_system(self):
        self.active_attacks.clear()
        heartbeat_manager._simulated_failed_nodes.clear()
        for node in global_controller.nodes.values():
            base = knowledge_base.get_baseline(node.node_type.value)
            node.status = NodeStatus.ONLINE
            node.security_level = SecurityLevel.DEFCON_5
            node.threat_score = 4.0
            node.current_threat = "NORMAL"
            node.threat_details = "System baseline nominal."
            node.cpu_usage = base["cpu"]
            node.network_traffic = base["traffic"]
            node.connections = int(base["connections"])
            node.failed_auths = 0
            node.heartbeat_status = "HEALTHY"
            node.last_heartbeat = time.time()
            node.mape_k_stage = MapeKStage.IDLE
            node.last_adaptation = "RESET"
            node.active_restrictions = ["Standard monitoring profile active"]

        global_controller.global_mode = global_controller.get_system_status().global_mode
        rst_evt = SystemEvent(
            event_type=SystemEventType.SIMULATION_STEP,
            node_id=None,
            message="Entire distributed system reset to baseline DEFCON 5 (Normal) & FULL ADAPTATION.",
            severity="SUCCESS",
            details={"action": "SYSTEM_RESET"}
        )
        knowledge_base.record_event(rst_evt)
        log_event_db(
            rst_evt.id, rst_evt.timestamp, rst_evt.formatted_time,
            rst_evt.event_type.value, rst_evt.node_id, rst_evt.message,
            rst_evt.severity, rst_evt.details
        )
        await websocket_manager.broadcast("system_reset", {
            "event": rst_evt.model_dump(),
            "nodes": {n_id: n.model_dump() for n_id, n in global_controller.nodes.items()}
        })
        await websocket_manager.broadcast("system_status", global_controller.get_system_status().model_dump())

    def run_full_demo(self):
        """Launches the 11-step complete demo scenario asynchronously"""
        if self.demo_in_progress:
            return False
        self._demo_task = asyncio.create_task(self._demo_scenario_runner())
        return True

    async def _emit_demo_progress(self, step: int, text: str):
        self.demo_current_step = step
        self.demo_status_text = text
        await websocket_manager.broadcast("demo_progress", {
            "current_step": step,
            "total_steps": self.demo_total_steps,
            "status_text": text
        })

    async def _demo_scenario_runner(self):
        self.demo_in_progress = True
        try:
            # Step 1: Normal system baseline
            await self._emit_demo_progress(1, "Step 1/11: Initializing baseline state (All nodes DEFCON 5, FULL ADAPTATION)...")
            await self.reset_system()
            await asyncio.sleep(2.0)

            # Step 2: Start continuous monitoring
            await self._emit_demo_progress(2, "Step 2/11: Engaging local & global MAPE-K monitoring loops...")
            self.start_simulation()
            await asyncio.sleep(2.5)

            # Step 3: Trigger ICMP flood on EDGE-02
            target_id = "EDGE-02"
            edge2 = global_controller.nodes[target_id]
            await self._emit_demo_progress(3, "Step 3/11: Injecting ICMP Flood attack on EDGE-02 (traffic surge)...")
            await self.trigger_attack(target_id, ThreatType.ICMP_FLOOD)
            edge2.network_traffic = 3500.0
            edge2.cpu_usage = 42.0
            await websocket_manager.broadcast("node_update", edge2.model_dump())
            await asyncio.sleep(2.5)

            # Step 4: Risk score rises (30 -> 45 -> 62 -> 78)
            await self._emit_demo_progress(4, "Step 4/11: Telemetry surge detected. Risk score climbing (30 -> 45 -> 62 -> 78)...")
            for simulated_score, traffic, cpu in [(32.0, 4800.0, 52.0), (55.0, 6500.0, 64.0), (78.0, 8420.0, 72.0)]:
                edge2.network_traffic = traffic
                edge2.cpu_usage = cpu
                await monitor_engine.run_mape_k_cycle(
                    node=edge2,
                    adaptation_mode=global_controller.global_mode,
                    propagate_callback=global_controller.propagate_threat_upstream
                )
                await websocket_manager.broadcast("node_update", edge2.model_dump())
                await websocket_manager.broadcast("system_status", global_controller.get_system_status().model_dump())
                await asyncio.sleep(2.0)

            # Step 5: Escalation confirmed to DEFCON 2
            await self._emit_demo_progress(5, f"Step 5/11: DEFCON escalated on EDGE-02: {edge2.security_level.value} (Risk Score: {edge2.threat_score})...")
            await asyncio.sleep(2.0)

            # Step 6: Adaptation Action (Rate Limiting)
            await self._emit_demo_progress(6, "Step 6/11: Executing automated adaptation action: Simulated Rate Limiting enforced...")
            await asyncio.sleep(2.0)

            # Step 7: Security event propagation
            await self._emit_demo_progress(7, "Step 7/11: Propagating threat awareness upstream: EDGE-02 -> FOG-01 -> CLOUD...")
            await global_controller.propagate_threat_upstream("FOG-01", "EDGE-02", ThreatType.ICMP_FLOOD, edge2.security_level)
            await asyncio.sleep(2.5)

            # Step 8: Node failure simulation
            await self._emit_demo_progress(8, "Step 8/11: Simulating fatal node failure on EDGE-02 (Heartbeat lost)...")
            await self.fail_node("EDGE-02")
            await asyncio.sleep(3.0)

            # Step 9: Partial Adaptation
            await self._emit_demo_progress(9, "Step 9/11: Heartbeat timeout confirmed! Topology partitioned -> Switched to PARTIAL ADAPTATION...")
            await asyncio.sleep(3.5)

            # Step 10: Node recovery initiated
            await self._emit_demo_progress(10, "Step 10/11: Initiating recovery on EDGE-02: OFFLINE -> RECOVERING -> ONLINE...")
            await self.recover_node("EDGE-02")
            await asyncio.sleep(settings.RECOVERY_VALIDATION_SECONDS + 1.0)

            # Step 11: Reintegration and Full Adaptation
            await self._emit_demo_progress(11, "Step 11/11: EDGE-02 reintegrated! Topology re-established -> Returned to FULL ADAPTATION. Demo Complete!")
            await asyncio.sleep(2.0)

        except Exception as e:
            print(f"Error during demo runner: {e}")
            await self._emit_demo_progress(0, f"Demo error: {str(e)}")
        finally:
            self.demo_in_progress = False

simulation_engine = SimulationEngine()
