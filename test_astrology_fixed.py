#!/usr/bin/env python
"""
Test the fixed astrology tool
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Test the fixed astrology tool
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
        
        # Check if we have the outer planets
        outer_planets = ["天王星", "海王星", "冥王星"]
        for planet_name in outer_planets:
            if planet_name in planets:
                info = planets[planet_name]
                print(f"  ✓ {planet_name}: {info.get('sign')} at {info.get('position')}")
            else:
                print(f"  ✗ {planet_name}: Not found")
    else:
        print(f"✗ Astrology calculation failed: {result.get('error')}")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ Error during calculation: {e}")
    import traceback
    traceback.print_exc()