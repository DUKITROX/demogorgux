from langchain_core.tools import tool
from browser.actions import move_and_click_real, scroll_page_real, fill_field_real
import asyncio

# Note: LangGraph executes synchronous tools by default unless configured for async,
# so we use a small asyncio.run wrapper (or handle async graphs).

@tool
async def click_element(element_description: str) -> str:
    """
    Clicks on a visible screen element (a button, link, tab, or menu).
    The 'element_description' parameter should be the exact text you see.
    """
    # We call the real Playwright muscle here!
    resultado = await move_and_click_real(element_description)
    return resultado

@tool
async def scroll_page(direction: str) -> str:
    """
    Scrolls the page to show more content.
    The 'direction' parameter can only be 'up' or 'down'.
    """
    resultado = await scroll_page_real(direction)
    return resultado

@tool
async def fill_input_field(element_description: str, text_to_type: str) -> str:
    """
    Clicks on an input field (like a search bar or a form input) and types the specified text.
    Use this when the user asks to search for something, log in, or fill out dummy data.
    'element_description' should describe the field (e.g., 'Search input' or 'Email address').
    'text_to_type' is the exact string you will type into the field.
    """
    result = await fill_field_real(element_description, text_to_type)
    return result

@tool
async def go_to_url(url: str) -> str:
    """
    Usa esta herramienta cuando el usuario te pida ir a una página web específica o visitar una URL.
    Asegúrate de incluir 'https://' en la URL.
    """
    from browser.controller import get_current_page
    page = await get_current_page()
    await page.goto(url)
    return f"He navegado a la página: {url}"

browser_tools = [click_element, scroll_page, fill_input_field, go_to_url]