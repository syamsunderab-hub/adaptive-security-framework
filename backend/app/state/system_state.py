from ..services.global_controller import global_controller
from ..services.simulation_engine import simulation_engine
from ..services.knowledge import knowledge_base
from ..core.websocket_manager import websocket_manager
from ..core.database import get_recent_events_db

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
        # Merge in-memory recent events with DB if available
        if self.knowledge.events_history:
            return self.knowledge.events_history[:limit]
        return get_recent_events_db(limit)

    def get_threats(self):
        return self.knowledge.threats_history

    def get_adaptations(self):
        return self.knowledge.adaptation_history

system_state = SystemState()
