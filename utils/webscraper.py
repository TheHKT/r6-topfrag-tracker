import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_match_data(username: str, headless: bool = False, save_to_file: bool = False) -> dict:
    """
    Scrapes R6 Siege match data for a given username.
    
    Args:
        username: The R6 Siege username to scrape
        headless: Whether to run browser in headless mode (default: False)
        save_to_file: Whether to save the JSON response to a file (default: False)
    
    Returns:
        dict: The match data JSON, or None if scraping failed
    """
    url = f"https://r6.tracker.network/r6siege/profile/ubi/{username}/overview"
    match_data = None
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        
        response_captured = asyncio.Event()
        
        async def handle_response(response):
            nonlocal match_data
            if 'api.tracker.gg/api/v2/r6siege/standard/matches' in response.url and username not in response.url:
                try:
                    json_data = await response.json()

                    if save_to_file:
                        with open(f'./store/{username}.json', 'w') as f:
                            json.dump(json_data, f, indent=2)
                    
                    match_data = json_data
                    response_captured.set()
                    
                except Exception as e:
                    print(f"Error processing match data response: {e}")

        page.on('response', handle_response)   

        # Open page
        await page.goto(url, wait_until='domcontentloaded')
        
        cookie_handled = False        
        cookie_selectors = [
            'button:has-text("Accept")',
            '[data-testid="accept-cookies"]',
            'button[aria-label*="Accept"]',
            'button:text-is("Accept All")',
            '#ncmp__tool button:has-text("Accept")'
        ]
        
        for selector in cookie_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.wait_for_timeout(1000)
                await page.click(selector, timeout=5000, force=True)
                cookie_handled = True
                break
            except Exception as e:
                continue
        
        if not cookie_handled:
            try:
                await page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const acceptBtn = buttons.find(b => 
                            b.textContent.toLowerCase().includes('accept')
                        );
                        if (acceptBtn) {
                            acceptBtn.click();
                            return true;
                        }
                        return false;
                    }
                """)
                cookie_handled = True
            except:
                pass
        if not cookie_handled:
            print("No cookie popup handled (might not be present)")
        await page.wait_for_timeout(2000)
        
        try:
            await page.wait_for_selector('.v3-match-row', timeout=15000)
            await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Error waiting for matches: {e}")
            await browser.close()
            return None
        
        # Retrieve first match
        first_match = await page.query_selector('.v3-match-row:first-child')
        if first_match:
            try:
                # Use force=True to bypass any overlays
                await first_match.click(force=True, timeout=10000)
            except Exception as e:
                print(f"Click failed, trying JavaScript click: {e}")
                await page.evaluate("document.querySelector('.v3-match-row:first-child').click()")
            
            try:
                await asyncio.wait_for(response_captured.wait(), timeout=30.0)
            except asyncio.TimeoutError:
                print("Timeout waiting for match data response")
            
            await page.wait_for_timeout(2000)
        else:
            print("Could not find first match row")

        await browser.close()
    
    return match_data