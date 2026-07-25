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
    text = alert_text.lower()
    
    if extracted.get("service") == runbook.get("service"):
        score += 3
    
    if extracted.get("severity") == runbook.get("severity"):
        score += 2
    
    for tag in runbook.get("tags", []):
        if tag.lower() in text:
            score += 2
    
    if runbook.get("alert", "").lower() in text:
        score += 3
    
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
        
        if score > 0:
            scored.append({
                "score": score,
                "runbook": runbook
            })
        
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
