import json
import logging
from typing import Dict, Any, List, Generator
from openai import OpenAI
from .config import settings
from .schemas import DiagnosticReport, Issue
from .tools import dns_lookup, tls_probe, http_check, hosting_provider_detect, take_screenshot_sync

logger = logging.getLogger(__name__)

# Tool definitions for the Responses API - Focus on critical issues only
TOOLS = [
    {
        "type": "function",
        "name": "dns_lookup",
        "description": "Lookup DNS records for a domain to check if it resolves",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "record_types": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["A","AAAA","CNAME","MX","NS","TXT"]},
                    "default": ["A","AAAA","CNAME","MX","NS","TXT"]
                }
            },
            "required": ["domain"]
        }
    },
    {
        "type": "function",
        "name": "http_check",
        "description": "Fetch a URL and return status, final URL, headers, and sample of body to check if the site is accessible",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "method": {"type": "string", "enum": ["GET","HEAD","POST"], "default": "GET"},
                "follow_redirects": {"type": "boolean", "default": True},
                "timeout_sec": {"type": "integer", "default": 10}
            },
            "required": ["url"]
        }
    },
    {
        "type": "function",
        "name": "tls_probe",
        "description": "Probe a TLS endpoint to get cert details and expiry to check if HTTPS is working",
        "parameters": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer", "default": 443},
                "sni": {"type": "boolean", "default": True}
            },
            "required": ["host"]
        }
    },
    {
        "type": "function",
        "name": "take_screenshot_sync",
        "description": "Analyze a website for visual issues, rendering problems, JavaScript errors, or broken content using browser automation.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to analyze"},
                "width": {"type": "integer", "default": 1280, "description": "Viewport width"},
                "height": {"type": "integer", "default": 720, "description": "Viewport height"},
                "timeout": {"type": "integer", "default": 30000, "description": "Timeout in milliseconds"}
            },
            "required": ["url"]
        }
    },
    {
        "type": "function",
        "name": "hosting_provider_detect",
        "description": "Detect hosting provider based on DNS records and TLS certificate information, providing specific instructions and dashboard links",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "dns_records": {
                    "type": "object",
                    "description": "DNS records from dns_lookup function (optional)"
                },
                "tls_info": {
                    "type": "object",
                    "description": "TLS certificate information from tls_probe function (optional)"
                }
            },
            "required": ["domain"]
        }
    }
]

FUNCTIONS = {
    "dns_lookup": dns_lookup,
    "http_check": http_check,
    "tls_probe": tls_probe,
    "hosting_provider_detect": hosting_provider_detect,
    "take_screenshot_sync": take_screenshot_sync,
}

