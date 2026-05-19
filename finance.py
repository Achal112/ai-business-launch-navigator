def break_even(fixed_cost, selling_price, variable_cost):
    return fixed_cost / (selling_price - variable_cost)

def profit(revenue, total_cost):
    return revenue - total_cost

def revenue_projection(price):
    return [price * i for i in [50, 100, 150, 200]]