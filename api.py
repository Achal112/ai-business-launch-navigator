import requests

def get_product_data(query):
    try:
        url = f"https://dummyjson.com/products/search?q={query}"
        res = requests.get(url)
        data = res.json()

        if data["products"]:
            p = data["products"][0]

            return {
                "price": p["price"],
                "rating": p["rating"],
                "stock": p["stock"]
            }

    except:
        pass

    return {"price": 500, "rating": 3.5, "stock": 50}