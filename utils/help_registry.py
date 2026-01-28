HELP = {}

def register_help(plugin, command, usage, description):
    if plugin not in HELP:
        HELP[plugin] = []
    HELP[plugin].append({
        "command": command,
        "usage": usage,
        "description": description
    })

def get_all_help():
    return HELP

def get_plugin_help(name):
    return HELP.get(name)