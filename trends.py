from pytrends.request import TrendReq
import random

def get_trend_score(keyword):
    try:
        from pytrends.request import TrendReq
        py = TrendReq(hl='en-IN', tz=330)
        py.build_payload([keyword], timeframe='today 3-m')
        data = py.interest_over_time()

        if not data.empty:
            return int(data[keyword].mean())
    except Exception as e:
        print("Trend error:", e)

    return random.randint(50, 80)