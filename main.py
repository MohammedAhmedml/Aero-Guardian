import pathway as pw

# -------- Schema --------
class PollutionSchema(pw.Schema):
    city: str
    pm25: float
    timestamp: str

# -------- Read pollution.csv (streaming mode) --------
pollution_table = pw.io.csv.read(
    "pollution.csv",
    schema=PollutionSchema,
    mode="streaming"
)

# -------- Risk Level Logic --------
def get_risk(pm25: float) -> str:
    if pm25 > 300:
        return "Hazardous"
    elif pm25 > 200:
        return "Very Unhealthy"
    elif pm25 > 150:
        return "Unhealthy"
    elif pm25 > 100:
        return "Moderate"
    else:
        return "Good"

dashboard_table = pollution_table.with_columns(
    risk_level=pw.apply(get_risk, pollution_table.pm25)
)

# -------- Write dashboard.csv --------
pw.io.csv.write(dashboard_table, "dashboard.csv")

# -------- RUN ENGINE --------
pw.run()