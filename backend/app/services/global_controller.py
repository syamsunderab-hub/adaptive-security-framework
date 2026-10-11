import asyncio
import time
from typing import Dict, List, Optional
from ..models.node import NodeState, NodeType, NodeStatus, SecurityLevel, MapeKStage
from ..models.security import AdaptationMode, SystemStatusResponse
from ..models.event import SystemEvent, SystemEventType
from ..models.threat import ThreatType
from ..core.config import settings
from ..core.websocket_manager import websocket_manager
from ..core.database import log_event_db, init_db
from .knowledge import knowledge_base
from .security_manager import security_level_manager
from .adaptation_manager import adaptation_manager
from .heartbeat_manager import heartbeat_manager
from .monitor import monitor_engine

class GlobalController:
    def __init__(self):
        self.nodes: Dict[str, NodeState] = {}
        self.global_mode: AdaptationMode = AdaptationMode.FULL_ADAPTATION
        self._initialized = False

    def initialize_topology(self):
        if self._initialized:
            return
        init_db()
        for node_cfg in settings.DEFAULT_NODES:
            node_state = NodeState(
                node_id=node_cfg.id,
                name=node_cfg.name,
                node_type=NodeType(node_cfg.node_type),
                status=NodeStatus.ONLINE,
                security_level=SecurityLevel.DEFCON_5,
                threat_score=4.0,
                current_threat="NORMAL",
                cpu_usage=node_cfg.initial_cpu,
                network_traffic=node_cfg.initial_traffic,
                connections=node_cfg.initial_connections,
                failed_auths=0,
                heartbeat_status="HEALTHY",
                last_heartbeat=time.time(),
                mape_k_stage=MapeKStage.IDLE,
                last_adaptation="SYSTEM_INIT",
                parent_id=node_cfg.parent_id,
                children_ids=node_cfg.children_ids,
                active_restrictions=["Normal baseline monitoring"]
            )
            self.nodes[node_cfg.id] = node_state

        heartbeat_manager.register_callbacks(
            on_offline=self.handle_node_offline,
            on_online=self.handle_node_online
        )
        self._initialized = True

    async def propagate_threat_upstream(
        self,
        target_id: str,
        source_id: str,
        threat_type: ThreatType,
        source_level: SecurityLevel
    ):
        """
        Propagates threat awareness to parent Fog or Cloud node.
        Elevates parent security stance appropriately.
        """
        if target_id not in self.nodes:
            return
        target = self.nodes[target_id]
        if target.status != NodeStatus.ONLINE:
            return

        # Upstream elevation logic:
        # e.g., if child escalated to DEFCON 2, parent Fog escalates to at least DEFCON 3
        suggested_parent_int = max(3, source_level.level_int + 1)
        suggested_parent_level = SecurityLevel.from_int(min(5, suggested_parent_int))

        if target.security_level.level_int > suggested_parent_level.level_int:
            prop_event = SystemEvent(
                event_type=SystemEventType.ADAPTATION_STARTED,
                node_id=target.node_id,
                message=f"Threat propagation from child {source_id} ({threat_type.value}) received. Upstream posture adapting to {suggested_parent_level.value}.",
                severity="WARNING",
                details={
                    "propagated_from": source_id,
                    "target_node": target.node_id,
                    "threat": threat_type.value,
                    "target_level": suggested_parent_level.value
                }
            )
            knowledge_base.record_event(prop_event)
            log_event_db(
                prop_event.id, prop_event.timestamp, prop_event.formatted_time,
                prop_event.event_type.value, prop_event.node_id, prop_event.message,
                prop_event.severity, prop_event.details
            )

            target.security_level = suggested_parent_level
            target.current_threat = f"PROPAGATED_{threat_type.value}"
            target.threat_score = max(target.threat_score, 52.0)
            target.last_adaptation = time.strftime("%H:%M:%S")

            await websocket_manager.broadcast("node_update", target.model_dump())
            await websocket_manager.broadcast("security_level_changed", {
                "event": prop_event.model_dump(),
                "node_id": target.node_id,
                "new_level": suggested_parent_level.value
            })

            # Check if Fog should further notify Cloud
            if target.parent_id and suggested_parent_level.level_int <= 3:
                await self.propagate_threat_upstream(
                    target.parent_id, target.node_id, threat_type, suggested_parent_level
                )

    async def handle_node_offline(self, node_id: str):
        prev_mode = self.global_mode
        self.global_mode = adaptation_manager.evaluate_adaptation_mode(self.nodes)

        if self.global_mode != prev_mode:
            mode_evt = SystemEvent(
                event_type=SystemEventType.MODE_CHANGED,
                node_id=node_id,
                message=f"System topology partitioned by offline node {node_id}. Global adaptation mode changed: {prev_mode.value} -> {self.global_mode.value}.",
                severity="CRITICAL",
                details={
                    "previous_mode": prev_mode.value,
                    "new_mode": self.global_mode.value,
                    "trigger_node": node_id
                }
            )
            knowledge_base.record_event(mode_evt)
            log_event_db(
                mode_evt.id, mode_evt.timestamp, mode_evt.formatted_time,
                mode_evt.event_type.value, mode_evt.node_id, mode_evt.message,
                mode_evt.severity, mode_evt.details
            )
            await websocket_manager.broadcast("mode_changed", {
                "previous_mode": prev_mode.value,
                "new_mode": self.global_mode.value,
                "event": mode_evt.model_dump()
            })

    async def handle_node_online(self, node_id: str):
        prev_mode = self.global_mode
        self.global_mode = adaptation_manager.evaluate_adaptation_mode(self.nodes)

        if self.global_mode != prev_mode:
            mode_evt = SystemEvent(
                event_type=SystemEventType.MODE_CHANGED,
                node_id=node_id,
                message=f"Node {node_id} reintegrated. All nodes healthy. Global adaptation mode returned: {prev_mode.value} -> {self.global_mode.value}.",
                severity="SUCCESS",
                details={
                    "previous_mode": prev_mode.value,
                    "new_mode": self.global_mode.value,
                    "trigger_node": node_id
                }
            )
            knowledge_base.record_event(mode_evt)
            log_event_db(
                mode_evt.id, mode_evt.timestamp, mode_evt.formatted_time,
                mode_evt.event_type.value, mode_evt.node_id, mode_evt.message,
                mode_evt.severity, mode_evt.details
            )
            await websocket_manager.broadcast("mode_changed", {
                "previous_mode": prev_mode.value,
                "new_mode": self.global_mode.value,
                "event": mode_evt.model_dump()
            })

    def get_most_restrictive_level(self) -> SecurityLevel:
        levels = [n.security_level for n in self.nodes.values() if n.status == NodeStatus.ONLINE]
        return security_level_manager.get_most_restrictive(levels)

    def get_system_status(self) -> SystemStatusResponse:
        total = len(self.nodes)
        online = sum(1 for n in self.nodes.values() if n.status == NodeStatus.ONLINE)
        offline = sum(1 for n in self.nodes.values() if n.status == NodeStatus.OFFLINE)
        recovering = sum(1 for n in self.nodes.values() if n.status == NodeStatus.RECOVERING)
        active_threats = sum(1 for n in self.nodes.values() if n.current_threat != "NORMAL" and n.status == NodeStatus.ONLINE)
        
        avg_risk = 0.0
        if online > 0:
            avg_risk = sum(n.threat_score for n in self.nodes.values() if n.status == NodeStatus.ONLINE) / online
        
        most_restrictive = self.get_most_restrictive_level()
        groups = adaptation_manager.get_active_adaptation_groups(self.nodes)
        isolated = [n.node_id for n in self.nodes.values() if n.status == NodeStatus.ISOLATED]

        return SystemStatusResponse(
            system_name=settings.PROJECT_NAME,
            global_mode=self.global_mode,
            overall_threat_level=most_restrictive,
            most_restrictive_level=most_restrictive,
            online_nodes=online,
            offline_nodes=offline,
            recovering_nodes=recovering,
            total_nodes=total,
            active_threats_count=active_threats,
            avg_risk_score=round(avg_risk, 1),
            isolated_nodes=isolated,
            active_adaptation_groups=groups
        )

global_controller = GlobalController()
