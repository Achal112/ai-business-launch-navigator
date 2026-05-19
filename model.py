def recommend_business(budget, experience, trend):

    if trend > 75 and budget > 70000:
        return "High Demand D2C Brand"

    elif trend > 60:
        return "E-commerce Store"

    elif budget < 20000:
        return "Dropshipping"

    elif experience == "Beginner":
        return "Reselling Business"

    return "Print on Demand"