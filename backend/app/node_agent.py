import argparse
import asyncio
import time
import httpx
import os

async def run_agent(node_id: str, controller_url: str):
    print(f"[NODE AGENT {node_id}] Booting up. Target Controller: {controller_url}")
    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            try:
                # 1. Fetch current node status & telemetry
                res = await client.get(f"{controller_url}/api/nodes/{node_id}")
                if res.status_code == 200:
                    node_data = res.json()
                    status = node_data.get("status")
                    sec_level = node_data.get("security_level")
                    risk = node_data.get("threat_score")
                    print(f"[{node_id}] Heartbeat OK | Status: {status} | Level: {sec_level} | Risk: {risk}")
                elif res.status_code == 404:
                    print(f"[{node_id}] Node not found in controller registry")
            except Exception as e:
                print(f"[{node_id}] Connection to controller failed: {e}")

            await asyncio.sleep(2.0)

def main():
    parser = argparse.ArgumentParser(description="Distributed Node Security Agent")
    parser.add_argument("--node-id", default=os.getenv("NODE_ID", "EDGE-01"), help="Node ID")
    parser.add_argument("--controller", default=os.getenv("CONTROLLER_URL", "http://localhost:8000"), help="Controller URL")
    args = parser.parse_args()

    asyncio.run(run_agent(args.node_id, args.controller))

if __name__ == "__main__":
    main()
