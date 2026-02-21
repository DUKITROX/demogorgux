import asyncio
from browser.controller import get_current_page

async def move_and_click_real(selector_or_text: str) -> str:
    """
    Finds the element, visually moves the red mouse to it, and clicks.
    """
    page = get_current_page()
    if not page:
        return "Error: The browser is not started."
    
    try:
        # 1. Try to locate by visible text that Claude saw in the screenshot
        element = page.locator(f"text='{selector_or_text}'").first
        
        # If not found by text, assume Claude provided a CSS selector
        if not await element.is_visible():
            element = page.locator(selector_or_text).first
            
        if not await element.is_visible():
            return f"Could not locate the element '{selector_or_text}' on the current screen."
        
        # 2. Obtain the element's geometric coordinates
        box = await element.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            
            # 3. Move the mouse with 'steps' so the user sees the path in the video
            await page.mouse.move(center_x, center_y, steps=20) 
            
            # Dramatic pause for a third of a second before clicking (adds realism)
            await asyncio.sleep(0.3) 
            
            # 4. Perform the physical click
            await page.mouse.click(center_x, center_y)
            
            # Wait a bit so the website can load the new view if there was navigation
            await asyncio.sleep(1) 
            
            return f"Action completed: Clicked on '{selector_or_text}'."
            
        return "Element found, but could not calculate its position on the screen."
        
    except Exception as e:
        return f"Internal error trying to click: {str(e)}"

async def scroll_page_real(direction: str) -> str:
    """Performs a physical scroll on the web page."""
    page = get_current_page()
    if not page:
         return "Error: The browser is not started."
         
    # Move the mouse wheel by 600 pixels
    amount = 600 if direction.lower() == "down" else -600
    await page.mouse.wheel(0, amount)
    
    # Pause so the user can absorb the new content
    await asyncio.sleep(1)
    
    return f"Action completed: Scrolled {direction}."

async def fill_field_real(selector_or_text: str, text_to_type: str) -> str:
    """
    Finds an input field, moves the visible cursor to it, clicks to focus, 
    and types the text with a human-like delay.
    """
    page = get_current_page()
    if not page:
        return "Error: Browser is not running."
    
    try:
        # 1. Locate the input field (by placeholder, nearby text, or CSS selector)
        element = page.locator(f"text='{selector_or_text}'").first
        
        if not await element.is_visible():
            element = page.locator(selector_or_text).first
            
        if not await element.is_visible():
            return f"Error: Could not find the input field '{selector_or_text}' on the screen."
        
        # 2. Move the red AI cursor to the input field
        box = await element.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            
            await page.mouse.move(center_x, center_y, steps=20)
            await asyncio.sleep(0.3) # Brief pause before clicking
            
            # 3. Click to focus the input
            await page.mouse.click(center_x, center_y)
            await asyncio.sleep(0.2)
            
            # 4. Type the text like a human (100ms delay between keystrokes)
            await page.keyboard.type(text_to_type, delay=100)
            
            # Wait a moment for UI reactions (like dropdowns appearing after typing)
            await asyncio.sleep(0.5)
            
            return f"Successfully typed '{text_to_type}' into '{selector_or_text}'."
            
        return "Element found, but could not calculate its position on screen."
        
    except Exception as e:
        return f"Internal error while trying to type: {str(e)}"