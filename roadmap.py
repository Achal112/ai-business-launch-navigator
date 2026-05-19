from openai import OpenAI

client = OpenAI()

def generate_roadmap(idea, budget):

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
                Give a business roadmap in JSON format with:
                Month 1, Month 2, Month 3

                Each month should include:
                platform, action, how

                Idea: {idea}
                Budget: ₹{budget}
                """
            }]
        )

        import json
        return json.loads(res.choices[0].message.content)

    except:
        # 🔥 fallback structured data
        return {
            "Month 1": {
                "platform": "Instagram",
                "action": "Build audience",
                "how": "Post reels daily + trending content"
            },
            "Month 2": {
                "platform": "Shopify",
                "action": "Setup store",
                "how": "Add products, payment gateway"
            },
            "Month 3": {
                "platform": "Ads",
                "action": "Scale business",
                "how": "Run Meta ads + influencer collab"
            }
        }