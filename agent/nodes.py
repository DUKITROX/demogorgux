from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import AgentState
from agent.prompts import get_sales_system_prompt
from agent.tools import browser_tools
from pydantic import BaseModel, Field

GEMINI_MODEL = "gemini-2.5-flash"

class IntentGuard(BaseModel):
    is_off_topic: bool = Field(
        description="True ONLY if the user asks for things that are completely out of context (such as recipes, jokes, or writing code). False for greetings, questions about the website, or commands."
    )

# Modelos válidos según list_google_models.py (generativelanguage.googleapis.com)
routing_llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0)
supervisor_chain = routing_llm.with_structured_output(IntentGuard)

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, streaming=True)
llm_with_tools = llm.bind_tools(browser_tools)

def supervisor_node(state: AgentState):
    last_message = state["messages"][-1].content

    # Detailed prompt for the guardrail (in English)
    prompt = f"""System: You are the security filter for a web sales agent.
The user says: '{last_message}'.
RULES:
1. If it's a greeting ("Hello", "Hi") -> is_off_topic = False
2. If the user asks what you can do or what's on the screen -> is_off_topic = False
3. If the user gives a command to interact with the website -> is_off_topic = False
4. If the user asks for irrelevant things (recipes, poems, hacking, or programming) -> is_off_topic = True

Evaluate and return the JSON."""
    
    try:
        classification = supervisor_chain.invoke(prompt)
        return {"is_off_topic": classification.is_off_topic}
    except Exception:
        # If in doubt or error, let it pass
        return {"is_off_topic": False}

async def sales_agent_node(state: AgentState):
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
        messages_to_pass.extend(state["messages"][-5:-1])
    
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
        
    # Usar astream para que el API pueda enviar tokens en tiempo real (SSE)
    response = None
    async for chunk in llm_with_tools.astream(
        messages_to_pass,
        config={"tags": ["main_agent"]},
    ):
        if response is None:
            response = chunk
        else:
            response = response + chunk
    return {"messages": [response]}