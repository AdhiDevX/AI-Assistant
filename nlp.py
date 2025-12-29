ACTIONS = {
    "open": ["open", "launch", "start", "run"],
    "close": ["close", "exit", "quit"],
    "search": ["search", "find", "look for"]
}

TARGETS = {
    "browser": ["browser", "google"],
    "youtube": ["youtube", "yt"],
    "assistant": ["assistant", "nova"]
}

FILLER_WORDS = [
    "please", "can you", "could you", "would you",
    "hey nova", "i want to", "for me", "now"
]

def normalize_command(command):
    for f in FILLER_WORDS:
        command = command.replace(f, "")
    return command.strip()

def split_commands(command):
    for sep in [" and ", " then ", " also "]:
        if sep in command:
            return [c.strip() for c in command.split(sep)]
    return [command]

def extract_action_target(command):
    action_found, target_found = None, None
    for action, words in ACTIONS.items():
        if any(w in command for w in words):
            action_found = action
            break
    for target, words in TARGETS.items():
        if any(w in command for w in words):
            target_found = target
            break
    return action_found, target_found

def extract_app_name(command):
    for word in ACTIONS["open"]:
        if word in command:
            return command.split(word, 1)[1].strip()
    return None

def extract_parameter(command, keyword):
    if keyword in command:
        return command.split(keyword, 1)[1].strip()
    return None
