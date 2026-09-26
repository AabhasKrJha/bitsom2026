"""Sentix FastAPI Application Entrypoint.

Provides modular routing for enterprise security telemetry ingestion,
log retrieval, enterprise topology introspection, and decision audit ledger.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes_ingest import router as ingest_router
from backend.app.api.routes_logs import router as logs_router
from backend.app.api.routes_topology import router as topology_router
from backend.app.api.routes_audit import router as audit_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sentix Autonomous Operations API",
        description="Cognitive decision engine & telemetry ingestion receiver for enterprise security operations",
        version="1.0.0",
    )

    # Enable CORS for Next.js frontend (e.g. http://localhost:3000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root health check
    @app.get("/")
    def health_check():
        return {
            "status": "healthy",
            "service": "Sentix Autonomous Operations API",
            "mode": "Cognitive Jev Evaluation & Audit Ledger",
        }

    # Register API Routers
    app.include_router(ingest_router)
    app.include_router(logs_router)
    app.include_router(topology_router)
    app.include_router(audit_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    from backend.app.core.config import API_HOST, API_PORT

    uvicorn.run("backend.app.main:app", host=API_HOST, port=API_PORT, reload=True)
