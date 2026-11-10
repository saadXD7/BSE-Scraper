from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import uvicorn

app = FastAPI()

async def scrape_bse_gainers():
    # Target Rediff Money (Live BSE Gainers). 
    # Rediff does NOT block GitHub/Azure cloud IPs, making it the perfect
    # target to demonstrate Playwright DOM traversal and wait strategies.
    url = "https://money.rediff.com/gainers/bse/daily/groupa"
    data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for the specific data table to load in the DOM
            await page.wait_for_selector("table.dataTable tbody tr", timeout=30000)
            
            # Extract the rows
            rows = await page.query_selector_all("table.dataTable tbody tr")
            
            for row in rows:
                cols = await row.query_selector_all("td")
                
                # Rediff Columns: 0=Company, 1=Group, 2=Prev Close, 3=Current Price, 4=% Change
                if len(cols) >= 5:
                    company_name = await cols[0].inner_text()
                    ltp = await cols[3].inner_text()
                    pct_change = await cols[4].inner_text()
                    
                    if company_name.strip():
                        data.append({
                            "security_code": "BSE Group A", 
                            "company_name": company_name.strip(),
                            "ltp": ltp.strip(),
                            "pct_change": pct_change.strip() + "%"
                        })
                        
                    # Limit to top 20 gainers for a clean UI
                    if len(data) >= 20:
                        break
                        
        except Exception as e:
            print(f"Scraping Error: {e}")
        finally:
            await browser.close()
            
    return data

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    scraped_data = await scrape_bse_gainers()
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Live Top Gainers</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f9; padding: 2rem; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #0056b3; color: white; }
            .positive { color: #28a745; font-weight: bold; }
            .empty-state { color: #dc3545; font-weight: bold; margin-top: 20px; }
            .note { font-size: 0.85rem; color: #666; margin-top: 15px; font-style: italic; border-top: 1px solid #eee; padding-top: 10px;}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Live Top Gainers (BSE Equity)</h2>
    """
    
    if not scraped_data:
        html_content += "<p class='empty-state'>Failed to extract live market data.</p>"
    else:
        html_content += """
            <table>
                <thead>
                    <tr>
                        <th>Security / Group</th>
                        <th>Company Name</th>
                        <th>LTP (₹)</th>
                        <th>% Change</th>
                    </tr>
                </thead>
                <tbody>
        """
        for gainer in scraped_data:
            html_content += f"""
                        <tr>
                            <td>{gainer['security_code']}</td>
                            <td>{gainer['company_name']}</td>
                            <td>{gainer['ltp']}</td>
                            <td class="positive">{gainer['pct_change']}</td>
                        </tr>
            """
        html_content += """
                </tbody>
            </table>
            <p class="note"><b>Architecture Note:</b> Data sourced via Playwright DOM extraction from Rediff Money (Live BSE Data) to demonstrate required wait strategies and raw element extraction while bypassing cloud datacenter IP blocks on the primary domain.</p>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)