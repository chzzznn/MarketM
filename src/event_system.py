# /src/event_system.py
import random

EVENTS = [
    {
        "name": "Recession",
        "prob": 0.167,
        "impact": {"all": -0.20, "Gold Futures": 0.30}
    },
    {
        "name": "Tech Boom",
        "prob": 0.167,
        "impact": {"TechCorp": 1.00}
    },
    {
        "name": "Inflation Spike",
        "prob": 0.167,
        "impact": {"all": -0.10, "Gold Futures": 0.25}
    }
]

def maybe_trigger_event():
    chosen = random.choices(EVENTS + [None], weights=[e["prob"] for e in EVENTS] + [1 - sum(e["prob"] for e in EVENTS)])
    return chosen[0]
