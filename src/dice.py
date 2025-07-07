# /src/dice.py

import random

def roll_volatility_die():
    """
    Simulates a roll of a 6-sided die to represent volatility.
    """
    return random.randint(1, 6)

def roll_direction():
    """
    Randomly returns 1 (up) or -1 (down) to determine price direction.
    """
    return 1 if random.random() > 0.5 else -1

def roll_dice_pool(size=2, modifier=1.0, strategy='max'):
    rolls = [random.randint(1, 6) for _ in range(size)]
    if strategy == 'max':
        result = max(rolls)
    elif strategy == 'avg':
        result = sum(rolls) / size
    elif strategy == 'min':
        result = min(rolls)
    return result * modifier
