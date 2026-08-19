import requests
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="weather_script")


# --------------------------------------------------
# Address -> Latitude / Longitude
# --------------------------------------------------

def get_coordinates(address):

    location = geolocator.geocode(address)

    if location:
        return location.latitude, location.longitude

    return None, None


# --------------------------------------------------
# Download one day's weather
# --------------------------------------------------

def get_hourly_weather(lat, lon, date):

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={date}"
        f"&end_date={date}"
        "&hourly="
        "temperature_2m,"
        "relative_humidity_2m,"
        "dew_point_2m,"
        "apparent_temperature,"
        "wind_speed_10m,"
        "shortwave_radiation,"
        "wet_bulb_temperature_2m"
        "&timezone=auto"
    )

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    return response.json()

# Weather for one Onset_Time
def get_weather_for_time(weather, onset_time):

    target_hour = onset_time.hour

    hourly = weather["hourly"]

    for i, t in enumerate(hourly["time"]):

        hour = int(t[11:13])

        if hour == target_hour:

            return {
                "Temperature": hourly["temperature_2m"][i],
                "Relative Humidity": hourly["relative_humidity_2m"][i],
                "Dew Point": hourly["dew_point_2m"][i],
                "Apparent Temperature": hourly["apparent_temperature"][i],
                "Wind Speed": hourly["wind_speed_10m"][i],
                "Solar Radiation": hourly["shortwave_radiation"][i],
                "Wet Bulb": hourly["wet_bulb_temperature_2m"][i]
            }

    return None

def get_weather_between_times(weather, start_time, end_time):

    hourly = weather["hourly"]

    weather_list = []

    start_hour = start_time.hour
    end_hour = end_time.hour

    for i, t in enumerate(hourly["time"]):

        hour = int(t[11:13])

        if start_hour <= hour <= end_hour:

            weather_list.append({
                "Hour": hour,
                "Temperature": hourly["temperature_2m"][i],
                "Relative Humidity": hourly["relative_humidity_2m"][i],
                "Dew Point": hourly["dew_point_2m"][i],
                "Apparent Temperature": hourly["apparent_temperature"][i],
                "Wind Speed": hourly["wind_speed_10m"][i],
                "Solar Radiation": hourly["shortwave_radiation"][i],
                "Wet Bulb": hourly["wet_bulb_temperature_2m"][i]
            })

    return weather_list

# Calculate Summary Statistics
def calculate_weather_statistics(df):

    return {

        # Temperature
        "Temperature Mean": round(df["Temperature (°C)"].mean(), 2),
        "Temperature Min": round(df["Temperature (°C)"].min(), 2),
        "Temperature Max": round(df["Temperature (°C)"].max(), 2),

        # Humidity
        "Humidity Mean": round(df["Relative Humidity (%)"].mean(), 2),
        "Humidity Min": round(df["Relative Humidity (%)"].min(), 2),
        "Humidity Max": round(df["Relative Humidity (%)"].max(), 2),

        # Dew Point
        "Dew Point Mean": round(df["Dew Point (°C)"].mean(), 2),
        "Dew Point Min": round(df["Dew Point (°C)"].min(), 2),
        "Dew Point Max": round(df["Dew Point (°C)"].max(), 2),

        # Apparent Temperature
        "Apparent Temperature Mean": round(df["Apparent Temperature (°C)"].mean(), 2),
        "Apparent Temperature Min": round(df["Apparent Temperature (°C)"].min(), 2),
        "Apparent Temperature Max": round(df["Apparent Temperature (°C)"].max(), 2),

        # WBGT
        "WBGT Mean": round(df["WBGT (°C)"].mean(), 2),
        "WBGT Min": round(df["WBGT (°C)"].min(), 2),
        "WBGT Max": round(df["WBGT (°C)"].max(), 2)

    }