import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse # <-- NUEVO: Para enviar datos en streaming

from agent.graph import app as langgraph_agent
from agent.state import AgentState
from browser.controller import start_browser, take_screenshot
from langchain_core.messages import HumanMessage

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando servidor API y arrancando Playwright...")
    await start_browser(start_url="https://demo.playwright.dev/todomvc/#/")
    yield
    print("🛑 Apagando servidor y cerrando navegador...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

sessions = {}


def _chunk_content_to_text(content) -> str:
    """Convierte el content del chunk (str o lista multimodal) a un único string."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return "".join(parts)
    return ""


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # --- 1. Inicializar sesión ---
    if request.session_id not in sessions:
        sessions[request.session_id] = AgentState(
            messages=[],
            demo_stage="greeting",
            current_url="https://demo.playwright.dev/todomvc/#/",
            company_context="You are testing a demo web app.",
            current_screenshot=None,
            is_off_topic=False
        )
    
    state = sessions[request.session_id]
    
    # --- 2. Preparar el estado antes de invocar a Gemini ---
    foto_b64 = await take_screenshot()
    state["current_screenshot"] = foto_b64
    state["messages"].append(HumanMessage(content=request.message))
    
    # --- 3. Generador de Streaming ---
    async def event_generator():
        print("🧠 Gemini está procesando la interfaz (Streaming mode)...")
        
        # Usamos astream_events para capturar los tokens en tiempo real
        # La versión V2 de astream_events es la recomendada
        async for event in langgraph_agent.astream_events(state, version="v2"):
            kind = event["event"]
            
            # A) STREAMING DE TEXTO: Gemini está hablando
            if kind == "on_chat_model_stream":
                # Filtramos para que solo salgan los tokens del nodo 'sales_agent'
                if event["metadata"].get("langgraph_node") == "sales_agent":
                    raw = event["data"]["chunk"].content
                    content = _chunk_content_to_text(raw)
                    if content:
                        payload = json.dumps({"type": "token", "content": content})
                        yield f"data: {payload}\n\n"
            
            # B) HERRAMIENTA LLAMADA: Gemini decide usar una Tool
            elif kind == "on_tool_start":
                tool_name = event["name"]
                payload = json.dumps({"type": "tool_start", "content": f"⚙️ Usando herramienta: {tool_name}..."})
                yield f"data: {payload}\n\n"
                
            # C) GRAFO TERMINADO: Guardamos el estado final y enviamos la foto
            elif kind == "on_chain_end" and event["name"] == "LangGraph":
                # Actualizamos la sesión en memoria con el estado final
                sessions[request.session_id] = event["data"]["output"]
                
                # Sacamos foto final y la enviamos
                foto_despues_b64 = await take_screenshot()
                payload = json.dumps({"type": "screenshot", "content": foto_despues_b64})
                yield f"data: {payload}\n\n"
                
        # D) CIERRE DE CONEXIÓN
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    # Retornamos la respuesta como un stream usando el generador
    return StreamingResponse(event_generator(), media_type="text/event-stream")