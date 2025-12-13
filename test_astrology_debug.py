#!/usr/bin/env python
"""
Debug script to find the exact source of the 'int' object is not iterable error
"""

import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Test astrology tool directly
try:
    from framework.tools.astrology_tool import calculate_astrology_chart
    print("✓ Successfully imported astrology_tool")
    
    # Test with simple parameters
    print("\nTesting astrology calculation...")
    result = calculate_astrology_chart(
        year=2024,
        month=6,
        day=21,
        hour=12,
        minute=0,
        location={"lat": "51n30", "lon": "0w07"}  # London
    )
    
    if result.get("success"):
        print("✓ Astrology calculation succeeded")
        planets = result.get("planets", {})
        print(f"Number of planets: {len(planets)}")
        for name, info in planets.items():
            print(f"  {name}: {info.get('sign')}")
    else:
        print(f"✗ Astrology calculation failed: {result.get('error')}")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"✗ Error during calculation: {e}")
    traceback.print_exc()

# Test importing flatlib directly
print("\n" + "="*60)
print("Testing flatlib import...")
try:
    # Add flatlib library path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'framework/lib/flatlib'))
    
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib.chart import Chart
    print("✓ Successfully imported flatlib components")
    
    # Try creating a chart
    date_str = "2024/06/21"
    time_str = "12:00"
    datetime_obj = Datetime(date_str, time_str, '+00:00')
    pos = GeoPos("51n30", "0w07")
    chart = Chart(datetime_obj, pos)
    print("✓ Successfully created chart")
    
    # Test getting planets one by one
    planets_to_test = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    for planet_id in planets_to_test:
        try:
            planet = chart.get(planet_id)
            if planet:
                print(f"✓ {planet_id}: sign={planet.sign}, lon={planet.lon}")
            else:
                print(f"✗ {planet_id}: Not found")
        except Exception as e:
            print(f"✗ {planet_id}: Error - {e}")
            
except ImportError as e:
    print(f"✗ Failed to import flatlib: {e}")
    print("The flatlib library might not be installed or the path might be incorrect")
except Exception as e:
    print(f"✗ Error with flatlib: {e}")
    traceback.print_exc()