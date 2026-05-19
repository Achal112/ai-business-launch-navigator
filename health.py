def health_score(budget_score, risk_score, profit_score, experience_score):

    return (
        0.30 * budget_score +
        0.25 * (100 - risk_score) +
        0.25 * profit_score +
        0.20 * experience_score
    )