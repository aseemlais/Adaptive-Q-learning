
import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    PROJECT_NAME = "SmartSupply-AI"
    VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/smartsupply.db")
    QLEARN_ALPHA = 0.1
    QLEARN_GAMMA = 0.95
    QLEARN_EPSILON = 1.0
    QLEARN_EPSILON_MIN = 0.05
    QLEARN_EPSILON_DECAY = 0.995
    QLEARN_EPISODES = 500
    FORECAST_ALPHA = 0.35
    REGIONS = ["North","South","East","West","Central","Northeast"]
    DISTRICTS = {
        "North":     ["Delhi","Lucknow","Chandigarh","Jaipur","Amritsar"],
        "South":     ["Chennai","Bangalore","Hyderabad","Kochi","Coimbatore"],
        "East":      ["Kolkata","Patna","Bhubaneswar","Ranchi","Dhanbad"],
        "West":      ["Mumbai","Pune","Ahmedabad","Surat","Nagpur"],
        "Central":   ["Bhopal","Indore","Raipur","Jabalpur","Gwalior"],
        "Northeast": ["Shillong","Imphal","Agartala","Aizawl","Kohima"],
    }
    SEASONS = {1:"Winter",2:"Winter",3:"Spring",4:"Spring",5:"Summer",6:"Monsoon",
               7:"Monsoon",8:"Monsoon",9:"Post-Monsoon",10:"Post-Monsoon",11:"Autumn",12:"Winter"}
    WEATHER_BY_REGION = {
        "North":     {"Summer":"Hot & Dry","Monsoon":"Heavy Rain","Winter":"Cold & Foggy","Spring":"Warm","Post-Monsoon":"Pleasant","Autumn":"Cool"},
        "South":     {"Summer":"Hot & Humid","Monsoon":"Moderate Rain","Winter":"Mild","Spring":"Warm & Dry","Post-Monsoon":"Warm","Autumn":"Mild"},
        "East":      {"Summer":"Hot & Humid","Monsoon":"Very Heavy Rain","Winter":"Cool","Spring":"Warm & Humid","Post-Monsoon":"Warm","Autumn":"Cool & Humid"},
        "West":      {"Summer":"Hot & Dry","Monsoon":"Moderate Rain","Winter":"Pleasant","Spring":"Warm","Post-Monsoon":"Warm","Autumn":"Pleasant"},
        "Central":   {"Summer":"Extreme Heat","Monsoon":"Moderate Rain","Winter":"Cool","Spring":"Hot","Post-Monsoon":"Warm","Autumn":"Cool"},
        "Northeast": {"Summer":"Warm & Humid","Monsoon":"Extremely Heavy Rain","Winter":"Very Cold","Spring":"Mild","Post-Monsoon":"Cool","Autumn":"Cold"},
    }
    SEASONAL_DISEASES = {
        "Winter":["Influenza","Pneumonia","Bronchitis","Common Cold"],
        "Spring":["Allergic Rhinitis","Conjunctivitis","Asthma"],
        "Summer":["Diarrhea","Typhoid","Heat Stroke","Food Poisoning"],
        "Monsoon":["Malaria","Dengue","Cholera","Leptospirosis","Typhoid"],
        "Post-Monsoon":["Dengue","Chikungunya","Viral Fever","Malaria"],
        "Autumn":["Influenza","Viral Fever","Asthma"],
    }
    DISEASE_MEDICINE_MAP = {
        "Influenza":"Antipyretics","Pneumonia":"Antibiotics","Bronchitis":"Bronchodilators",
        "Common Cold":"Antihistamines","Allergic Rhinitis":"Antihistamines","Conjunctivitis":"Eye Drops",
        "Asthma":"Bronchodilators","Diarrhea":"ORS & Antidiarrheals","Typhoid":"Antibiotics",
        "Heat Stroke":"IV Fluids","Food Poisoning":"ORS & Antidiarrheals","Malaria":"Antimalarials",
        "Dengue":"Antipyretics","Cholera":"ORS & Antidiarrheals","Leptospirosis":"Antibiotics",
        "Chikungunya":"Antipyretics","Viral Fever":"Antipyretics",
    }
    MEDICINE_CATEGORIES = [
        "Antipyretics","Antibiotics","Bronchodilators","Antihistamines",
        "ORS & Antidiarrheals","Antimalarials","IV Fluids","Eye Drops",
        "Antidiabetics","Cardiovascular","Vitamins & Supplements","Analgesics",
    ]
    REGION_DEMAND_MULTIPLIERS = {
        "North":1.3,"South":1.2,"East":0.9,"West":1.4,"Central":0.8,"Northeast":0.6
    }

settings = Settings()
