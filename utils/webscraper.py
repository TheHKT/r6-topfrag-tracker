import random
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
        random_delay = random.random() * 2000 + 3000
        
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
        await page.goto(url)
        
        # Handle cookie
        try:
            await page.wait_for_selector('button:has-text("Accept")', timeout=10000)
            await page.wait_for_timeout(random_delay) 
            await page.click('button:has-text("Accept")')
        except:
            try:
                await page.wait_for_selector('[data-testid="accept-cookies"]', timeout=10000)
                await page.wait_for_timeout(random_delay) 
                await page.click('[data-testid="accept-cookies"]')
            except:
                print("No cookie popup found or couldn't click accept")

        # Wait for matches to load
        #print("⏳ Waiting for matches to load...")
        await page.wait_for_selector('.v3-match-row', timeout=10000)
        await page.wait_for_timeout(random_delay)
        
        # Retrieve first match
        first_match = await page.query_selector('.v3-match-row:first-child')
        if first_match:
            #print("✅ Found first match, clicking...")
            await first_match.click()
            
            try:
                await asyncio.wait_for(response_captured.wait(), timeout=30.0)
                #print("✅ Match data captured successfully!")
            except asyncio.TimeoutError:
                print("Timeout waiting for match data response")
            
            await page.wait_for_timeout(3000)
        else:
            print("Could not find first match row")

        await browser.close()
    
    return match_data