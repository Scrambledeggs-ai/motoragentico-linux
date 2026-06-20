CLAUDE_PRICING = {
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_creation": 3.75,
        "cache_read": 0.30,
    },
    "claude-opus-4-8": {
        "input": 15.00,
        "output": 75.00,
        "cache_creation": 18.75,
        "cache_read": 1.50,
    },
    "claude-haiku-4-5": {
        "input": 0.80,
        "output": 4.00,
        "cache_creation": 1.00,
        "cache_read": 0.08,
    },
}

DEFAULT_CLAUDE_PRICING = CLAUDE_PRICING["claude-sonnet-4-6"]

CLAUDE_SUBSCRIPTIONS = {
    "Pro": 20.0,
    "Max (5x)": 100.0,
    "Max (20x)": 200.0,
    "Team": 25.0,
}

HERMES_SUBSCRIPTIONS = {
    "Hermes Free": 0.0,
    "Hermes Pro": 20.0,
}
