from ..services.global_controller import global_controller
from ..services.simulation_engine import simulation_engine
from ..services.knowledge import knowledge_base
from ..core.websocket_manager import websocket_manager
from ..core.database import get_recent_events_db, get_recent_adaptations_db

class SystemState:
    def __init__(self):
        self.controller = global_controller
        self.simulation = simulation_engine
        self.knowledge = knowledge_base
        self.ws = websocket_manager

    def get_all_nodes(self):
        return list(self.controller.nodes.values())

    def get_node(self, node_id: str):
        return self.controller.nodes.get(node_id)

    def get_status(self):
        return self.controller.get_system_status()

    def get_events(self, limit: int = 50):
        memory = [e.model_dump() for e in self.knowledge.events_history[:limit]]
        durable = get_recent_events_db(limit)
        merged = {item["id"]: item for item in durable}
        merged.update({item["id"]: item for item in memory})
        return sorted(merged.values(), key=lambda item: item.get("timestamp", 0), reverse=True)[:limit]

    def get_threats(self):
        return self.knowledge.threats_history

    def get_adaptations(self):
        memory = [a.model_dump() for a in self.knowledge.adaptation_history]
        return memory or get_recent_adaptations_db()

system_state = SystemState()
