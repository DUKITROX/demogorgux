import asyncio
import io
import logging
from PIL import Image
from livekit import rtc
from browser.controller import get_current_page

logger = logging.getLogger("video-track")

class BrowserVideoTrack:
    def __init__(self, width=1280, height=720, fps=15):
        """Initializes the video source with HD resolution and 15 frames per second."""
        self.width = width
        self.height = height
        self.fps = fps
        
        # 1. Create the LiveKit video source
        self.source = rtc.VideoSource(width, height)
        # 2. Create the actual track we'll publish in the room
        self.track = rtc.LocalVideoTrack.create_video_track("screen-share", self.source)
        
        self._task = None
        self._running = False

    def start(self):
        """Starts the screen capture loop."""
        self._running = True
        self._task = asyncio.create_task(self._capture_loop())
        logger.info(f"Screen recording started at {self.fps} FPS")
        return self.track

    def stop(self):
        """Stops the recording."""
        self._running = False
        if self._task:
            self._task.cancel()

    async def _capture_loop(self):
        """The loop that runs X times per second."""
        sleep_duration = 1.0 / self.fps
        
        while self._running:
            start_time = asyncio.get_event_loop().time()
            
            try:
                page = get_current_page()
                if page:
                    # A. Take a super fast screenshot with Playwright
                    screenshot_bytes = await page.screenshot(type="jpeg", quality=60)
                    
                    # B. Open it with Pillow and ensure the size is exact and color is RGBA
                    img = Image.open(io.BytesIO(screenshot_bytes)).convert("RGBA")
                    if img.size != (self.width, self.height):
                        img = img.resize((self.width, self.height))
                        
                    # C. Create a blank frame for LiveKit
                    argb_frame = rtc.ArgbFrame.create(
                        rtc.VideoFormatType.FORMAT_RGBA, 
                        self.width, 
                        self.height
                    )
                    
                    # D. Dump our image pixels to the frame
                    argb_frame.data[:] = img.tobytes()
                    
                    # E. Convert to I420 (the standard WebRTC format) and send it
                    video_frame = rtc.VideoFrame(
                        0, 
                        rtc.VideoRotation.VIDEO_ROTATION_0, 
                        argb_frame.to_i420()
                    )
                    self.source.capture_frame(video_frame)
                    
            except Exception as e:
                # If the page hasn't loaded yet, ignore the error and keep going
                pass
                
            # F. Sleep the exact time needed to maintain stable FPS
            elapsed = asyncio.get_event_loop().time() - start_time
            await asyncio.sleep(max(0, sleep_duration - elapsed))