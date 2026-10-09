"""
VERIACT — Pre-Execution Verification Gateway (FastAPI Entrypoint)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.v1.intercept import router as intercept_router
from app.api.v1.escalation import router as escalation_router
from app.api.v1.traces import router as traces_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.sandbox import router as sandbox_router
from app.api.v1.ground_truth import router as ground_truth_router
from app.api.v1.benchmark import router as benchmark_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Pre-execution runtime verification gateway for autonomous AI agents.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 Routers
app.include_router(intercept_router, prefix=settings.API_V1_STR, tags=["Interception"])
app.include_router(escalation_router, prefix=settings.API_V1_STR, tags=["Escalation Queue"])
app.include_router(traces_router, prefix=settings.API_V1_STR, tags=["Audit Traces"])
app.include_router(analytics_router, prefix=settings.API_V1_STR, tags=["Analytics & Telemetry"])
app.include_router(sandbox_router, prefix=settings.API_V1_STR, tags=["Attack Sandbox"])
app.include_router(ground_truth_router, prefix=settings.API_V1_STR, tags=["Ground Truth"])
app.include_router(benchmark_router, prefix=settings.API_V1_STR, tags=["Benchmark & Pareto"])

@app.get("/", tags=["Health"])
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "tagline": "Verify the Action. Then Let the Agent Act.",
        "status": "ONLINE",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "HEALTHY", "guardrail": "ACTIVE", "fail_closed": True}
