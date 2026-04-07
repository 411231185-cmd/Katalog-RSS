from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import agents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)

@app.get("/health")
async def health_check():
    agents_count = len(agents.agent_states)
    return {"status": "ok", "agents_count": agents_count, "telegram": "ok"}
