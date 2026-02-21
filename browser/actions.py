import asyncio
from browser.controller import get_current_page

async def move_and_click_real(selector_or_text: str) -> str:
    """
    Finds an element (button, link, etc.), visibly moves the mouse to it, and clicks it.
    Uses multiple search strategies for robustness.
    """
    page = get_current_page()
    if not page:
        return "Error: The browser is not started."
    
    try:
        # Clean up characters that often break exact search
        clean_text = selector_or_text.replace('"', '').strip()
        
        # Strategy 1: Find by role (button/link) containing the text (most robust)
        element = page.get_by_role("button", name=clean_text, exact=False).first
        
        if await element.count() == 0:
            element = page.get_by_role("link", name=clean_text, exact=False).first
            
        # Strategy 2: If not a button or link, search for any text that partially matches
        if await element.count() == 0:
            element = page.get_by_text(clean_text, exact=False).first
            
        # Strategy 3: If all else fails, assume Gemini sent a raw CSS selector
        if await element.count() == 0:
            element = page.locator(selector_or_text).first
            
        if await element.count() == 0 or not await element.is_visible():
            return f"Element '{selector_or_text}' could not be found on the screen."
        
        # Get coordinates and move the mouse
        box = await element.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            
            await page.mouse.move(center_x, center_y, steps=10) 
            await asyncio.sleep(0.2) 
            
            await page.mouse.click(center_x, center_y)
            await asyncio.sleep(1) # Wait for the page to react to the click
            
            return f"Action completed: Clicked on '{selector_or_text}'."
            
        return "Element found, but unable to calculate its on-screen position."
        
    except Exception as e:
        return f"Internal error trying to click: {str(e)}"

async def scroll_page_real(direction: str) -> str:
    """Performs a physical scroll on the page."""
    page = get_current_page()
    if not page:
         return "Error: The browser is not started."
         
    amount = 600 if direction.lower() == "down" else -600
    await page.mouse.wheel(0, amount)
    await asyncio.sleep(1)
    
    return f"Action completed: Scrolled {direction}."

async def fill_field_real(selector_or_text: str, text_to_type: str) -> str:
    """
    Finds a text field, moves the mouse, clicks to focus,
    types like a human, and presses Enter.
    """
    page = get_current_page()
    if not page:
        return "Error: The browser is not running."
    
    try:
        clean_text = selector_or_text.replace("?", "").replace('"', '').strip()
        
        # Strategy 1: Find by placeholder or label
        element = page.get_by_placeholder(clean_text, exact=False).first
        
        if await element.count() == 0:
            element = page.get_by_label(clean_text, exact=False).first
            
        # Strategy 2: As a last resort, search for any generic input
        if await element.count() == 0:
            element = page.locator("input").first
            
        if await element.count() == 0 or not await element.is_visible():
            return f"Error: Could not find text field '{selector_or_text}'."
        
        # Move mouse and focus
        box = await element.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            
            await page.mouse.move(center_x, center_y, steps=80)
            await asyncio.sleep(0.2) 
            await page.mouse.click(center_x, center_y)
            await asyncio.sleep(0.2)
            
            # 1. Limpiamos el campo de forma segura
            await element.clear()
            
            # 2. Escribimos secuencialmente como un humano (aumenta el delay para que teclee más lento)
            await element.press_sequentially(text_to_type, delay=150)
            
            # 3. Pulsamos Enter
            await page.keyboard.press("Enter")
            await asyncio.sleep(0.5)
            
            return f"Typed '{text_to_type}' successfully in '{selector_or_text}'."
            
        return "Field found, but could not click on it."
        
    except Exception as e:
        return f"Internal error trying to type: {str(e)}"