import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from .core.config import settings
from .core.websocket_manager import websocket_manager
from .state.system_state import system_state
from .api.routes_nodes import router as nodes_router
from .api.routes_simulation import router as sim_router
from .api.routes_events import router as events_router
from .api.routes_security import router as sec_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[STARTUP] Initializing Adaptive Security Framework topology...")
    system_state.controller.initialize_topology()
    # Start background simulation ticker
    system_state.simulation.start_simulation()
    print("[STARTUP] Simulation ticker active. Ready for connections.")
    yield
    # Shutdown
    print("[SHUTDOWN] Stopping simulation ticker...")
    system_state.simulation.stop_simulation()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(nodes_router, prefix=settings.API_PREFIX)
app.include_router(sim_router, prefix=settings.API_PREFIX)
app.include_router(events_router, prefix=settings.API_PREFIX)
app.include_router(sec_router, prefix=settings.API_PREFIX)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        # Send initial full state immediately upon connection
        init_data = {
            "nodes": {n.node_id: n.model_dump() for n in system_state.get_all_nodes()},
            "system_status": system_state.get_status().model_dump(),
            "events": [e.model_dump() if hasattr(e, "model_dump") else e for e in system_state.get_events(30)],
            "threats": [t.model_dump() if hasattr(t, "model_dump") else t for t in system_state.get_threats()[:20]]
        }
        await websocket.send_json({
            "type": "init_state",
            "data": init_data
        })

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket client error: {e}")
        await websocket_manager.disconnect(websocket)

# Static files for frontend build if present
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "framework": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "ONLINE",
            "api_docs": "/docs",
            "ws_endpoint": "/ws"
        }

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
