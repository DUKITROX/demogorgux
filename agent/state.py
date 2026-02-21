from typing import Annotated, TypedDict, List, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # The conversation history (text and tool call responses).
    # 'add_messages' ensures that new messages are appended to the list rather than overwritten.
    messages: Annotated[List[AnyMessage], add_messages]
    
    # --- THE EYES ---
    # Screenshot in Base64 format. LiveKit will update it each turn.
    current_screenshot: Optional[str] 
    
    # --- BUSINESS CONTEXT ---
    current_url: str          # Where we're currently browsing
    company_context: str      # Which company we're demoing and what the objective is
    demo_stage: str           # Stage of the sales process (e.g., "start", "showing_dashboard", "closing")
    
    # --- GUARDRAIL ---
    is_off_topic: bool        # Security flag if the user tries to hack the prompt