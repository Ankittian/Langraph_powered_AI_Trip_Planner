"""Place Search Tool — search for attractions, restaurants, hotels via free APIs."""

import requests
from langchain_core.tools import tool


@tool
def search_places(query: str, city: str, category: str = "tourism.attraction") -> str:
    """
    Search for places (attractions, restaurants, hotels) in a given city.

    Args:
        query: What to search for (e.g. 'best restaurants', 'top attractions').
        city: The city name to search in (e.g. 'Goa', 'Tokyo').
        category: Category filter — 'tourism.attraction', 'catering.restaurant',
                  'accommodation.hotel', 'tourism.sights'. Default is 'tourism.attraction'.

    Returns:
        A formatted list of places with names, addresses, and ratings.
    """
    try:
        # Step 1: Geocode the city
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = requests.get(geo_url, params={"name": city, "count": 1}, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return f"Could not find location data for '{city}'."

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]

        # Step 2: Search using Geoapify Places API (free tier: 3000 req/day)
        # Using the free Nominatim/Overpass approach as fallback
        overpass_url = "https://overpass-api.de/api/interpreter"

        # Map category to OSM tags
        category_map = {
            "tourism.attraction": '["tourism"="attraction"]',
            "tourism.sights": '["tourism"~"attraction|museum|viewpoint|artwork"]',
            "catering.restaurant": '["amenity"="restaurant"]',
            "accommodation.hotel": '["tourism"~"hotel|motel|hostel|guest_house"]',
        }
        osm_tag = category_map.get(category, '["tourism"="attraction"]')

        overpass_query = f"""
        [out:json][timeout:15];
        (
          node{osm_tag}(around:10000,{lat},{lon});
          way{osm_tag}(around:10000,{lat},{lon});
        );
        out center 15;
        """

        resp = requests.post(overpass_url, data={"data": overpass_query}, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        elements = data.get("elements", [])
        if not elements:
            return f"No results found for '{query}' in {city} (category: {category})."

        lines = [f"📍 Results for '{query}' in {city} (showing top 15):\n"]
        for i, el in enumerate(elements[:15], 1):
            tags = el.get("tags", {})
            name = tags.get("name", tags.get("name:en", "Unnamed"))
            addr_street = tags.get("addr:street", "")
            addr_city = tags.get("addr:city", city)
            cuisine = tags.get("cuisine", "")
            stars = tags.get("stars", "")
            website = tags.get("website", "")
            phone = tags.get("phone", "")
            opening = tags.get("opening_hours", "")

            details = []
            if addr_street:
                details.append(f"📌 {addr_street}, {addr_city}")
            if cuisine:
                details.append(f"🍽 Cuisine: {cuisine}")
            if stars:
                details.append(f"⭐ Stars: {stars}")
            if opening:
                details.append(f"🕐 Hours: {opening}")
            if phone:
                details.append(f"📞 {phone}")
            if website:
                details.append(f"🔗 {website}")

            detail_str = " | ".join(details) if details else "No additional details available"
            lines.append(f"  {i}. **{name}** — {detail_str}")

        return "\n".join(lines)

    except requests.RequestException as e:
        return f"Error searching for places: {e}"
    except Exception as e:
        return f"Unexpected error in place search tool: {e}"


@tool
def search_hotels(city: str, budget_level: str = "mid-range") -> str:
    """
    Search for hotels in a given city based on budget level.

    Args:
        city: The city to search hotels in (e.g. 'Paris', 'Mumbai').
        budget_level: One of 'budget', 'mid-range', 'luxury'. Default is 'mid-range'.

    Returns:
        A formatted list of hotel options.
    """
    return search_places.invoke({
        "query": f"{budget_level} hotels",
        "city": city,
        "category": "accommodation.hotel"
    })


# Export tool list for the agent
place_tools = [search_places, search_hotels]
