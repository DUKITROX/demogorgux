from playwright.async_api import async_playwright, Page, BrowserContext
import base64

# Global variables to keep the browser session alive on the server
# and accessible from anywhere in our code.
_playwright_instance = None
_browser = None
_context: BrowserContext = None
_page: Page = None

async def start_browser(start_url: str) -> Page:
    """Starts the headless browser and prepares the demo environment."""
    global _playwright_instance, _browser, _context, _page

    _playwright_instance = await async_playwright().start()

    # Start in headless mode (no OS graphical interface)
    # but force a standard window size (720p), perfect for streaming.
    _browser = await _playwright_instance.chromium.launch(headless=False)

    _context = await _browser.new_context(
        viewport={"width": 1280, "height": 720},
        device_scale_factor=1
    )

    _page = await _context.new_page()
    await _page.goto(start_url)

    # Inject our red cursor so it appears in the video
    await _inject_fake_cursor(_page)

    return _page

async def _inject_fake_cursor(page: Page):
    """
    Injects a realistic HTML div that acts as the agent's visible cursor.
    It automatically switches between an arrow and a pointer hand when hovering over clickable elements.
    """
    js_code = """
    () => {
        // SVG Data URIs for standard OS cursors (Black with white border for visibility)
        const cursorArrow = "url(\\"data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M5.5 3.21V20.8L9.6 16.7L12.5 22.8L15.3 21.4L12.4 15.3H18.6L5.5 3.21Z' fill='black' stroke='white' stroke-width='1.5' stroke-linejoin='round'/%3E%3C/svg%3E\\")";
        
        const cursorHand = "url(\\"data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M10.5 10.5V3.5C10.5 2.4 11.5 2.4 11.5 3.5V10.5M11.5 10.5V5.5C11.5 4.4 12.5 4.4 12.5 5.5V10.5M12.5 10.5V6.5C12.5 5.4 13.5 5.4 13.5 6.5V10.5M13.5 10.5V8.5C13.5 7.4 14.5 7.4 14.5 8.5V14.5C14.5 18.5 11.5 21.5 8.5 21.5H7.5C4.5 21.5 2.5 18.5 2.5 14.5V11.5C2.5 10.4 3.5 10.4 3.5 11.5V13.5M10.5 10.5L6.5 6.5' fill='black' stroke='white' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E\\")";

        const cursor = document.createElement('div');
        cursor.id = 'ai-cursor';
        cursor.style.width = '24px';
        cursor.style.height = '24px';
        cursor.style.position = 'absolute';
        cursor.style.zIndex = '999999'; // On top of everything
        cursor.style.pointerEvents = 'none'; // Doesn't block real clicks
        cursor.style.backgroundImage = cursorArrow;
        cursor.style.backgroundSize = 'contain';
        cursor.style.backgroundRepeat = 'no-repeat';
        // Fast transition for position, smooth transition for the image swap
        cursor.style.transition = 'top 0.05s linear, left 0.05s linear, background-image 0.1s ease-in-out'; 
        document.body.appendChild(cursor);

        // When Playwright moves the invisible mouse, our realistic cursor will follow it
        document.addEventListener('mousemove', (e) => {
            // Position the top-left corner of the div exactly at the mouse coordinates
            cursor.style.left = e.pageX + 'px';
            cursor.style.top = e.pageY + 'px';

            // Check what element is currently under the cursor (using clientX/Y for viewport)
            const elementUnderCursor = document.elementFromPoint(e.clientX, e.clientY);
            let isClickable = false;

            if (elementUnderCursor) {
                const style = window.getComputedStyle(elementUnderCursor);
                // Standard heuristic to detect clickable elements
                if (
                    style.cursor === 'pointer' || 
                    elementUnderCursor.tagName.toLowerCase() === 'a' || 
                    elementUnderCursor.tagName.toLowerCase() === 'button' ||
                    elementUnderCursor.closest('a, button') !== null // Handles text inside buttons
                ) {
                    isClickable = true;
                }
            }

            // Swap the SVG based on context
            cursor.style.backgroundImage = isClickable ? cursorHand : cursorArrow;
        });
    }
    """
    await page.evaluate(js_code)

def get_current_page() -> Page:
    """Returns the current tab so the tools can use it."""
    return _page

async def take_screenshot() -> str:
    """Takes a current screenshot of the web page and returns it in Base64 for Claude."""
    if not _page:
        return None
    # Use JPEG at quality 70 so the photo isn't too large and the Claude API is fast to respond
    screenshot_bytes = await _page.screenshot(type="jpeg", quality=70)
    return base64.b64encode(screenshot_bytes).decode('utf-8')