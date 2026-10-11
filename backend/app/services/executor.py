import time
from typing import Optional
from ..models.node import NodeState, MapeKStage, SecurityLevel
from ..models.security import AdaptationRecord, AdaptationMode
from ..models.event import SystemEvent, SystemEventType
from .planner import AdaptationPlan
from .knowledge import knowledge_base
from ..core.websocket_manager import websocket_manager
from ..core.database import log_event_db, log_adaptation_db

class Executor:
    async def execute_plan(
        self,
        node: NodeState,
        plan: AdaptationPlan,
        adaptation_mode: AdaptationMode = AdaptationMode.FULL_ADAPTATION
    ) -> Optional[AdaptationRecord]:
        node.mape_k_stage = MapeKStage.EXECUTE
        node.active_restrictions = plan.restrictions
        node.last_adaptation = time.strftime("%H:%M:%S")

        level_changed = (node.security_level != plan.target_level)
        prev_level = node.security_level
        node.security_level = plan.target_level

        adapt_record = None

        if level_changed:
            adapt_record = AdaptationRecord(
                node_id=node.node_id,
                previous_level=prev_level,
                new_level=plan.target_level,
                action_taken=plan.action,
                trigger_threat=plan.threat_type.value,
                adaptation_mode=adaptation_mode,
                affected_nodes=[node.node_id],
                details=plan.reason
            )
            knowledge_base.record_adaptation(adapt_record)
            log_adaptation_db(
                adapt_record.id,
                adapt_record.timestamp,
                adapt_record.node_id,
                adapt_record.previous_level.value,
                adapt_record.new_level.value,
                adapt_record.action_taken.value,
                adapt_record.trigger_threat,
                adapt_record.adaptation_mode.value,
                adapt_record.affected_nodes,
                adapt_record.details
            )

            # Security level changed event
            evt_severity = "WARNING" if plan.target_level.level_int <= 3 else "INFO"
            if plan.target_level.level_int == 1:
                evt_severity = "CRITICAL"

            sec_event = SystemEvent(
                event_type=SystemEventType.SECURITY_LEVEL_CHANGED,
                node_id=node.node_id,
                message=f"{node.node_id} security posture adapted: {prev_level.value} -> {plan.target_level.value} ({plan.action.value})",
                severity=evt_severity,
                details={
                    "previous_level": prev_level.value,
                    "new_level": plan.target_level.value,
                    "action": plan.action.value,
                    "threat": plan.threat_type.value,
                    "restrictions": plan.restrictions
                }
            )
            knowledge_base.record_event(sec_event)
            log_event_db(
                sec_event.id,
                sec_event.timestamp,
                sec_event.formatted_time,
                sec_event.event_type.value,
                sec_event.node_id,
                sec_event.message,
                sec_event.severity,
                sec_event.details
            )

            await websocket_manager.broadcast("security_level_changed", {
                "event": sec_event.model_dump(),
                "adaptation": adapt_record.model_dump()
            })

        return adapt_record

executor_engine = Executor()
