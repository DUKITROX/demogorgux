from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.nodes import supervisor_node, sales_agent_node
from agent.tools import browser_tools

# 1. Create the node that automatically executes our tools (mouse, keyboard, scroll)
tool_node = ToolNode(browser_tools)

# 2. Define a specific node just for handling off-topic/malicious requests
def handle_off_topic_node(state: AgentState):
    """
    Returns a polite rejection without waking up the heavy multimodal LLM.
    This replaces the manual check we previously had inside 'sales_agent_node'.
    """
    msg = "Sorry, as a sales assistant I am only authorized to demonstrate this platform. Shall we get back to the demo?"
    return {"messages": [msg]}

# 3. Initialize the graph
workflow = StateGraph(AgentState)

# 4. Add all our "workstations" (Nodes)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("handle_off_topic", handle_off_topic_node)
workflow.add_node("sales_agent", sales_agent_node)
workflow.add_node("tools", tool_node)

# 5. Connect the start to the supervisor
workflow.add_edge(START, "supervisor")

# ---------------------------------------------------------
# THE NEW CONDITIONAL ROUTING: Where the intent is checked
# ---------------------------------------------------------
def route_after_supervisor(state: AgentState):
    """
    Reads the 'is_off_topic' flag set by the fast routing LLM.
    Decides which track the train should take.
    """
    if state.get("is_off_topic"):
        return "handle_off_topic"
    return "sales_agent"

# We apply the conditional switch immediately after the supervisor
workflow.add_conditional_edges(
    "supervisor",
    route_after_supervisor,
    {
        "handle_off_topic": "handle_off_topic",
        "sales_agent": "sales_agent"
    }
)

# If it went to the off-topic handler, the turn ends immediately
workflow.add_edge("handle_off_topic", END)

# ---------------------------------------------------------
# TOOL ROUTING: Deciding if we need to move the mouse or just speak
# ---------------------------------------------------------
def route_after_agent(state: AgentState):
    """
    Checks if Claude decided to use a tool (like clicking or typing).
    """
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"
    
    return END

# Connect the main agent to the tool router
workflow.add_conditional_edges(
    "sales_agent",
    route_after_agent,
    {
        "tools": "tools", 
        END: END
    }
)

# After using a tool, the agent must look at the new screen and speak
workflow.add_edge("tools", "sales_agent")

# 6. Compile the brain!
app = workflow.compile()