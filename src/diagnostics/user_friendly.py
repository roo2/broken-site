import logging
from typing import List, Optional
from .schemas import Issue, UserFriendlyIssue, UserFriendlyReport

logger = logging.getLogger(__name__)

def convert_to_user_friendly(issues: List[Issue]) -> UserFriendlyReport:
    """
    Convert technical diagnostic issues into user-friendly messages.
    Prioritizes the most critical issue that's causing the site to be "broken".
    """
    logger.info(f"Converting {len(issues)} technical issues to user-friendly format")
    
    if not issues:
        logger.info("No issues found - returning healthy site report")
        return UserFriendlyReport(
            is_broken=False,
            user_message="✅ Your website is working properly! No critical issues found.",
            all_issues_count=0
        )
    
    # Sort issues by priority (high severity first, then by category importance)
    priority_order = {
        "DNS": 1,      # Most critical - site won't load
        "HTTP": 2,     # Site loads but with errors
        "TLS": 3,      # Security issues
        "SecurityHeaders": 4,  # Security improvements
        "EmailAuth": 5,        # Email deliverability
        "Network": 6,
        "Content": 7
    }
    
    severity_weight = {"high": 3, "medium": 2, "low": 1, "info": 0}
    
    sorted_issues = sorted(issues, key=lambda x: (
        -severity_weight.get(x.severity, 0),  # High severity first
        priority_order.get(x.category, 999)   # Then by category priority
    ))
    
    primary_issue = sorted_issues[0]
    logger.info(f"Primary issue selected: {primary_issue.category} - {primary_issue.severity} severity")
    user_friendly_issue = _convert_issue_to_user_friendly(primary_issue)
    
    # Determine if site is "broken" (high severity DNS/HTTP/TLS issues)
    is_broken = (
        primary_issue.severity == "high" and 
        primary_issue.category in ["DNS", "HTTP", "TLS"]
    )
    
    logger.info(f"Site broken status: {is_broken} (severity: {primary_issue.severity}, category: {primary_issue.category})")
    
    # Generate user message
    if is_broken:
        user_message = f"🚨 Your website is currently broken due to: {user_friendly_issue.title}"
        quick_fix = user_friendly_issue.solution
        logger.info("Generated broken site message with quick fix")
    else:
        user_message = f"⚠️ Your website is working but has some issues: {user_friendly_issue.title}"
        quick_fix = None
        logger.info("Generated working site with issues message")
    
    logger.info(f"User-friendly conversion completed. Total issues: {len(issues)}")
    return UserFriendlyReport(
        is_broken=is_broken,
        primary_issue=user_friendly_issue,
        user_message=user_message,
        quick_fix=quick_fix,
        all_issues_count=len(issues)
    )

def _convert_issue_to_user_friendly(issue: Issue) -> UserFriendlyIssue:
    """Convert a technical issue into user-friendly language"""
    
    # DNS Issues
    if issue.category == "DNS":
        if "lookup error" in issue.id.lower():
            return UserFriendlyIssue(
                title="Domain Name Not Found",
                description="Your website's domain name cannot be found on the internet.",
                impact="Visitors cannot access your website at all.",
                solution="Contact your domain registrar to ensure your domain is active and properly configured.",
                urgency="critical",
                technical_details=issue.evidence
            )
        elif "not resolving" in issue.evidence.lower():
            return UserFriendlyIssue(
                title="Domain Not Resolving",
                description="Your domain name is not pointing to your website server.",
                impact="Visitors get 'site not found' errors.",
                solution="Update your domain's DNS settings to point to your web hosting provider.",
                urgency="critical",
                technical_details=issue.evidence
            )
        else:
            return UserFriendlyIssue(
                title="DNS Configuration Issue",
                description="Your domain's DNS settings have a problem.",
                impact="Visitors may have trouble accessing your website.",
                solution="Contact your domain registrar or DNS provider to check your DNS configuration.",
                urgency="critical",
                technical_details=issue.evidence
            )
    
    # HTTP Issues
    elif issue.category == "HTTP":
        if "server error" in issue.id.lower():
            return UserFriendlyIssue(
                title="Website Server Error",
                description="Your website server is experiencing technical problems.",
                impact="Visitors see error messages instead of your website.",
                solution="Contact your web hosting provider to check server status and restart if needed.",
                urgency="critical",
                technical_details=issue.evidence
            )
        elif "not reachable" in issue.evidence.lower():
            return UserFriendlyIssue(
                title="Website Not Accessible",
                description="Your website server is not responding to requests.",
                impact="Visitors cannot load your website.",
                solution="Check if your web hosting service is running and contact your hosting provider.",
                urgency="critical",
                technical_details=issue.evidence
            )
        else:
            return UserFriendlyIssue(
                title="Website Connection Problem",
                description="Your website is not responding properly to requests.",
                impact="Visitors may see error messages or slow loading times.",
                solution="Contact your web hosting provider to check server status and configuration.",
                urgency="critical",
                technical_details=issue.evidence
            )
    
    # TLS/SSL Issues
    elif issue.category == "TLS":
        if "expiring" in issue.id.lower():
            return UserFriendlyIssue(
                title="Security Certificate Expiring Soon",
                description="Your website's security certificate will expire shortly.",
                impact="Visitors may see security warnings in their browsers.",
                solution="Renew your SSL certificate through your hosting provider or certificate authority.",
                urgency="important",
                technical_details=issue.evidence
            )
        elif "handshake error" in issue.id.lower():
            return UserFriendlyIssue(
                title="Security Certificate Problem",
                description="Your website's security certificate has an issue.",
                impact="Visitors see security warnings and may not trust your site.",
                solution="Contact your hosting provider to fix or renew your SSL certificate.",
                urgency="critical",
                technical_details=issue.evidence
            )
        else:
            return UserFriendlyIssue(
                title="Security Certificate Issue",
                description="Your website's security certificate has a problem.",
                impact="Visitors may see security warnings in their browsers.",
                solution="Contact your hosting provider to check and fix your SSL certificate.",
                urgency="important",
                technical_details=issue.evidence
            )
    
    # Security Headers
    elif issue.category == "SecurityHeaders":
        return UserFriendlyIssue(
            title="Security Headers Missing",
            description="Your website is missing some recommended security protections.",
            impact="Your website is less secure against certain types of attacks.",
            solution="Ask your web developer to add security headers to your website configuration.",
            urgency="minor",
            technical_details=issue.evidence
        )
    
    # Email Authentication
    elif issue.category == "EmailAuth":
        return UserFriendlyIssue(
            title="Email Security Missing",
            description="Your domain is missing email security protections.",
            impact="Your emails may be marked as spam or spoofed by attackers.",
            solution="Add SPF and DMARC records to your domain's DNS settings.",
            urgency="minor",
            technical_details=issue.evidence
        )
    
    # Fallback for unknown issues
    else:
        return UserFriendlyIssue(
            title=f"{issue.category} Issue",
            description=issue.evidence,
            impact="May affect website functionality or security.",
            solution=issue.recommended_fix,
            urgency="medium" if issue.severity == "high" else "minor",
            technical_details=issue.evidence
        )
