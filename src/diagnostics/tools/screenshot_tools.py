import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

async def take_screenshot(url: str, width: int = 1280, height: int = 720, timeout: int = 30000) -> Dict[str, Any]:
    """
    Analyze a website using Playwright to detect visual issues.
    Returns analysis of potential visual issues without screenshots to avoid context overflow.
    """
    result: Dict[str, Any] = {"url": url, "success": False}
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': width, 'height': height},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Set timeout
            page.set_default_timeout(timeout)
            
            # Navigate to URL
            response = await page.goto(url, wait_until='networkidle')
            
            if response:
                result["status_code"] = response.status
                result["final_url"] = response.url
                
                # Wait a bit for any dynamic content to load
                await page.wait_for_timeout(2000)
                
                # Analyze page for potential issues (no screenshot to avoid context overflow)
                analysis = await analyze_page_visual_issues(page)
                result["visual_analysis"] = analysis
                
                result["success"] = True
                
            await browser.close()
            
    except Exception as e:
        result["error"] = str(e)
        result["success"] = False
    
    return result

async def analyze_page_visual_issues(page) -> Dict[str, Any]:
    """Analyze the page for potential visual issues"""
    analysis = {
        "has_content": False,
        "is_blank": False,
        "has_errors": False,
        "has_loading_indicators": False,
        "text_content_length": 0,
        "visible_elements": 0,
        "issues": []
    }
    
    try:
        # Check if page has meaningful content
        text_content = await page.evaluate("""
            () => {
                const body = document.body;
                if (!body) return { textLength: 0, visibleElements: 0 };
                
                // Get visible text content
                const text = body.innerText || body.textContent || '';
                const textLength = text.trim().length;
                
                // Count visible elements
                const visibleElements = document.querySelectorAll('*:not(script):not(style):not(meta):not(link)').length;
                
                return { textLength, visibleElements };
            }
        """)
        
        analysis["text_content_length"] = text_content.get("textLength", 0)
        analysis["visible_elements"] = text_content.get("visibleElements", 0)
        
        # Check for common issues
        issues = await page.evaluate("""
            () => {
                const issues = [];
                
                // Check if page is mostly blank
                const body = document.body;
                if (body) {
                    const text = body.innerText || body.textContent || '';
                    if (text.trim().length < 50) {
                        issues.push("Page appears to have very little text content");
                    }
                }
                
                // Check for error messages
                const errorSelectors = [
                    'div[class*="error"]',
                    'div[class*="Error"]',
                    'div[id*="error"]',
                    'div[id*="Error"]',
                    '.error',
                    '.Error',
                    '#error',
                    '#Error',
                    '[class*="alert"]',
                    '[class*="Alert"]',
                    '[class*="warning"]',
                    '[class*="Warning"]',
                    '[class*="danger"]',
                    '[class*="Danger"]'
                ];
                
                errorSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(element => {
                        // Check if element is visible
                        const style = window.getComputedStyle(element);
                        const isVisible = style.display !== 'none' && 
                                        style.visibility !== 'hidden' && 
                                        style.opacity !== '0' &&
                                        element.offsetWidth > 0 && 
                                        element.offsetHeight > 0;
                        
                        if (isVisible) {
                            // Get text content
                            const text = element.innerText || element.textContent || '';
                            const trimmedText = text.trim();
                            
                            // Only report if there's meaningful text content
                            if (trimmedText.length > 0 && trimmedText.length < 500) {
                                issues.push(`Found visible error element: "${trimmedText}" (selector: ${selector})`);
                            }
                        }
                    });
                });
                
                // Check for loading indicators
                const loadingSelectors = [
                    'div[class*="loading"]',
                    'div[class*="Loading"]',
                    'div[class*="spinner"]',
                    'div[class*="Spinner"]',
                    '.loading',
                    '.Loading',
                    '.spinner',
                    '.Spinner'
                ];
                
                loadingSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        issues.push(`Found potential loading indicators with selector: ${selector}`);
                    }
                });
                
                // Check for JavaScript errors in console
                const originalError = console.error;
                const errors = [];
                console.error = function(...args) {
                    errors.push(args.join(' '));
                    originalError.apply(console, args);
                };
                
                // Check for broken images
                const images = document.querySelectorAll('img');
                const brokenImages = Array.from(images).filter(img => !img.complete || img.naturalWidth === 0);
                if (brokenImages.length > 0) {
                    issues.push(`Found ${brokenImages.length} broken or failed to load images`);
                }
                
                return { issues, errors };
            }
        """)
        
        analysis["issues"] = issues.get("issues", [])
        analysis["javascript_errors"] = issues.get("errors", [])
        
        # Determine overall status
        analysis["has_content"] = analysis["text_content_length"] > 100
        analysis["is_blank"] = analysis["text_content_length"] < 50 and analysis["visible_elements"] < 10
        analysis["has_errors"] = len(analysis["issues"]) > 0 or len(analysis["javascript_errors"]) > 0
        analysis["has_loading_indicators"] = any("loading" in issue.lower() for issue in analysis["issues"])
        
    except Exception as e:
        analysis["issues"].append(f"Error during visual analysis: {str(e)}")
    
    return analysis

def take_screenshot_sync(url: str, width: int = 1280, height: int = 720, timeout: int = 30000) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async screenshot function.
    This is what the agent will call.
    """
    return asyncio.run(take_screenshot(url, width, height, timeout))
