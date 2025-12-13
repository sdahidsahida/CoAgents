#!/usr/bin/env python
"""
Test with full traceback to see exactly where the error occurs
"""

import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from framework.tools.astrology_tool import calculate_astrology_chart
    
    # Test with simple parameters
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
        for name, info in list(planets.items())[:5]:
            print(f"  {name}: {info.get('sign')}")
    else:
        print(f"✗ Astrology calculation failed: {result.get('error')}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()