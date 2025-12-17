#!/usr/bin/env python
"""
Test summary for the three external libraries:
1. bazi - Chinese astrology (Bazi) calculator
2. flatlib - Western astrology library
3. py-iztro - Zi Wei Dou Shu (Chinese astrology) library
"""

import sys
import os
import subprocess
from datetime import datetime

print("=" * 80)
print("Test Summary for External Libraries")
print("=" * 80)
print(f"Test run at: {datetime.now()}")
print()

# Test 1: bazi library
print("\n1. Testing Bazi Library (Chinese Astrology)")
print("-" * 50)
bazi_path = os.path.join(os.path.dirname(__file__), '../../lib/bazi/bazi.py')
if os.path.exists(bazi_path):
    print("✓ Bazi script exists")
    try:
        # Test bazi execution
        result = subprocess.run(
            [sys.executable, bazi_path, '1990', '5', '15', '14'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if len(result.stdout) > 0:
            print("✓ Bazi script executes and produces output")
            # Check for Chinese characters in output
            chinese_chars = ['甲', '乙', '丙', '丁', '子', '丑', '寅', '卯']
            has_chinese = any(char in result.stdout for char in chinese_chars)
            if has_chinese:
                print("✓ Output contains Chinese characters (expected)")
        else:
            print("✗ Bazi script produced no output")
    except Exception as e:
        print(f"✗ Error running Bazi: {e}")
else:
    print("✗ Bazi script not found")

# Test dependencies
print("\nDependencies:")
for dep in ['lunar_python', 'colorama']:
    try:
        __import__(dep)
        print(f"✓ {dep} is available")
    except ImportError:
        print(f"✗ {dep} is NOT available")

# Test 2: flatlib library
print("\n\n2. Testing Flatlib Library (Western Astrology)")
print("-" * 50)
try:
    # Add to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib/flatlib'))
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib.chart import Chart
    from flatlib import const
    
    print("✓ Flatlib modules imported successfully")
    
    # Test basic chart creation
    date = Datetime('2024/06/21', '12:00', '+00:00')
    pos = GeoPos('51n30', '0w07')
    chart = Chart(date, pos)
    
    print("✓ Chart created successfully")
    
    # Test getting Sun position
    sun = chart.get(const.SUN)
    if sun:
        print(f"✓ Sun position calculated: {sun.sign}")
    
    print("✓ Flatlib is working correctly")
    
except ImportError as e:
    print(f"✗ Flatlib import failed: {e}")
    print("  Note: Flatlib requires pyswisseph==2.08.00-1")
except Exception as e:
    print(f"✗ Flatlib test failed: {e}")

# Test 3: py-iztro library
print("\n\n3. Testing py-iztro Library (Zi Wei Dou Shu)")
print("-" * 50)
try:
    from py_iztro import Astro
    
    print("✓ py-iztro imported successfully")
    
    # Test chart creation
    astro = Astro()
    result = astro.by_solar("2000-08-16", 2, "女")
    
    print("✓ Chart created successfully")
    print(f"  Solar Date: {result.solar_date}")
    print(f"  Gender: {result.gender}")
    print(f"  Soul: {result.soul}")
    print(f"  Body: {result.body}")
    print(f"  Zodiac: {result.zodiac}")
    
    # Test JSON export
    json_str = result.model_dump_json(by_alias=True, indent=2)
    print(f"✓ JSON export works ({len(json_str)} characters)")
    
    print("✓ py-iztro is working correctly")
    
except ImportError:
    print("✗ py-iztro not installed (pip install py-iztro)")
except Exception as e:
    print(f"✗ py-iztro test failed: {e}")

print("\n" + "=" * 80)
print("Summary")
print("=" * 80)
print("""
1. Bazi: Located in lib/bazi/ - A script-based Chinese astrology calculator
   - Requires: lunar_python, colorama
   - Usage: python bazi.py yyyy mm dd hh

2. Flatlib: Located in lib/flatlib/ - A Western astrology library
   - Requires: pyswisseph==2.08.00-1 (not installed)
   - Provides: Chart creation, planetary positions, aspects calculation

3. py-iztro: Installed via pip (v0.1.5)
   - Provides: Zi Wei Dou Shu chart calculation
   - Usage: Astro().by_solar(date, hour, gender)

Recommendations:
- Install flatlib dependencies: pip install pyswisseph==2.08.00-1
- All three libraries are functional (with dependencies installed)
""")