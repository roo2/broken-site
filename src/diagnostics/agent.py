import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from .config import settings
from .schemas import DiagnosticReport, Issue
from .tools import dns_lookup, tls_probe, http_check

logger = logging.getLogger(__name__)

# Tool definitions for the Chat Completions API - Focus on critical issues only
TOOLS = [
    {
        "type": "function",
        "function": {
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
        }
    },
    {
        "type": "function",
        "function": {
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
        }
    },
    {
        "type": "function",
        "function": {
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
        }
    }
]

FUNCTIONS = {
    "dns_lookup": dns_lookup,
    "http_check": http_check,
    "tls_probe": tls_probe,
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
        "content": f"""Diagnose the target "{target}" and focus ONLY on issues that would make the site "broken" for users.

Return a structured JSON report with:
- summary (string) - focus on critical issues that prevent site access,
- issues (list of objects: id, category in ["DNS","TLS","HTTP","Network","Content"], severity in ["medium","high"], evidence, recommended_fix),
- artifacts.raw_samples containing raw tool outputs.

CRITICAL: Only report issues that would prevent users from accessing or using the site. Ignore:
- Security headers (these don't break the site)
- Email authentication (SPF/DKIM/DMARC - these don't break the site)
- Minor configuration issues

Focus on:
- DNS resolution failures
- HTTP server errors (4xx, 5xx)
- TLS certificate problems
- Network connectivity issues
- Content loading problems

Steps:
1) Run dns_lookup on the domain.
2) Run http_check on https://{domain} (unless target is an explicit URL, then use it).
3) Run tls_probe on the domain.

Then synthesize findings into issues, focusing ONLY on what would make the site "broken" for users."""
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
    
    # Try to parse JSON - first try direct parsing, then extract from markdown
    try:
        # First attempt: direct JSON parsing
        data = json.loads(final_message)
        logger.info("Successfully parsed JSON response from OpenAI")
    except json.JSONDecodeError:
        # Second attempt: extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', final_message, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                logger.info("Successfully extracted and parsed JSON from markdown response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse extracted JSON: {str(e)}")
                logger.error(f"Extracted text: {json_match.group(1)}")
                # Fallback minimal report
                return DiagnosticReport(summary="Model response could not be parsed; see raw message.",
                                        issues=[],
                                        artifacts={"screenshots": [], "raw_samples": {"raw_model_text": final_message}})
        else:
            logger.error("No JSON found in markdown response")
            logger.error(f"Raw response text: {final_message}")
            # Fallback minimal report
            return DiagnosticReport(summary="Model response could not be parsed; see raw message.",
                                    issues=[],
                                    artifacts={"screenshots": [], "raw_samples": {"raw_model_text": final_message}})
    
    # Normalize into DiagnosticReport
    try:
        result = DiagnosticReport(**data)
        logger.info("Successfully created DiagnosticReport from OpenAI response")
        return result
    except Exception as e:
        logger.error(f"Failed to create DiagnosticReport from parsed data: {str(e)}", exc_info=True)
        logger.error(f"Parsed data: {data}")
        # Fallback minimal report
        return DiagnosticReport(summary="Model response could not be converted to report format.",
                                issues=[],
                                artifacts={"screenshots": [], "raw_samples": {"raw_model_text": final_message, "parsed_data": data}})
