import random

def roll_volatility_die():
    return random.randint(1, 6)

def roll_sentiment():
    return random.choice(["Bear", "Neutral", "Bull"])

def sentiment_multiplier(sentiment):
    return {"Bear": 0.8, "Neutral": 1.0, "Bull": 1.2}[sentiment]
