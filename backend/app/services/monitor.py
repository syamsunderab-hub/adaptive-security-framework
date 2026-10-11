import time
import asyncio
from typing import Optional, Dict, Any
from ..models.node import NodeState, NodeTelemetry, MapeKStage, NodeStatus
from ..models.threat import ThreatEvent, ThreatType, ThreatSeverity
from ..models.event import SystemEvent, SystemEventType
from ..models.security import AdaptationMode
from .analyzer import analyzer_engine
from .planner import planner_engine
from .executor import executor_engine
from .knowledge import knowledge_base
from ..core.websocket_manager import websocket_manager
from ..core.database import log_threat_db, log_event_db

class Monitor:
    async def run_mape_k_cycle(
        self,
        node: NodeState,
        adaptation_mode: AdaptationMode = AdaptationMode.FULL_ADAPTATION,
        propagate_callback = None
    ) -> NodeState:
        """
        Executes a real local MAPE-K loop for a node:
        Monitor -> Analyze -> Plan -> Execute
        """
        if node.status != NodeStatus.ONLINE:
            node.mape_k_stage = MapeKStage.IDLE
            return node

        # 1. MONITOR STAGE
        node.mape_k_stage = MapeKStage.MONITOR
        telemetry = NodeTelemetry(
            cpu_percent=node.cpu_usage,
            network_traffic_pps=node.network_traffic,
            connection_count=node.connections,
            failed_auth_count=node.failed_auths,
            packet_rate=node.network_traffic
        )

        # 2. ANALYZE STAGE
        node.mape_k_stage = MapeKStage.ANALYZE
        baseline = knowledge_base.get_baseline(node.node_type.value)
        risk_score, threat_type, severity, confidence, desc, rec_action = analyzer_engine.analyze(
            telemetry, baseline
        )
        
        node.threat_score = risk_score
        node.current_threat = threat_type.value
        node.threat_details = desc

        # If threat detected and not normal, log threat event
        if threat_type != ThreatType.NORMAL:
            threat_event = ThreatEvent(
                node_id=node.node_id,
                threat_type=threat_type,
                severity=severity,
                confidence=confidence,
                description=desc,
                recommended_action=rec_action,
                metrics_snapshot={
                    "cpu": node.cpu_usage,
                    "traffic": node.network_traffic,
                    "connections": node.connections,
                    "failed_auths": node.failed_auths
                }
            )
            knowledge_base.record_threat(threat_event)
            log_threat_db(
                threat_event.threat_id,
                threat_event.node_id,
                threat_event.threat_type.value,
                threat_event.severity.value,
                threat_event.confidence,
                threat_event.timestamp,
                threat_event.description,
                threat_event.recommended_action,
                threat_event.metrics_snapshot
            )

            # Broadcast threat detection
            th_evt = SystemEvent(
                event_type=SystemEventType.THREAT_DETECTED,
                node_id=node.node_id,
                message=f"Threat detected on {node.node_id}: {threat_type.value} ({severity.value}) - Risk Score: {risk_score}",
                severity="CRITICAL" if severity == ThreatSeverity.CRITICAL else "WARNING",
                details={
                    "threat_id": threat_event.threat_id,
                    "type": threat_type.value,
                    "severity": severity.value,
                    "risk_score": risk_score
                }
            )
            knowledge_base.record_event(th_evt)
            log_event_db(
                th_evt.id, th_evt.timestamp, th_evt.formatted_time,
                th_evt.event_type.value, th_evt.node_id, th_evt.message,
                th_evt.severity, th_evt.details
            )
            await websocket_manager.broadcast("threat_detected", threat_event.model_dump())

        # 3. PLAN STAGE
        node.mape_k_stage = MapeKStage.PLAN
        plan = planner_engine.plan(
            node, risk_score, threat_type, severity, rec_action
        )

        # 4. EXECUTE STAGE
        node.mape_k_stage = MapeKStage.EXECUTE
        await executor_engine.execute_plan(node, plan, adaptation_mode)

        # Propagation upstream if plan flagged it
        if plan.should_propagate_upstream and propagate_callback and plan.upstream_target:
            await propagate_callback(plan.upstream_target, node.node_id, threat_type, plan.target_level)

        # Completed cycle - return to IDLE after execute
        node.mape_k_stage = MapeKStage.IDLE
        return node

monitor_engine = Monitor()
