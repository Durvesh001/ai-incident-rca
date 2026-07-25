import re
from app.data_loader import load_incidents, load_runbooks
from app.search import find_similar_incidents, find_relevant_runbooks

def extract_field(alert_text):
    text = alert_text.lower()
    
    service_match = re.search(r"service:\s*([a-zA-Z0-9-_]+)", alert_text, re.IGNORECASE)
    severity_match = re.search(r"severity:\s*(P[0-9])", alert_text, re.IGNORECASE)
    metric_match = re.search(r"metric:\s*(.+)", alert_text, re.IGNORECASE)
    
    error_type = "unknown"
    
    if "timeout" in text:
        error_type = "timeout"
    elif "5xx" in text or "500" in text:
        error_type = "5xx error"
    elif "latency" in text or "slow" in text:
        error_type = "latency"
    elif "oom" in text or "memory" in text:
        error_type = "memory issue"
    elif "restart" in text or "crash" in text:
        error_type = "pod restart"
        
    return {
        "service": service_match.group(1) if service_match else None,
        "severity": severity_match.group(1) if severity_match else None,
        "error_type": error_type,
        "metric": metric_match.group(1).strip() if metric_match else None
    }

    
    
def generate_rca(extracted, matched_incidents, matched_runbooks):
    top_incident = matched_incidents[0]["incident"] if matched_incidents else None
    top_runbook = matched_runbooks[0]["runbook"] if matched_runbooks else None
    
    service = extracted.get("service") or "Affected Service"
    error_type = extracted.get("error_type") or "unknown issue"
    
    evidence = ["Alert input was parsed for service, severity, error type, and metric."]
    
    if top_incident:
        evidence.append(f"Similar incident found: {top_incident['id']} - {top_incident['title']}")
    if top_runbook:
        evidence.append(f"Relevant runbook found: {top_runbook['id']} - {top_runbook['alert']}")
    if extracted.get("metric"):
        evidence.append(f"Metric mentioned in alert: {extracted['metric']}")
    
    remediation_steps = []
    
    if top_runbook:
        remediation_steps.extend(top_runbook.get("remediation_steps", []))
    if top_incident:
        remediation_steps.extend(top_incident.get("remediation", []))
    
    confidence_score = 40
    
    if top_incident: confidence_score += 30
    if top_runbook: confidence_score += 20
    if extracted.get("service"):
        confidence_score += 5

    if extracted.get("severity"):
        confidence_score += 5

    confidence_score = min(confidence_score, 95)

    return {
        "incident_summary": f"{service} is showing {error_type} related symptoms.",
        "impact": "Users may be experiencing failed, slow, or degraded requests.",
        "evidence": evidence,
        "probable_root_cause": top_incident["root_cause"] if top_incident else "Not enough matching evidence to determine a specific root cause.",
        "suggested_remediation": remediation_steps,
        "confidence_score": confidence_score
    } 

def analyze_incident(alert_text):
    incidents = load_incidents()
    runbooks = load_runbooks()
    
    extracted = extract_field(alert_text)
    
    matched_incidents = find_similar_incidents(alert_text, incidents, extracted)
    matched_runbooks = find_relevant_runbooks(alert_text, runbooks, extracted)
    
    rca = generate_rca(extracted, matched_incidents, matched_runbooks)
    
    return {
        "extracted_fields": extracted,
        "similar_incidents": matched_incidents,
        "relevant_runbooks": matched_runbooks,
        "rca": rca
    }