
# Hardcoded function to decide which agent to use (Not necessary after implementation of router agent)
def route_message(message: str) -> str:
    text = message.lower()

    urgent_keywords = [
        "fraud",
        "stolen",
        "scam",
        "unauthorized transaction",
        "card was cloned",
        "account hacked",
        "blocked account",
    ]

    consultant_keywords = [
        "should i",
        "is it worth",
        "risk",
        "safe",
        "suitable",
        "recommend",
        "my financial situation",
        "afford",
        "can i pay",
        "debt",
        "income",
        "urgent",
        "need immediately",
        "better than financing",
        "consortium or financing",
        "worth joining",
        "bid strategy",
    ]

    salesman_keywords = [
        "consortium",
        "consorcio",
        "consórcio",
        "automobile",
        "car",
        "motorcycle",
        "moto",
        "real estate",
        "property",
        "house",
        "apartment",
        "services",
        "plan",
        "credit amount",
        "installment",
        "available options",
        "show me",
    ]

    if any(keyword in text for keyword in urgent_keywords):
        return "human_support"

    if any(keyword in text for keyword in consultant_keywords):
        return "consultant"

    if any(keyword in text for keyword in salesman_keywords):
        return "salesman"

    return "consultant"