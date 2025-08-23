import logging
from fastapi import FastAPI, HTTPException
from .schemas import DiagnoseRequest, DiagnosticReport, UserFriendlyReport
from pydantic import BaseModel
from .offline import run_offline_diagnosis
from .agent import run_agent
from .user_friendly import convert_to_user_friendly
from .config import settings

# Configure logging
import os
log_level = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.ERROR),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level, logging.ERROR))

app = FastAPI(title="Site Diagnostics Pro", version="0.1.0")

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/diagnose", response_model=DiagnosticReport)
def diagnose(req: DiagnoseRequest, mode: str = "offline"):
    """Diagnose a target (URL or domain). mode=offline runs deterministic checks.
    mode=openai uses the OpenAI Responses API with tool-calling for reasoning & reporting.
    """
    logger.info(f"Starting diagnosis for target: {req.target} with mode: {mode}")
    
    try:
        if mode == "openai":
            logger.info("Using OpenAI agent mode")
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY is not set")
                raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set")
            result = run_agent(req.target)
            logger.info("OpenAI agent diagnosis completed successfully")
            return result
        else:
            logger.info("Using offline diagnosis mode")
            result = run_offline_diagnosis(req.target)
            logger.info("Offline diagnosis completed successfully")
            return result
    except HTTPException:
        logger.error(f"HTTPException in diagnose endpoint: {req.target}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in diagnose endpoint for {req.target}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagnose/user-friendly", response_model=UserFriendlyReport)
def diagnose_user_friendly(req: DiagnoseRequest, mode: str = "offline"):
    """Diagnose a target and return a user-friendly report focusing on the most critical issue.
    Perfect for non-technical users who just want to know what's wrong and how to fix it.
    """
    logger.info(f"Starting user-friendly diagnosis for target: {req.target} with mode: {mode}")
    
    try:
        # Get the full diagnostic report
        if mode == "openai":
            logger.info("Using OpenAI agent mode for user-friendly diagnosis")
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY is not set for user-friendly diagnosis")
                raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set")
            full_report = run_agent(req.target)
            logger.info("OpenAI agent diagnosis completed for user-friendly conversion")
        else:
            logger.info("Using offline diagnosis mode for user-friendly diagnosis")
            full_report = run_offline_diagnosis(req.target)
            logger.info("Offline diagnosis completed for user-friendly conversion")
        
        # Convert to user-friendly format
        logger.info(f"Converting {len(full_report.issues)} issues to user-friendly format")
        user_friendly_report = convert_to_user_friendly(full_report.issues)
        logger.info("User-friendly conversion completed successfully")
        return user_friendly_report
        
    except HTTPException:
        logger.error(f"HTTPException in user-friendly diagnose endpoint: {req.target}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in user-friendly diagnose endpoint for {req.target}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

class TextualSummaryResponse(BaseModel):
    summary: str
    details: str
    recommendations: str
    mode: str

@app.post("/diagnose/textual", response_model=TextualSummaryResponse)
def diagnose_textual(req: DiagnoseRequest, mode: str = "openai"):
    """Diagnose a target and return a textual summary that's easy to read and understand.
    This endpoint is perfect for displaying results in a user-friendly way.
    """
    logger.info(f"Starting textual diagnosis for target: {req.target} with mode: {mode}")
    
    try:
        # Get the full diagnostic report
        if mode == "openai":
            logger.info("Using OpenAI agent mode for textual diagnosis")
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY is not set for textual diagnosis")
                raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set")
            full_report = run_agent(req.target)
            logger.info("OpenAI agent diagnosis completed for textual summary")
        else:
            logger.info("Using offline diagnosis mode for textual diagnosis")
            full_report = run_offline_diagnosis(req.target)
            logger.info("Offline diagnosis completed for textual summary")
        
        # Handle markdown response from OpenAI agent
        if mode == "openai":
            # Get the raw markdown response
            raw_samples = full_report.artifacts.raw_samples
            raw_markdown = raw_samples.get("raw_model_text", full_report.summary or "Diagnostic analysis completed.")
            
            # For OpenAI mode, return the raw markdown for frontend rendering
            summary = "AI Analysis Complete"
            details = raw_markdown
            recommendations = ""  # Will be handled by frontend markdown rendering
        else:
            # Handle offline mode with the old structured format
            summary = full_report.summary or "Diagnostic analysis completed."
            
            # Build details section
            details_parts = []
            if full_report.issues:
                # Filter issues based on priority - if there are high severity issues, hide low/info ones
                high_priority_issues = [issue for issue in full_report.issues if issue.severity in ["high", "medium"]]
                low_priority_issues = [issue for issue in full_report.issues if issue.severity in ["low", "info"]]
                
                # If there are high priority issues, only show those
                if high_priority_issues:
                    issues_to_show = high_priority_issues
                    if low_priority_issues:
                        details_parts.append(f"Found {len(high_priority_issues)} critical issue(s) (hiding {len(low_priority_issues)} minor issues):")
                    else:
                        details_parts.append(f"Found {len(high_priority_issues)} issue(s):")
                else:
                    issues_to_show = full_report.issues
                    details_parts.append(f"Found {len(full_report.issues)} issue(s):")
                
                for i, issue in enumerate(issues_to_show, 1):
                    severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "ℹ️"}.get(issue.severity, "ℹ️")
                    # Handle evidence as either string or dict
                    evidence_text = ""
                    if isinstance(issue.evidence, dict):
                        evidence_text = f"Technical data: {str(issue.evidence)[:100]}..."
                    else:
                        evidence_text = str(issue.evidence)
                    
                    details_parts.append(f"{i}. {severity_emoji} {issue.category} ({issue.severity} severity)")
                    if evidence_text:
                        details_parts.append(f"   Evidence: {evidence_text}")
            else:
                details_parts.append("✅ No issues found - your website appears to be working correctly!")
            
            details = "\n".join(details_parts)
            
            # Build recommendations section
            recommendations_parts = []
            if full_report.issues:
                # Use the same filtered issues for recommendations
                if high_priority_issues:
                    issues_for_recommendations = high_priority_issues
                else:
                    issues_for_recommendations = full_report.issues
                    
                recommendations_parts.append("Recommendations:")
                for i, issue in enumerate(issues_for_recommendations, 1):
                    if issue.recommended_fix:
                        recommendations_parts.append(f"{i}. {issue.recommended_fix}")
                        
                        # Add hosting provider specific instructions if available
                        if issue.hosting_provider:
                            provider = issue.hosting_provider
                            recommendations_parts.append(f"   🏢 Hosting Provider: {provider.get('name', 'Unknown')}")
                            if provider.get('dashboard_url'):
                                recommendations_parts.append(f"   🔗 Dashboard: {provider.get('dashboard_url')}")
                            if provider.get('instructions'):
                                recommendations_parts.append(f"   📋 Instructions: {provider.get('instructions')}")
                            if provider.get('support_url'):
                                recommendations_parts.append(f"   🆘 Support: {provider.get('support_url')}")
                            recommendations_parts.append("")  # Add spacing
            else:
                recommendations_parts.append("🎉 Your website is in good shape! Keep up the good work.")
            
            recommendations = "\n".join(recommendations_parts)
        
        logger.info("Textual summary created successfully")
        return TextualSummaryResponse(
            summary=summary,
            details=details,
            recommendations=recommendations,
            mode=mode
        )
        
    except HTTPException:
        logger.error(f"HTTPException in textual diagnose endpoint: {req.target}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in textual diagnose endpoint for {req.target}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
