SECTORS = [
    "Agriculture", "Energy", "Health", "Transportation", "Water",
    "Urban Development", "Industry", "Buildings", "Other",
]

HAZARDS = [
    "Flood", "Extreme heat", "Drought", "Extreme precipitation",
    "Landslide", "Wildfire", "Storm", "Sea-level rise",
]

RISK_BANDS = ["Low", "Moderate", "High", "Critical"]

PAKISTAN_REGIONS = [
    "Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan",
    "Islamabad Capital Territory", "Gilgit-Baltistan", "Azad Jammu & Kashmir",
]

MOUNTAIN_SYSTEMS = [
    "Himalayas", "Karakoram", "Hindu Kush", "Sulaiman / Koh-e-Suleman",
    "Spīn Ghar / Safed Koh", "Kirthar", "Salt Range",
]

RESILIENCE_PRIORITIES = [
    "drainage and flood protection", "heat resilience", "water availability",
    "slope stability", "asset protection", "emergency preparedness",
    "operational continuity", "climate-adaptive design",
]

REGION_PRIORITIES = {
    "Punjab": ["drainage and flood protection", "heat resilience", "water availability", "asset protection", "emergency preparedness", "operational continuity", "climate-adaptive design"],
    "Sindh": ["drainage and flood protection", "heat resilience", "water availability", "asset protection", "emergency preparedness", "operational continuity", "climate-adaptive design"],
    "Khyber Pakhtunkhwa": ["drainage and flood protection", "slope stability", "heat resilience", "water availability", "asset protection", "emergency preparedness", "operational continuity", "climate-adaptive design"],
    "Balochistan": ["water availability", "heat resilience", "drought resilience", "drainage and flood protection", "asset protection", "emergency preparedness", "operational continuity", "climate-adaptive design"],
    "Islamabad Capital Territory": ["drainage and flood protection", "slope stability", "heat resilience", "asset protection", "emergency preparedness", "operational continuity", "climate-adaptive design"],
    "Gilgit-Baltistan": ["slope stability", "flood and GLOF risk screening", "water availability", "asset protection", "emergency preparedness", "operational continuity", "climate-adaptive design"],
    "Azad Jammu & Kashmir": ["slope stability", "drainage and flood protection", "landslide screening", "water availability", "asset protection", "emergency preparedness", "operational continuity", "climate-adaptive design"],
}

MOUNTAIN_PRIORITIES = {
    "Himalayas": ["slope stability", "landslide screening", "drainage and flood protection", "water availability", "asset protection", "emergency preparedness", "operational continuity"],
    "Karakoram": ["slope stability", "flood and GLOF risk screening", "water availability", "asset protection", "emergency preparedness", "operational continuity"],
    "Hindu Kush": ["slope stability", "landslide screening", "flood and GLOF risk screening", "water availability", "asset protection", "emergency preparedness"],
    "Sulaiman / Koh-e-Suleman": ["slope stability", "hill-torrent and flood drainage", "water availability", "asset protection", "emergency preparedness", "operational continuity"],
    "Spīn Ghar / Safed Koh": ["slope stability", "landslide screening", "drainage and flood protection", "water availability", "asset protection", "emergency preparedness"],
    "Kirthar": ["water availability", "drought resilience", "flash-flood drainage", "slope stability", "asset protection", "emergency preparedness"],
    "Salt Range": ["slope stability", "drainage and flood protection", "water availability", "asset protection", "emergency preparedness", "operational continuity"],
}

SECTOR_PRIORITIES = {
    "Agriculture": ["drought", "heat", "flood", "water availability", "crop resilience"],
    "Energy": ["heat", "water availability", "flood", "grid resilience", "cooling demand"],
    "Health": ["heat", "vector disease", "water-borne disease", "air quality", "health readiness"],
    "Transportation": ["flood", "extreme heat", "landslide", "asset resilience", "disruption"],
    "Water": ["drought", "flood", "water quality", "demand", "catchment resilience"],
}

SCREENING_DISCLAIMER = (
    "This screening is an early-stage decision-support exercise. Use the results to identify "
    "issues that may need further investigation. It does not replace an Environmental Impact "
    "Assessment (EIA), Initial Environmental Examination (IEE), engineering design, hydrological "
    "study, health assessment, disaster-risk assessment, or regulatory review."
)
