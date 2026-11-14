from django.core.exceptions import ValidationError

VALID_TRANSITIONS={
    'open': ['in_progress', 'pending', 'closed'],
    'in_progress': ['pending', 'resolved', 'closed'],
    'pending': ['in_progress', 'resolved', 'closed'],
    'resolved': ['closed','open'],
    'closed': ['open']
}

def validate_status_transition(old_status,new_status):
    if old_status==new_status:
        return
    allowed = VALID_TRANSITIONS.get(old_status, [])
    if new_status not in allowed:
        raise ValidationError(
            f"Cannot change status from '{old_status}' to '{new_status}'. "
            f"Allowed next steps: {', '.join(allowed) if allowed else 'none'}."
        )

