from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
import asyncio
from core.telegram_notify import send_telegram

router = APIRouter()
agent_states = {}

class AgentRunRequest(BaseModel):
    prompt: str
    params: dict

@router.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, request: AgentRunRequest):
    if agent_id not in agent_states:
        raise HTTPException(status_code=404, detail="Агент не найден")

    process = subprocess.Popen(["python", f"agents/{agent_id}/agent.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    agent_states[agent_id] = {"status": "running", "process": process}

    # Отправка уведомления в Telegram
    message = f"Запущен агент: {agent_id} с параметрами: {request.params}"
    await send_telegram(message)

    return {"status": "running"}

@router.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    state = agent_states.get(agent_id)
    if not state:
        raise HTTPException(status_code=404, detail="Агент не найден")
    
    return {"status": state["status"], "last_result": state.get("last_result")}

@router.post("/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, message: str):
    # Логика для общения с агентом
    pass

@router.get("/agents/list")
async def list_agents():
    agents = []
    for filename in os.listdir("agents"):
        if filename.endswith(".yaml"):
            agents.append(filename[:-5])  # Убираем .yaml
    return agents
