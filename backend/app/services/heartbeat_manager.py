import asyncio
import time
from typing import Dict, Optional, Callable, Awaitable
from ..models.node import NodeState, NodeStatus
from ..models.event import SystemEvent, SystemEventType
from ..core.config import settings
from ..core.websocket_manager import websocket_manager
from ..core.database import log_event_db
from .knowledge import knowledge_base

class HeartbeatManager:
    def __init__(self):
        self.interval = settings.HEARTBEAT_INTERVAL_SECONDS
        self.timeout = settings.HEARTBEAT_TIMEOUT_SECONDS
        self.recovery_delay = settings.RECOVERY_VALIDATION_SECONDS
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._simulated_failed_nodes: set = set()
        self._on_node_offline_cb: Optional[Callable[[str], Awaitable[None]]] = None
        self._on_node_online_cb: Optional[Callable[[str], Awaitable[None]]] = None

    def register_callbacks(
        self,
        on_offline: Callable[[str], Awaitable[None]],
        on_online: Callable[[str], Awaitable[None]]
    ):
        self._on_node_offline_cb = on_offline
        self._on_node_online_cb = on_online

    def simulate_fail_heartbeat(self, node_id: str):
        self._simulated_failed_nodes.add(node_id)

    def simulate_restore_heartbeat(self, node_id: str):
        self._simulated_failed_nodes.discard(node_id)

    def is_heartbeat_blocked(self, node_id: str) -> bool:
        return node_id in self._simulated_failed_nodes

    async def pulse(self, node: NodeState):
        """Called when a node successfully sends a heartbeat"""
        if node.node_id in self._simulated_failed_nodes:
            # Heartbeat dropped by simulation failure
            return
        node.last_heartbeat = time.time()
        node.heartbeat_status = "HEALTHY"

    async def check_heartbeats(self, nodes: Dict[str, NodeState]):
        now = time.time()
        for node_id, node in nodes.items():
            # If manually failed or timeout exceeded
            if node_id in self._simulated_failed_nodes:
                if node.status == NodeStatus.ONLINE:
                    await self._mark_offline(node)
                continue

            if node.status == NodeStatus.ONLINE:
                if (now - node.last_heartbeat) > self.timeout:
                    await self._mark_offline(node)
                else:
                    node.heartbeat_status = "HEALTHY"

    async def _mark_offline(self, node: NodeState):
        node.status = NodeStatus.OFFLINE
        node.heartbeat_status = "TIMEOUT"
        
        event = SystemEvent(
            event_type=SystemEventType.HEARTBEAT_LOST,
            node_id=node.node_id,
            message=f"Node {node.node_id} heartbeat timeout exceeded (> {self.timeout}s). Marked OFFLINE.",
            severity="CRITICAL",
            details={
                "timeout_seconds": self.timeout,
                "node_status": "OFFLINE",
                "adaptation_mode_target": "PARTIAL_ADAPTATION"
            }
        )
        knowledge_base.record_event(event)
        log_event_db(
            event.id, event.timestamp, event.formatted_time,
            event.event_type.value, event.node_id, event.message,
            event.severity, event.details
        )
        await websocket_manager.broadcast("heartbeat_lost", {
            "node_id": node.node_id,
            "status": "OFFLINE",
            "event": event.model_dump()
        })

        if self._on_node_offline_cb:
            await self._on_node_offline_cb(node.node_id)

    async def recover_node_sequence(self, node: NodeState):
        """
        Executes sequence: OFFLINE -> RECOVERING -> ONLINE
        """
        self.simulate_restore_heartbeat(node.node_id)
        node.status = NodeStatus.RECOVERING
        node.heartbeat_status = "VALIDATING"
        node.last_heartbeat = time.time()

        rec_event = SystemEvent(
            event_type=SystemEventType.NODE_RECOVERED,
            node_id=node.node_id,
            message=f"Node {node.node_id} heartbeat detected. Transitioning to RECOVERING state.",
            severity="WARNING",
            details={"state": "RECOVERING"}
        )
        knowledge_base.record_event(rec_event)
        log_event_db(
            rec_event.id, rec_event.timestamp, rec_event.formatted_time,
            rec_event.event_type.value, rec_event.node_id, rec_event.message,
            rec_event.severity, rec_event.details
        )
        await websocket_manager.broadcast("node_update", node.model_dump())

        # Give a short async delay for simulated recovery validation
        await asyncio.sleep(self.recovery_delay)

        node.status = NodeStatus.ONLINE
        node.heartbeat_status = "HEALTHY"
        node.last_heartbeat = time.time()

        online_event = SystemEvent(
            event_type=SystemEventType.NODE_RECOVERED,
            node_id=node.node_id,
            message=f"Node {node.node_id} successfully verified and reintegrated into active topology. Status: ONLINE.",
            severity="SUCCESS",
            details={"state": "ONLINE"}
        )
        knowledge_base.record_event(online_event)
        log_event_db(
            online_event.id, online_event.timestamp, online_event.formatted_time,
            online_event.event_type.value, online_event.node_id, online_event.message,
            online_event.severity, online_event.details
        )
        await websocket_manager.broadcast("node_recovered", {
            "node_id": node.node_id,
            "status": "ONLINE",
            "event": online_event.model_dump()
        })

        if self._on_node_online_cb:
            await self._on_node_online_cb(node.node_id)

heartbeat_manager = HeartbeatManager()
