import asyncio
import logging
import base64
import urllib.parse
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()
# Import our Brain and Body
from agent.graph import app as langgraph_agent
from agent.state import AgentState
from browser.controller import start_browser, take_screenshot, get_current_page, close_browser
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("Interactive-Test")


# ---------------------------------------------------------
# THE TRICKY UI: We inject this HTML to try and fool Claude
# ---------------------------------------------------------
TRICKY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; padding: 40px; background: #f9f9f9; }
        .fake-button { background: #ff4444; color: white; padding: 10px 20px; text-align: center; display: inline-block; border-radius: 5px; cursor: default; }
        .real-button { background: #00C851; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .fake-link { color: blue; text-decoration: underline; cursor: text; }
        .hidden-input { opacity: 0.2; }
    </style>
</head>
<body>
    <h2>🤖 Vision AI - Tricky Test Environment</h2>
    <p>This page is designed to confuse the AI.</p>
    
    <hr>
    <h3>Trap 1: Ambiguity</h3>
    <button class="real-button">Save Changes</button>
    <button class="real-button" style="background: #33b5e5;">Save</button>
    
    <hr>
    <h3>Trap 2: Fake Elements</h3>
    <div class="fake-button">Delete Account</div> 
    <br><br>
    <span class="fake-link">Forgot Password?</span>
    
    <hr>
    <h3>Trap 3: Hidden Inputs</h3>
    <input type="text" placeholder="Normal input..." />
    <br><br>
    <input type="text" class="hidden-input" placeholder="Secret input..." />
</body>
</html>
"""

async def save_debug_image(b64_string: str, filename: str):
    """Saves the Base64 screenshot to the hard drive."""
    if not b64_string:
        return
    image_data = base64.b64decode(b64_string)
    image = Image.open(io.BytesIO(image_data))
    image.save(filename)
    logger.info(f"📸 Screenshot saved: {filename}")

async def run_interactive_chat():
    logger.info("Starting Playwright and loading the TRICKY HTML...")
    
    # We use a data URI to load our custom HTML directly into Playwright
    data_url = "data:text/html;charset=utf-8," + urllib.parse.quote(TRICKY_HTML)
    await start_browser(start_url=data_url)
    
    # Initialize the memory
    state = AgentState(
        messages=[],
        demo_stage="testing",
        current_url="local://tricky-test",
        company_context="You are navigating a tricky testing environment. Pay close attention to the user's instructions.",
        current_screenshot=None,
        is_off_topic=False
    )
    
    step_counter = 1
    print("\n" + "="*50)
    print("🟢 INTERACTIVE CHAT STARTED")
    print("  • Escribe 'exit' o 'quit' para salir del chat.")
    print("  • Prueba: 'Click on Delete Account', 'Type hello in the secret input', 'Click Save'.")
    print("="*50 + "\n")

    while True:
        user_input = input("\n🧑 You: ")
        
        if user_input.lower().strip() in ['exit', 'quit']:
            logger.info("Ending test...")
            await close_browser()
            print("\n👋 Chat cerrado. Hasta luego.\n")
            break
            
        if not user_input.strip():
            continue

        # 1. Take 'Before' screenshot
        foto_antes = await take_screenshot()
        await save_debug_image(foto_antes, f"step_{step_counter}_before.jpg")
        
        # 2. Add input and screenshot to state
        state["messages"].append(HumanMessage(content=user_input))
        state["current_screenshot"] = foto_antes
        
        # 3. Let Claude think and act
        logger.info("🧠 Agent is looking at the screen and deciding...")
        new_state = await langgraph_agent.ainvoke(state)
        
        # 4. Print the text response
        agent_response = new_state["messages"][-1].content
        print(f"\n🤖 Agent: {agent_response}")
        
        # 5. Take 'After' screenshot to see the result of its tools
        foto_despues = await take_screenshot()
        await save_debug_image(foto_despues, f"step_{step_counter}_after.jpg")
        
        # Update memory for the next loop
        state["messages"] = new_state["messages"]
        step_counter += 1

if __name__ == "__main__":
    asyncio.run(run_interactive_chat())