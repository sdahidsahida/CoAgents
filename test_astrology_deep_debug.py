#!/usr/bin/env python
"""
Deep debug script to understand the chart.get() method behavior
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Add flatlib library path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'framework/lib/flatlib'))

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

# Create chart
date_str = "2024/06/21"
time_str = "12:00"
datetime_obj = Datetime(date_str, time_str, '+00:00')
pos = GeoPos("51n30", "0w07")
chart = Chart(datetime_obj, pos)

print("Chart object created successfully")
print(f"Chart type: {type(chart)}")

# Check available objects in const
print("\nChecking const module for planet constants...")
planet_consts = [attr for attr in dir(const) if attr.upper() == attr and not attr.startswith('_')]
print(f"Available constants: {planet_consts[:20]}...")  # Show first 20

# Try different approaches to get Uranus
print("\n" + "="*60)
print("Testing different ways to get Uranus...")

# Method 1: Direct string
try:
    result = chart.get("Uranus")
    print(f"✓ chart.get('Uranus'): {result}")
except Exception as e:
    print(f"✗ chart.get('Uranus'): {type(e).__name__} - {e}")

# Method 2: Check if it's in const
if hasattr(const, 'URANUS'):
    print(f"Found URANUS in const: {const.URANUS}")
    try:
        result = chart.get(const.URANUS)
        print(f"✓ chart.get(const.URANUS): {result}")
    except Exception as e:
        print(f"✗ chart.get(const.URANUS): {type(e).__name__} - {e}")
else:
    print("URANUS not found in const")

# Method 3: Check what chart.get actually expects
print("\n" + "="*60)
print("Investigating chart.get method...")

# Test with a working planet
sun = chart.get("Sun")
if sun:
    print(f"Sun object: {sun}")
    print(f"Sun object type: {type(sun)}")
    print(f"Sun attributes: {[attr for attr in dir(sun) if not attr.startswith('_')]}")

# Try to iterate over something that might be the issue
print("\n" + "="*60)
print("Testing potential iteration issues...")

# Check if any planet properties might be causing the iteration error
for planet_name in ["Sun", "Uranus"]:
    print(f"\nTesting {planet_name}:")
    try:
        planet = chart.get(planet_name)
        if planet:
            print(f"  Got planet object")
            # Test accessing properties
            if hasattr(planet, 'sign'):
                print(f"  Sign: {planet.sign}")
            if hasattr(planet, 'lon'):
                print(f"  Longitude: {planet.lon}")
                # Check if longitude is iterable when it shouldn't be
                try:
                    for x in planet.lon:
                        print(f"    Unexpected iteration over lon: {x}")
                except TypeError:
                    print(f"  Longitude is not iterable (expected)")
    except Exception as e:
        print(f"  Error: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()