def run_agent(target: str) -> DiagnosticReport:
    logger.info(f"Starting OpenAI agent diagnosis for target: {target}")
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Heuristic parsing
    is_url = target.startswith("http://") or target.startswith("https://")
    domain = target.split("://", 1)[1].split("/")[0] if is_url else target
    
    logger.info(f"Parsed target - is_url: {is_url}, domain: {domain}")

    # Initialize messages for Chat Completions API
    messages = [{
        "role": "user", 
        "content": f"""You are a helpful website diagnostic assistant. Diagnose the target "{target}" and provide clear, actionable guidance.

IMPORTANT INSTRUCTIONS:
1. Focus ONLY on issues that would make the site "broken" for users (prevent access or core functionality)
2. ALWAYS run hosting_provider_detect when you find issues - this provides specific instructions for the user's hosting provider and certificate management method
3. Provide clear, step-by-step instructions that non-technical users can follow
4. Include specific dashboard links and support contacts when available
5. When certificate issues are found, the hosting provider detection will automatically determine if it's managed by AWS Certificate Manager or Certbot/Let's Encrypt

Return your findings in clear, well-formatted markdown. Structure your response with:

## Summary
A clear explanation of the main issue preventing site access (if any issues found) or confirmation that the site is working properly.

## Issues Found
List any critical issues that would prevent users from accessing the site. For each issue:
- **Issue Type**: What kind of problem it is
- **Severity**: How critical the issue is
- **Explanation**: What this means in simple terms
- **Detailed Steps to Fix**: Step-by-step instructions with specific actions

## Recommendations
Provide comprehensive, detailed instructions for fixing any issues found. Include:
- Specific hosting provider dashboard links
- Exact menu paths and button names
- Support contact information
- Alternative solutions if available
- Troubleshooting steps

If no issues are found, provide basic maintenance tips and best practices.

CRITICAL: Only report issues that would prevent users from accessing or using the site. Ignore:
- Security headers (these don't break the site)
- Email authentication (SPF/DKIM/DMARC - these don't break the site)
- Minor configuration issues

Focus on:
- DNS resolution failures (domain doesn't resolve)
- HTTP server errors (4xx, 5xx status codes)
- TLS certificate problems (expired, invalid, or missing certificates)
- Network connectivity issues
- Content loading problems

DIAGNOSTIC STEPS:
1) Run dns_lookup on the domain "{domain}" to check if it resolves
2) Run http_check on https://{domain} (or the explicit URL if provided) to test website accessibility
3) Run tls_probe on the domain "{domain}" to check SSL certificate status
4) Run take_screenshot_sync on the domain "{domain}" to capture and analyze the rendered page and check for visual issues, rendering problems, JavaScript errors, or broken content.
5) If ANY issues are found, run hosting_provider_detect with the domain "{domain}" to get provider-specific instructions

IMPORTANT: Always use the full domain "{domain}" (including any subdomains) when calling tools. Do not strip subdomains or use the root domain.

HELPFUL GUIDANCE REQUIREMENTS:
- For each issue, provide DETAILED, step-by-step instructions that a non-technical user can follow
- Include specific hosting provider dashboard links when available
- Mention support contact information when relevant
- Explain what each issue means in simple terms
- Provide alternative solutions when possible
- If the site is working fine, clearly state that and provide basic maintenance tips
- ALWAYS provide comprehensive, detailed instructions - don't be brief or vague
- Include specific menu paths, button names, and exact steps to follow
- Mention any important settings or options the user should look for
- Provide troubleshooting steps if the main solution doesn't work

Example detailed response: "Your website is down because the domain has expired. Here's exactly how to fix it: 1) Open your web browser and go to [dashboard link], 2) Click 'Sign In' in the top right corner, 3) Enter your email and password, 4) Once logged in, click 'Domains' in the main menu, 5) Find your domain name in the list and click on it, 6) Look for the 'Renew Domain' button (usually green) and click it, 7) Select the renewal period (1-10 years) and click 'Continue', 8) Review the pricing and click 'Complete Purchase', 9) Enter your payment information and click 'Submit Order'. If you can't find the renew button or need help, call GoDaddy support at [support link] or use their live chat feature."

Synthesize your findings into clear, actionable issues that focus on what would make the site "broken" for users."""
    }]
    
    logger.info(f"Creating OpenAI chat completion with model: {settings.OPENAI_MODEL}")
    
    # Function calling loop
    iteration = 0
    while True:
        iteration += 1
        logger.info(f"Function calling iteration {iteration}")
        
        # Create chat completion
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        logger.info("Received response from OpenAI")
        
        # Get the assistant's message
        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump())
        
        # Check if there are function calls
        if not assistant_message.tool_calls:
            logger.info("No more function calls - breaking loop")
            break
        
        logger.info(f"Found {len(assistant_message.tool_calls)} function calls to execute")
        
        # Execute function calls
        logger.info("Executing function calls...")
        for tool_call in assistant_message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")
            logger.info(f"Handling function call: {name} with args: {args}")
            
            fn = FUNCTIONS.get(name)
            if not fn:
                logger.error(f"Unknown function: {name}")
                result = {"error": f"unknown function {name}"}
            else:
                try:
                    # Handle default parameters for specific functions
                    if name == "dns_lookup" and "record_types" not in args:
                        args["record_types"] = ["A", "AAAA", "CNAME", "MX", "NS", "TXT"]
                        result = fn(**args)
                    elif name == "hosting_provider_detect":
                        # Automatically get DNS records if not provided
                        if "dns_records" not in args:
                            from .tools.dns_tools import dns_lookup
                            dns_result = dns_lookup(domain=args.get("domain"), record_types=["A", "AAAA", "CNAME", "MX", "NS", "TXT"])
                            args["dns_records"] = dns_result
                        
                        # Automatically get TLS info if not provided
                        if "tls_info" not in args:
                            from .tools.tls_tools import tls_probe
                            tls_result = tls_probe(host=args.get("domain"))
                            args["tls_info"] = tls_result
                        
                        result = fn(**args)
                    else:
                        result = fn(**args)
                    logger.info(f"Function {name} executed successfully")
                except Exception as e:
                    logger.error(f"Error executing function {name}: {str(e)}", exc_info=True)
                    result = {"error": str(e)}
            
            # Add function result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    
    # Get the final response
    final_message = messages[-1]["content"]
    logger.info("Extracting final response text from OpenAI")
    
    # Parse markdown response into structured format
    import re
    
    # Extract sections from markdown
    summary_match = re.search(r'## Summary\s*\n(.*?)(?=\n##|\Z)', final_message, re.DOTALL)
    issues_match = re.search(r'## Issues Found\s*\n(.*?)(?=\n##|\Z)', final_message, re.DOTALL)
    recommendations_match = re.search(r'## Recommendations\s*\n(.*?)(?=\n##|\Z)', final_message, re.DOTALL)
    
    # Extract content, stripping markdown formatting
    summary = summary_match.group(1).strip() if summary_match else "No summary provided"
    issues_text = issues_match.group(1).strip() if issues_match else "No issues found"
    recommendations = recommendations_match.group(1).strip() if recommendations_match else "No recommendations provided"
    
    # Collect all tool results from the conversation
    tool_results = {}
    for msg in messages:
        if msg.get("role") == "tool":
            try:
                content = json.loads(msg.get("content", "{}"))
                tool_call_id = msg.get("tool_call_id", "unknown")
                tool_results[tool_call_id] = content
            except:
                pass
    
    # Create a simple DiagnosticReport with the parsed markdown
    result = DiagnosticReport(
        summary=summary,
        issues=[],  # We'll handle issues differently now
        artifacts={
            "screenshots": [],
            "raw_samples": {
                "raw_model_text": final_message,
                "parsed_summary": summary,
                "parsed_issues": issues_text,
                "parsed_recommendations": recommendations,
                "tool_results": tool_results
            }
        }
    )
    
    logger.info("Successfully created DiagnosticReport from markdown response")
    return result

