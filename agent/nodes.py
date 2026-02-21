from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import AgentState
from agent.prompts import get_sales_system_prompt
from agent.tools import browser_tools
from pydantic import BaseModel, Field

class IntentGuard(BaseModel):
    is_off_topic: bool = Field(
        description="True ONLY if the user is asking for things unrelated to the software demo."
    )

# Usamos Gemini 1.5 Flash para el supervisor (rápido y gratis/barato)
routing_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
supervisor_chain = routing_llm.with_structured_output(IntentGuard)

# Usamos Gemini 1.5 Pro para el agente (visión superior)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
llm_with_tools = llm.bind_tools(browser_tools)

def supervisor_node(state: AgentState):
    last_message = state["messages"][-1].content
    
    # Prompt simple para el guardrail
    prompt = f"System: You are a security router. User says: '{last_message}'. Is it off-topic? Return JSON."
    
    try:
        classification = supervisor_chain.invoke(prompt)
        return {"is_off_topic": classification.is_off_topic}
    except Exception:
        return {"is_off_topic": False}

def sales_agent_node(state: AgentState):
    # 1. Generar prompt de sistema
    sys_prompt_text = get_sales_system_prompt(
        company_context=state["company_context"],
        current_url=state["current_url"],
        demo_stage=state["demo_stage"]
    )
    
    # 2. IMPORTANTE: Gemini prefiere el SystemMessage al principio
    messages_to_pass = [SystemMessage(content=sys_prompt_text)]
    
    # 3. Añadir historial
    if len(state["messages"]) > 1:
        messages_to_pass.extend(state["messages"][:-1])
    
    # 4. Preparar el último mensaje con la imagen
    last_human_msg = state["messages"][-1].content
    
    if state.get("current_screenshot"):
        # Formato compatible con Gemini
        content = [
            {"type": "text", "text": last_human_msg},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{state['current_screenshot']}"}
            }
        ]
        messages_to_pass.append(HumanMessage(content=content))
    else:
        messages_to_pass.append(HumanMessage(content=last_human_msg))
        
    # 5. Invocar a Gemini
    response = llm_with_tools.invoke(messages_to_pass)
    
    return {"messages": [response]}