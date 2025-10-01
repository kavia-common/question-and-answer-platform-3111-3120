from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from src.api.config import get_settings
from src.api.database import Base, engine
from src.api.routers import answers as answers_router
from src.api.routers import auth as auth_router
from src.api.routers import questions as questions_router

# Create all tables on startup (SQLite/local)
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="QnA Backend API",
    description=(
        "Handles user authentication, questions, and answers. "
        "Integrates with OpenAI to generate answers. "
        "Theme: Ocean Professional (blue & amber accents)."
    ),
    version=settings.api_version,
    contact={
        "name": "QnA Platform",
        "url": "https://example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "Health", "description": "Health checks and service info"},
        {"name": "Auth", "description": "User authentication (signup, login, profile)"},
        {"name": "Questions", "description": "Create and list questions"},
        {"name": "Answers", "description": "Generate and list answers"},
    ],
)

# CORS for Angular frontend (comma-separated origins, default "*")
allow_origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ocean Professional themed docs
OCEAN_PRIMARY = "#2563EB"
OCEAN_AMBER = "#F59E0B"
OCEAN_ERROR = "#EF4444"
OCEAN_TEXT = "#111827"
OCEAN_BG = "#f9fafb"
OCEAN_SURFACE = "#ffffff"

SWAGGER_CUSTOM_CSS = f"""
:root {{
  --primary: {OCEAN_PRIMARY};
  --secondary: {OCEAN_AMBER};
  --text: {OCEAN_TEXT};
  --surface: {OCEAN_SURFACE};
  --bg: {OCEAN_BG};
}}

html, body {{
  background: var(--bg) !important;
  color: var(--text) !important;
}}

.topbar, .swagger-ui .info {{
  background: linear-gradient(135deg, rgba(37,99,235,0.10), rgba(243,244,246,1));
  border-bottom: 1px solid #e5e7eb;
}}

.swagger-ui .topbar .download-url-wrapper .select-label {{
  color: var(--text);
}}

.swagger-ui .topbar .download-url-wrapper input[disabled] {{
  background-color: #eef2ff;
}}

.swagger-ui .btn.authorize, .opblock-summary-control {{
  border-radius: 10px !important;
}}

.swagger-ui .btn.authorize {{
  background-color: {OCEAN_PRIMARY} !important;
  border-color: {OCEAN_PRIMARY} !important;
}}

.swagger-ui .btn.execute.opblock-control__btn {{
  background-color: {OCEAN_AMBER} !important;
  border-color: {OCEAN_AMBER} !important;
  color: #1f2937 !important;
}}

.opblock-summary-method, .opblock-summary-path, .opblock-summary-operation-id {{
  border-radius: 6px;
}}

.swagger-ui .opblock {{
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(17,24,39,0.05);
}}

.swagger-ui .errors-wrapper {{
  color: {OCEAN_ERROR} !important;
}}
"""


@app.get("/", tags=["Health"], summary="Health Check", description="Check if the service is running.")
def health_check():
    """
    PUBLIC_INTERFACE
    Returns a simple health check response with server time.
    """
    from datetime import datetime

    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html() -> Any:
    """
    PUBLIC_INTERFACE
    Returns the Swagger UI with Ocean Professional theme overrides.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Docs",
        swagger_favicon_url="",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        init_oauth=None,
        swagger_ui_parameters={"docExpansion": "list", "defaultModelsExpandDepth": 1},
        **{"custom_css": SWAGGER_CUSTOM_CSS},
    )


@app.get("/redoc", include_in_schema=False)
def redoc_html() -> Any:
    """
    PUBLIC_INTERFACE
    Returns ReDoc UI.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
    )


# Mount routers
app.include_router(auth_router.router)
app.include_router(questions_router.router)
app.include_router(answers_router.router)
