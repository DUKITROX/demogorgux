import asyncio
import logging
from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli, run_app
from livekit.plugins import openai

# Import our brain and our body
from agent.graph import app as langgraph_agent
from agent.state import AgentState
from browser.controller import start_browser, take_screenshot
from langchain_core.messages import HumanMessage
from server.video_track import BrowserVideoTrack


logger = logging.getLogger("demo-agent")

# Initial commercial context configuration for the agent
DEMO_COMPANY = "AcmeCorp - CRM software sales. Objective: Show 'Dashboard' and 'Prices'."
START_URL = "https://example.com" # Your software URL goes here

async def entrypoint(ctx: JobContext):
    """
    This function runs each time a user connects to the LiveKit room.
    """
    logger.info(f"New user connected to the room: {ctx.room.name}")
    
    # 1. Automatically subscribe to the user's audio tracks
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # 2. Initialize the senses (STT and TTS) using LiveKit plugins
    stt = openai.STT() # Converts speech to text
    tts = openai.TTS() # Converts text to speech

    # 3. Start the body (Playwright)
    logger.info("Starting the headless browser...")
    await start_browser(start_url=START_URL)

    video_streamer = BrowserVideoTrack(width=1280, height=720, fps=15)
    video_track = video_streamer.start()
    await ctx.room.local_participant.publish_track(video_track)
    
    # Local session memory to pass to LangGraph
    # (In production, you might save this in a database)
    current_state = AgentState(
        messages=[],
        demo_stage="start",
        current_url=START_URL,
        company_context=DEMO_COMPANY,
        current_screenshot=None,
        is_off_topic=False
    )

    # 4. Greet the user (Proactive)
    # Synthesize an initial audio greeting and send it to the room
    initial_greeting = "Hello! I'm Alex. I already have the platform open on my screen. Where would you like to start?"
    audio_stream = await tts.synthesize(initial_greeting)
    await ctx.room.local_participant.publish_data(audio_stream)

    # 5. Listening loop: Process everything the user says
    # Create a transcription stream from the user's audio track
    transcription_stream = stt.stream()
    
    # Asynchronous function to listen continuously
    async def listen_and_respond():
        async for event in transcription_stream:
            # Only react when the user finishes speaking a full sentence (is_final)
            if event.type == "final_transcript" and event.alternatives:
                user_text = event.alternatives[0].text
                logger.info(f"User says: {user_text}")
                
                # A. Take a screenshot with Playwright!
                photo_b64 = await take_screenshot()
                
                # B. Prepare the package for LangGraph
                current_state["messages"].append(HumanMessage(content=user_text))
                current_state["current_screenshot"] = photo_b64
                
                # C. Invoke the brain (This will move the mouse if necessary)
                # NOTE: Since LangGraph is synchronous by default, if you have async tools,
                # you need to use ainvoke (asynchronous invoke)
                new_state = await langgraph_agent.ainvoke(current_state)
                
                # Update our memory with what the agent returned
                current_state["messages"] = new_state["messages"]
                
                # D. Extract the spoken response from Claude
                response_text = new_state["messages"][-1].content
                logger.info(f"Agent responds: {response_text}")
                
                # E. Speak back
                audio_response = await tts.synthesize(response_text)
                await ctx.room.local_participant.publish_data(audio_response)

    # Start the listening task in the background
    asyncio.create_task(listen_and_respond())

if __name__ == "__main__":
    # Start the LiveKit Worker
    cli.main_worker(WorkerOptions(entrypoint_fnc=entrypoint))