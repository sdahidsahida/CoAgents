#!/usr/bin/env python
"""
Isolated test to reproduce the 'int' object is not iterable error
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Add correct flatlib library path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart

def test_astrology_calculation():
    """Test the astrology calculation step by step"""
    
    # Create chart
    date_str = "2024/06/21"
    time_str = "12:00"
    datetime_obj = Datetime(date_str, time_str, '+00:00')
    pos = GeoPos("51n30", "0w07")
    chart = Chart(datetime_obj, pos)
    
    planets = [
        ("Sun", "太阳"),
        ("Moon", "月亮"),
        ("Mercury", "水星"),
        ("Venus", "金星"),
        ("Mars", "火星"),
        ("Jupiter", "木星"),
        ("Saturn", "土星"),
    ]
    
    # Try to get each planet
    for planet_id, planet_name in planets:
        try:
            planet = chart.get(planet_id)
            if planet:
                print(f"✓ {planet_name} ({planet_id}): sign={planet.sign}")
            else:
                print(f"✗ {planet_name} ({planet_id}): Not found")
        except Exception as e:
            print(f"✗ {planet_name} ({planet_id}): {type(e).__name__} - {e}")
            import traceback
            traceback.print_exc()
    
    # Now try with the three outer planets
    print("\n--- Testing outer planets ---")
    outer_planets = [
        ("Uranus", "天王星"),
        ("Neptune", "海王星"),
        ("Pluto", "冥王星")
    ]
    
    for planet_id, planet_name in outer_planets:
        try:
            planet = chart.get(planet_id)
            if planet:
                print(f"✓ {planet_name} ({planet_id}): sign={planet.sign}")
            else:
                print(f"✗ {planet_name} ({planet_id}): Not found")
        except Exception as e:
            print(f"✗ {planet_name} ({planet_id}): {type(e).__name__} - {e}")
            # Print full traceback
            import traceback
            traceback.print_exc()
            
            # Try to understand what's happening
            print(f"\nDebugging info for {planet_id}:")
            print(f"  chart.get method: {chart.get}")
            try:
                result = chart.get(planet_id)
                print(f"  chart.get returned: {result}")
                print(f"  Type of result: {type(result)}")
            except Exception as e2:
                print(f"  chart.get failed with: {e2}")
                
                # Check if the error happens inside chart.get
                import inspect
                try:
                    source = inspect.getsource(chart.get)
                    print(f"  Source of chart.get: {source[:200]}...")
                except:
                    pass

if __name__ == "__main__":
    test_astrology_calculation()