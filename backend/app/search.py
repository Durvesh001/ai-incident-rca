import re


GENERIC_RUNBOOK_TAGS = {
    "api",
    "application",
    "error",
    "failure",
    "http",
    "https",
    "service",
}
MIN_RUNBOOK_SCORE = 5


def tokenize(value):
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def runbook_tag_matches(tag, alert_tokens):
    meaningful_tokens = tokenize(tag) - GENERIC_RUNBOOK_TAGS
    return bool(meaningful_tokens) and meaningful_tokens.issubset(alert_tokens)


def score_incident(alert_text, incident, extracted):
    score = 0
    text = alert_text.lower()
    
    if extracted.get("service") == incident.get("service"):
        score += 3
    
    if extracted.get("severity") == incident.get("severity"):
        score += 2
    
    for tag in incident.get("tags", []):
        if tag.lower() in text:
            score += 2
    
    if incident.get("alert", "").lower() in text:
        score += 2
    
    return score

def score_runbook(alert_text, runbook, extracted):
    score = 0
    normalized_alert_text = alert_text.lower()
    alert_tokens = tokenize(alert_text)
    extracted_service = extracted.get("service")
    extracted_severity = extracted.get("severity")
    runbook_alert = runbook.get("alert", "").lower()
    
    if extracted_service and extracted_service == runbook.get("service"):
        score += 3
    
    if extracted_severity and extracted_severity == runbook.get("severity"):
        score += 2
    
    for tag in runbook.get("tags", []):
        if runbook_tag_matches(tag, alert_tokens):
            score += 2
    
    if runbook_alert and runbook_alert in normalized_alert_text:
        score += 5
    
    return score   

def find_similar_incidents(alert_text, incidents, extracted, limit = 3):
    scored = []
    
    for incident in incidents:
        score = score_incident(alert_text, incident, extracted)
        
        if score > 2:
            scored.append({
                "score": score,
                "incident": incident
            })
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
    
def find_relevant_runbooks(alert_text, runbooks, extracted, limit=2):
    scored = []
    
    for runbook in runbooks:
        score = score_runbook(alert_text, runbook, extracted)
        
        if score >= MIN_RUNBOOK_SCORE:
            scored.append({
                "score": score,
                "runbook": runbook
            })
        
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
