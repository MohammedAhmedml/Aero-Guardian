import pathway as pw

# ----------------------------
# Schema
# ----------------------------
class PollutionSchema(pw.Schema):
    city: str
    pm25: float
    timestamp: str


# ----------------------------
# Read Streaming Data
# ----------------------------
pollution_table = pw.io.csv.read(
    "pollution.csv",
    schema=PollutionSchema,
    mode="streaming"
)


# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(pm25):
    if pm25 < 100:
        return "Moderate"
    elif pm25 < 200:
        return "Unhealthy"
    elif pm25 < 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


pollution_with_risk = pollution_table.with_columns(
    risk=pw.apply(classify_risk, pw.this.pm25)
)


# ----------------------------
# Route Simulation
# ----------------------------
routes = pollution_with_risk.select(
    city=pw.this.city,
    pm25=pw.this.pm25,
    risk=pw.this.risk,
    route_a=pw.this.pm25 + 20,
    route_b=pw.this.pm25 - 30,
    route_c=pw.this.pm25 + 10,
)


def choose_route(a, b, c):
    options = {
        "Route A": a,
        "Route B": b,
        "Route C": c,
    }
    return min(options, key=options.get)


final_output = routes.with_columns(
    best_route=pw.apply(
        choose_route,
        pw.this.route_a,
        pw.this.route_b,
        pw.this.route_c,
    )
)
