focus_states = {}

def set_focus(user_id, task_name):
    """Set the focus state for a user with a specific task."""
    focus_states[user_id] = task_name

def clear_focus(user_id):
    """Clear the focus state for a user."""
    if user_id in focus_states:
        del focus_states[user_id]

def get_focus(user_id):
    """Get the current focus state of a user."""
    return focus_states.get(user_id, None)

def is_focused(user_id, task_name=None):
    """
    Check if a user is in focus mode.
    Optionally, check if they are focused on a specific task.
    """
    if task_name:
        return focus_states.get(user_id) == task_name
    return user_id in focus_states
