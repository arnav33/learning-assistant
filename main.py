from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.agent_api import router as agent_api_router
from backend.api.model_api import router as model_api_router
from backend.api.chat_api import router as chat_api_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(model_api_router, prefix="/api/v1/core/models", tags=["models"])
app.include_router(agent_api_router, prefix="/api/v1/core/agents", tags=["agents"])
app.include_router(chat_api_router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
