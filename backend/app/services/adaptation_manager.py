from typing import Dict, List, Any
from ..models.node import NodeState, NodeStatus, SecurityLevel
from ..models.security import AdaptationMode
from .security_manager import security_level_manager

class AdaptationManager:
    def __init__(self):
        self.groups_definition = {
            "CLUSTER_ALPHA": {
                "name": "Fog Cluster Alpha",
                "fog_node": "FOG-01",
                "edge_nodes": ["EDGE-01", "EDGE-02"]
            },
            "CLUSTER_BETA": {
                "name": "Fog Cluster Beta",
                "fog_node": "FOG-02",
                "edge_nodes": ["EDGE-03", "EDGE-04"]
            },
            "CORE_BACKBONE": {
                "name": "Cloud Core Backbone",
                "cloud_node": "CLOUD",
                "edge_nodes": []
            }
        }

    def evaluate_adaptation_mode(self, nodes: Dict[str, NodeState]) -> AdaptationMode:
        """
        FULL_ADAPTATION when all nodes are ONLINE.
        PARTIAL_ADAPTATION if any node is OFFLINE or ISOLATED.
        """
        for node in nodes.values():
            if node.status in (NodeStatus.OFFLINE, NodeStatus.ISOLATED):
                return AdaptationMode.PARTIAL_ADAPTATION
        return AdaptationMode.FULL_ADAPTATION

    def get_active_adaptation_groups(self, nodes: Dict[str, NodeState]) -> List[Dict[str, Any]]:
        result = []
        for g_id, g_info in self.groups_definition.items():
            all_members = []
            if "cloud_node" in g_info:
                all_members.append(g_info["cloud_node"])
            if "fog_node" in g_info:
                all_members.append(g_info["fog_node"])
            all_members.extend(g_info.get("edge_nodes", []))

            online_members = [
                m for m in all_members
                if m in nodes and nodes[m].status == NodeStatus.ONLINE
            ]
            offline_members = [
                m for m in all_members
                if m in nodes and nodes[m].status == NodeStatus.OFFLINE
            ]
            levels = [
                nodes[m].security_level for m in online_members if m in nodes
            ]
            most_restrictive = security_level_manager.get_most_restrictive(levels)

            result.append({
                "group_id": g_id,
                "name": g_info["name"],
                "total_members": len(all_members),
                "online_members": online_members,
                "offline_members": offline_members,
                "is_degraded": len(offline_members) > 0,
                "most_restrictive_level": most_restrictive.value
            })
        return result

adaptation_manager = AdaptationManager()