def run_agent_streaming(target: str) -> Generator[Dict[str, Any], None, None]:
    """
    Run the AI agent with streaming updates using OpenAI Responses API.
    Yields real-time updates as the agent thinks and uses tools.
    """
    logger.info(f"Starting streaming agent diagnosis for target: {target}")
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    yield {
        "type": "status",
        "message": "Initializing AI agent...",
        "step": "initialization"
    }
    
    # Prepare the tools for the Responses API
    tools = [
        {
            "type": "function",
            "name": "dns_lookup",
            "description": "Lookup DNS records for a domain to check if it resolves",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "record_types": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["A","AAAA","CNAME","MX","NS","TXT"]},
                        "default": ["A","AAAA","CNAME","MX","NS","TXT"]
                    }
                },
                "required": ["domain"]
            }
        },
        {
            "type": "function",
            "name": "http_check",
            "description": "Fetch a URL and return status, final URL, headers, and sample of body to check if the site is accessible",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "method": {"type": "string", "enum": ["GET","HEAD","POST"], "default": "GET"},
                    "follow_redirects": {"type": "boolean", "default": True},
                    "timeout_sec": {"type": "integer", "default": 10}
                },
                "required": ["url"]
            }
        },
        {
            "type": "function",
            "name": "tls_probe",
            "description": "Probe a TLS endpoint to get cert details and expiry to check if HTTPS is working",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer", "default": 443},
                    "sni": {"type": "boolean", "default": True}
                },
                "required": ["host"]
            }
        },
        {
            "type": "function",
            "name": "take_screenshot_sync",
            "description": "Analyze a website for visual issues, rendering problems, JavaScript errors, or broken content using browser automation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to analyze"},
                    "width": {"type": "integer", "default": 1280, "description": "Viewport width"},
                    "height": {"type": "integer", "default": 720, "description": "Viewport height"},
                    "timeout": {"type": "integer", "default": 30000, "description": "Timeout in milliseconds"}
                },
                "required": ["url"]
            }
        },
        {
            "type": "function",
            "name": "hosting_provider_detect",
            "description": "Detect hosting provider based on DNS records and TLS certificate information, providing specific instructions and dashboard links",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "dns_records": {
                        "type": "object",
                        "description": "DNS records from dns_lookup function (optional)"
                    },
                    "tls_info": {
                        "type": "object",
                        "description": "TLS certificate information from tls_probe function (optional)"
                    }
                },
                "required": ["domain"]
            }
        }
    ]
    
    # Initial prompt
    initial_message = f"""Please diagnose the website at {target}. 

Use the available tools to check:
1. DNS resolution and configuration
2. TLS/SSL certificate status and security
3. HTTP accessibility and response codes
4. Visual rendering and JavaScript functionality
5. Hosting provider detection for specific guidance

IMPORTANT: Focus ONLY on critical issues that would make the site appear "broken" to users. Ignore minor issues, security headers, or optimization suggestions.

A site is "broken" if:
- Users cannot access it at all (DNS issues, server errors)
- Users see error pages or blank screens
- Users get security warnings that prevent access
- Core functionality doesn't work due to technical problems
- Users see hosting suspension messages (like "Error. Page cannot be displayed. Please contact your service provider for more details.")

IMPORTANT: When you see generic error messages from hosting providers, the most common cause is an expired hosting account or unpaid bill. Always check for this first.

Provide clear, simple instructions. 

IMPORTANT: You must use valid markdown! 

When you detect hosting suspension errors, always include:
1. Check if hosting account is active/paid
2. Log into hosting provider dashboard
3. Look for billing/payment status
4. Contact hosting provider support if needed

Keep it simple and actionable, provide instructions tailored specifically for their hosting provider. If the site is working fine, just say so briefly.

Use this exact template structure:

## Summary
[One sentence: Is the site working or broken?]

## Critical Issues
[If any issues found, list them here. If no issues, write "No critical issues found."]

## How to Fix
[Step-by-step instructions for fixing any issues. If no issues, write "No action needed - your site is working correctly."]

## Hosting Provider Help
[Specific guidance for their hosting provider, or "No hosting provider issues detected."]

IMPORTANT: Follow this template exactly and use proper markdown formatting with blank lines between sections."""
    
    yield {
        "type": "status", 
        "message": "Analyzing website...",
        "step": "initial_analysis"
    }
    
    try:
        # Create the streaming response
        stream = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": initial_message}],
            tools=tools,
            stream=True,
        )
        
        # Process the streaming response
        current_function_call = None
        function_arguments = ""
        tool_results = []
        response_output = []
        
        for event in stream:
            event_type = event.type
            logger.debug(f"Received event: {event_type}")
            
            if event_type == "response.output_item.added":
                # Add this item to our response output
                response_output.append(event.item)
                
                if event.item.type == "function_call":
                    current_function_call = {
                        "id": event.item.id,
                        "call_id": event.item.call_id,
                        "name": event.item.name,
                        "arguments": ""
                    }
                    # Map tool names to friendly descriptions
                    friendly_names = {
                        "dns_lookup": "Checking your site's DNS settings",
                        "http_check": "Checking screenshot of your website",
                        "tls_probe": "Checking SSL certificate status",
                        "take_screenshot_sync": "Analyzing website appearance",
                        "hosting_provider_detect": "Identifying your hosting provider"
                    }
                    
                    friendly_name = friendly_names.get(event.item.name, f"Running {event.item.name}...")
                    
                    yield {
                        "type": "tool_call",
                        "tool": event.item.name,
                        "arguments": {},
                        "message": friendly_name
                    }
            
            elif event_type == "response.function_call_arguments.delta":
                if current_function_call and event.item_id == current_function_call["id"]:
                    function_arguments += event.delta
            
            elif event_type == "response.function_call_arguments.done":
                if current_function_call and event.item_id == current_function_call["id"]:
                    try:
                        function_args = json.loads(event.arguments)
                        function_name = current_function_call["name"]
                        
                        # Execute the tool
                        logger.info(f"Handling function call: {function_name} with args: {function_args}")
                        try:
                            if function_name == "dns_lookup":
                                if "record_types" not in function_args:
                                    function_args["record_types"] = ["A", "AAAA", "CNAME", "MX", "NS", "TXT"]
                                result = dns_lookup(**function_args)
                            elif function_name == "hosting_provider_detect":
                                # Automatically get DNS records if not provided
                                if "dns_records" not in function_args:
                                    dns_result = dns_lookup(domain=function_args.get("domain"), record_types=["A", "AAAA", "CNAME", "MX", "NS", "TXT"])
                                    function_args["dns_records"] = dns_result
                                
                                # Automatically get TLS info if not provided
                                if "tls_info" not in function_args:
                                    tls_result = tls_probe(host=function_args.get("domain"))
                                    function_args["tls_info"] = tls_result
                                
                                result = hosting_provider_detect(**function_args)
                            elif function_name == "http_check":
                                result = http_check(**function_args)
                            elif function_name == "tls_probe":
                                result = tls_probe(**function_args)
                            elif function_name == "take_screenshot_sync":
                                result = take_screenshot_sync(**function_args)
                            else:
                                result = {"error": f"Unknown tool: {function_name}"}
                            
                            logger.info(f"Function {function_name} executed successfully")
                            
                            # Store tool result for the next API call
                            tool_results.append({
                                "type": "tool_result",
                                "tool_call_id": current_function_call["call_id"],
                                "content": json.dumps(result)
                            })
                            
                            # Map tool names to friendly completion messages
                            completion_messages = {
                                "dns_lookup": "DNS check completed",
                                "http_check": "Website screenshot analysis completed",
                                "tls_probe": "SSL certificate check completed",
                                "take_screenshot_sync": "Website appearance analysis completed",
                                "hosting_provider_detect": "Hosting provider identification completed"
                            }
                            
                            completion_message = completion_messages.get(function_name, f"Completed {function_name}")
                            
                            yield {
                                "type": "tool_result",
                                "tool": function_name,
                                "result": result,
                                "message": completion_message
                            }
                            
                        except Exception as e:
                            logger.error(f"Error executing tool {function_name}: {str(e)}")
                            yield {
                                "type": "tool_error",
                                "tool": function_name,
                                "error": str(e),
                                "message": f"Error in {function_name}: {str(e)}"
                            }
                        
                        current_function_call = None
                        function_arguments = ""
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing function arguments: {str(e)}")
                        yield {
                            "type": "tool_error",
                            "tool": current_function_call["name"],
                            "error": f"Invalid arguments: {str(e)}",
                            "message": f"Error parsing arguments for {current_function_call['name']}"
                        }
            
            elif event_type == "response.completed":
                # Tool calls are completed, now get the final response
                logger.info("Tool calls completed, getting final response")
                
                if tool_results:
                    # Create new input with tool results
                    new_input = [
                        {"role": "user", "content": initial_message}
                    ]
                    
                    # Add the response output to our input (this includes the function calls)
                    new_input += response_output
                    
                    # Add tool results to the conversation
                    for tool_result in tool_results:
                        new_input.append({
                            "type": "function_call_output",
                            "call_id": tool_result["tool_call_id"],
                            "output": tool_result["content"]
                        })
                    
                    # Get the final response
                    yield {
                        "type": "status",
                        "message": "Analysis complete, generating report...",
                        "step": "generating_report"
                    }
                    
                    final_stream = client.responses.create(
                        model="gpt-4o-mini",
                        input=new_input,
                        stream=True
                    )
                    
                    # Process the final response
                    final_content = ""
                    for final_event in final_stream:
                        final_event_type = final_event.type
                        logger.debug(f"Final response event: {final_event_type}")
                        
                        if final_event_type == "response.output_text.delta":
                            if final_event.delta:
                                final_content += final_event.delta
                                yield {
                                    "type": "text_content",
                                    "content": final_event.delta,  # Send only the delta
                                    "message": "AI is analyzing..."
                                }
                        
                        elif final_event_type == "response.completed":
                            # Final response is complete
                            logger.info("Final response completed")
                            # Convert tool_results to the format expected by frontend
                            tool_data = {}
                            for i, tool_result in enumerate(tool_results):
                                try:
                                    tool_data[f"tool_{i}"] = json.loads(tool_result["content"])
                                except json.JSONDecodeError:
                                    tool_data[f"tool_{i}"] = {"raw_output": tool_result["content"]}
                            
                            yield {
                                "type": "result",
                                "data": {
                                    "summary": "AI Analysis Complete",
                                    "details": final_content,
                                    "mode": "openai",
                                    "tool_data": tool_data
                                }
                            }
                            return  # Exit the generator
                
                else:
                    # No tool calls were made, response is already complete
                    logger.info("No tool calls made, response is complete")
                    yield {
                        "type": "status",
                        "message": "Analysis complete, generating report...",
                        "step": "generating_report"
                    }
                    
                    yield {
                        "type": "result",
                        "data": {
                            "summary": "AI Analysis Complete",
                            "details": "Analysis completed without tool calls",
                            "mode": "openai",
                            "tool_data": {}  # No tool calls made
                        }
                    }
                    return  # Exit the generator
                
    except Exception as e:
        logger.error(f"Error in streaming response: {str(e)}")
        yield {
            "type": "error",
            "message": f"Streaming error: {str(e)}"
        }
