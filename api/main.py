"""
Generative AI Cloud Projects — Unified FastAPI Server
Exposes all 10 use cases through a REST API.
"""

import sys
import os
import time
import uuid
from typing import Optional, List
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from scripts.config import MODE, get_config_summary
from scripts.logger import get_logger
from scripts.metrics import MetricsCollector


# ─── Lifespan ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    app.state.metrics = MetricsCollector("api_metrics.db")
    app.state.logger = get_logger("api")
    yield
    app.state.metrics.close()


# ─── App ─────────────────────────────────────────────────────

app = FastAPI(
    title="Generative AI Cloud Projects API",
    description=(
        "Unified REST API for 10 Generative AI use cases across "
        "AWS, Azure, and Google Cloud."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response Models ───────────────────────────────

class MarketingRequest(BaseModel):
    content_type: str = Field("email", description="email | social_post | ad_copy")
    product: str = Field(..., description="Product name")
    audience: str = Field("general", description="Target audience")
    tone: str = Field("professional", description="Tone of voice")
    platform: Optional[str] = Field(None, description="Social platform")
    benefits: Optional[str] = None
    pain_point: Optional[str] = None
    usp: Optional[str] = None
    cta: Optional[str] = None


class ImageRequest(BaseModel):
    description: str = Field(..., description="Product description")
    style: str = Field("product", description="Style preset")
    extras: Optional[str] = None


class CodeCompletionRequest(BaseModel):
    code: str = Field(..., description="Code snippet to complete")
    language: str = Field("python", description="Programming language")


class SupportQueryRequest(BaseModel):
    query: str = Field(..., description="Customer query")


class MedicalReportRequest(BaseModel):
    report: Optional[str] = Field(None, description="Medical report text")


class LearningRequest(BaseModel):
    topic: str = Field(..., description="Learning topic")
    level: str = Field("beginner", description="beginner | intermediate | advanced")
    content_format: str = Field("lesson", description="lesson | exercise | quiz")
    student_context: Optional[str] = None


class AdDesignRequest(BaseModel):
    product: str = Field(..., description="Product name")
    headline: str = Field(..., description="Ad headline")
    ad_format: str = Field("instagram_post", description="Ad format")
    style: str = Field("modern", description="Visual style")


class CodeReviewRequest(BaseModel):
    code: str = Field(..., description="Code to review")
    language: str = Field("python", description="Programming language")


class LegalAnalysisRequest(BaseModel):
    query: str = Field(..., description="Legal query")
    contract_text: Optional[str] = None


class SimulationRequest(BaseModel):
    scenario: str = Field(..., description="Scenario description")


class APIResponse(BaseModel):
    request_id: str
    use_case: str
    mode: str
    result: dict
    latency_ms: float


# ─── Middleware: Request Tracking ────────────────────────────

@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track all API requests with timing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.time()

    response = await call_next(request)

    latency_ms = (time.time() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Latency-MS"] = f"{latency_ms:.2f}"
    return response


# ─── Health & Status ─────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "mode": MODE}


@app.get("/config", tags=["System"])
async def config_status():
    """Show current configuration (no secrets)."""
    return get_config_summary()


@app.get("/metrics", tags=["System"])
async def get_metrics(request: Request):
    """Get today's usage metrics."""
    return request.app.state.metrics.get_daily_summary()


@app.get("/metrics/by-use-case", tags=["System"])
async def get_metrics_by_use_case(request: Request, days: int = 7):
    """Get metrics breakdown by use case."""
    return request.app.state.metrics.get_summary_by_use_case(days)


# ─── Use Case Endpoints ─────────────────────────────────────

@app.post("/api/v1/marketing", response_model=APIResponse, tags=["01 - Marketing"])
async def generate_marketing_content(req: MarketingRequest, request: Request):
    """Generate marketing content (email, social post, ad copy)."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.01-marketing-content-azure.main")
        result = uc.generate(
            req.content_type,
            product=req.product,
            audience=req.audience,
            tone=req.tone,
            platform=req.platform,
            benefits=req.benefits,
            pain_point=req.pain_point,
            usp=req.usp,
            cta=req.cta,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "marketing", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="marketing_content",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/image", response_model=APIResponse, tags=["02 - Product Image"])
async def generate_product_image(req: ImageRequest, request: Request):
    """Generate a product image."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.02-product-image-aws.main")
        result = uc.generate(req.description, style=req.style, extras=req.extras)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "product_image", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="product_image",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/code/complete", response_model=APIResponse, tags=["03 - Code"])
async def complete_code(req: CodeCompletionRequest, request: Request):
    """Complete a code snippet."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.03-code-completion-gcp.main")
        result = uc.complete(req.code, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "code_completion", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="code_completion",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/support", response_model=APIResponse, tags=["04 - Support"])
async def customer_support_query(req: SupportQueryRequest, request: Request):
    """Answer a customer support question using RAG."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.04-customer-support-aws.main")
        result = uc.query(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "customer_support", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="customer_support",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/healthcare", response_model=APIResponse, tags=["05 - Healthcare"])
async def summarize_medical_report(req: MedicalReportRequest, request: Request):
    """Summarize a medical report with PHI redaction."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.05-healthcare-summarization-azure.main")
        result = uc.summarize(report_text=req.report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "healthcare", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="healthcare_summarization",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/learning", response_model=APIResponse, tags=["06 - Learning"])
async def generate_learning_content(req: LearningRequest, request: Request):
    """Generate personalized learning content."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.06-personalized-learning-gcp.main")
        result = uc.generate(
            req.topic,
            level=req.level,
            content_format=req.content_format,
            student_context=req.student_context,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "learning", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="personalized_learning",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/ad", response_model=APIResponse, tags=["07 - Ad Design"])
async def design_ad(req: AdDesignRequest, request: Request):
    """Generate a creative ad design."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.07-creative-ad-gcp.main")
        result = uc.generate(
            req.product,
            headline=req.headline,
            ad_format=req.ad_format,
            style=req.style,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "ad_design", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="creative_ad",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/code/review", response_model=APIResponse, tags=["08 - Code Review"])
async def review_code(req: CodeReviewRequest, request: Request):
    """Review code for quality, security, and best practices."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.08-automated-code-review-aws.main")
        result = uc.review(req.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "code_review", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="code_review",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/legal", response_model=APIResponse, tags=["09 - Legal"])
async def analyze_legal_document(req: LegalAnalysisRequest, request: Request):
    """Analyze legal documents for risk and compliance."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.09-legal-analysis-azure.main")
        result = uc.analyze(req.query, contract_text=req.contract_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "legal_analysis", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="legal_analysis",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


@app.post("/api/v1/manufacturing", response_model=APIResponse, tags=["10 - Manufacturing"])
async def simulate_manufacturing(req: SimulationRequest, request: Request):
    """Simulate manufacturing scenario impact."""
    start = time.time()
    try:
        from importlib import import_module
        uc = import_module("use-cases.10-manufacturing-simulation-gcp.main")
        result = uc.simulate(req.scenario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = (time.time() - start) * 1000
    request.app.state.metrics.track_request(
        "manufacturing", "api", MODE, 0, 0.0, latency
    )
    return APIResponse(
        request_id=request.state.request_id,
        use_case="manufacturing_simulation",
        mode=MODE,
        result=result,
        latency_ms=latency,
    )


# ─── Run ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
