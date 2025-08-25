import json
import logging
from typing import Dict, Any, List, Generator
from openai import OpenAI
from .config import settings

from .tools import dns_lookup, tls_probe, http_check, hosting_provider_detect, take_screenshot_sync

logger = logging.getLogger(__name__)





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

IMPORTANT: When you see generic error messages from hosting providers, the most common cause is an expired hosting account or unpaid bill.

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

IMPORTANT: 
- Follow this template exactly and use proper markdown formatting with blank lines between sections
- If the site uses a specific platform (WordPress, Shopify, etc.), tailor the instructions to that platform
- Consider the technology stack when providing fix instructions (e.g., WordPress admin vs. hosting dashboard)"""
    
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
