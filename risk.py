# def calculate_risk(budget, risk_level, trend_score):

#     score = 0

#     if budget < 20000:
#         score += 30
#     else:
#         score += 10

#     if risk_level == "High":
#         score += 40
#     elif risk_level == "Medium":
#         score += 25
#     else:
#         score += 10

#     if trend_score < 40:
#         score += 30

#     return min(score, 100)

from openai import OpenAI
client = OpenAI()

def generate_risk_analysis(idea, budget, trend, risk):

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
                Analyze risk for business:

                Idea: {idea}
                Budget: ₹{budget}
                Trend: {trend}
                Risk Score: {risk}

                Give output in this format:

                Where:
                - ...

                Why:
                - ...

                Solution:
                - ...
                """
            }]
        )

        output = res.choices[0].message.content

        if output:
            return output

    except Exception as e:
        print("Risk AI Error:", e)

    # 🔥 GUARANTEED FALLBACK
    return f"""
### ⚠️ Risk Breakdown

**Where:**
- Low budget may limit growth
- Market competition is high

**Why:**
- Budget ₹{budget} restricts scaling
- Trend score ({trend}) indicates moderate demand

**Solution:**
- Start with small MVP
- Focus on niche audience
- Use organic marketing
"""