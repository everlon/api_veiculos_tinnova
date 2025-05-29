from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.routes import veiculo, web as web_routes
from app.database import engine, Base

# Base.metadata.create_all(bind=engine) # Não usar em produção

FRONTEND_PREFIX = "/ui"

app = FastAPI(
    title="API de Veículos Tinnova",
    description="API REST para gerenciamento de veículos e Interface HTMX",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar as origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(veiculo.router, prefix="/api/v1")
# Inclui o router da interface web HTMX
app.include_router(web_routes.web_router, prefix=FRONTEND_PREFIX, tags=["Interface Web"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Tratamento personalizado para erros de validação.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erro de validação",
            "errors": errors
        }
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc):
    """
    Tratamento personalizado para erros de validação do Pydantic.
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erro de validação",
            "errors": exc.errors()
        }
    )

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo ao sistema Tinnova",
        "api_docs": app.docs_url,
        "api_redoc": app.redoc_url,
        "frontend_ui": FRONTEND_PREFIX
    }
