import sys
import os
import pytest
from datetime import datetime

# Add the lib directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../lib/flatlib'))

# Import flatlib modules
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const


class TestFlatlib:
    """Test cases for the Flatlib astrology library"""
    
    def test_flatlib_basic_chart_creation(self):
        """Test basic chart creation"""
        # Create a date and time
        date = Datetime('2024/01/01', '12:00', '+00:00')
        
        # Create a geographic position (London)
        pos = GeoPos('51n30', '0w07')
        
        # Create chart
        chart = Chart(date, pos)
        
        assert chart is not None
        assert chart.date == date
        assert chart.pos == pos
    
    def test_flatlib_sun_position(self):
        """Test getting Sun's position"""
        date = Datetime('2024/06/21', '12:00', '+00:00')  # Summer solstice
        pos = GeoPos('0n0', '0e0')  # Equator
        
        chart = Chart(date, pos)
        sun = chart.get(const.SUN)
        
        assert sun is not None
        assert hasattr(sun, 'sign')
        assert hasattr(sun, 'lon')
        # Sun should be in Cancer around summer solstice
        print(f"\nSun position on {date}: {sun}")
    
    def test_flatlib_moon_position(self):
        """Test getting Moon's position"""
        date = Datetime('2024/01/01', '12:00', '+00:00')
        pos = GeoPos('40n42', '74w00')  # New York
        
        chart = Chart(date, pos)
        moon = chart.get(const.MOON)
        
        assert moon is not None
        assert hasattr(moon, 'sign')
        assert hasattr(moon, 'lon')
        print(f"Moon position: {moon}")
    
    def test_flatlib_ascendant(self):
        """Test getting Ascendant"""
        date = Datetime('2024/03/21', '06:00', '+00:00')  # Spring equinox, sunrise
        pos = GeoPos('0n0', '0e0')
        
        chart = Chart(date, pos)
        asc = chart.get(const.ASC)
        
        assert asc is not None
        assert hasattr(asc, 'sign')
        assert hasattr(asc, 'lon')
        print(f"Ascendant: {asc}")
    
    def test_flatlib_planetary_aspects(self):
        """Test planetary aspects"""
        date = Datetime('2024/01/01', '12:00', '+00:00')
        pos = GeoPos('51n30', '0w07')
        
        chart = Chart(date, pos)
        
        # Get Sun and Moon
        sun = chart.get(const.SUN)
        moon = chart.get(const.MOON)
        
        # Check if there are aspects between them
        from flatlib.aspects import getAspect
        
        aspect = getAspect(sun, moon, 0)  # 0 degree orb
        print(f"Sun-Moon aspect: {aspect}")
    
    def test_flatlib_houses(self):
        """Test house calculation"""
        date = Datetime('2024/01/01', '12:00', '+00:00')
        pos = GeoPos('40n42', '74w00')  # New York
        
        chart = Chart(date, pos)
        
        # Get house positions
        houses = []
        for i in range(1, 13):
            house_id = getattr(const, f'HOUSE{i}', None)
            if house_id:
                house = chart.get(house_id)
                if house:
                    houses.append(house)
        
        assert len(houses) > 0
        print(f"\nNumber of houses calculated: {len(houses)}")
        for i, house in enumerate(houses[:4]):  # Print first 4 houses
            print(f"House {i+1}: {house}")
    
    def test_flatlib_angles(self):
        """Test angle calculations"""
        from flatlib.angle import Angle
        
        # Test angle creation
        angle1 = Angle(90)
        angle2 = Angle(180)
        
        assert angle1.deg == 90
        assert angle2.deg == 180
        
        # Test angle operations
        assert angle1 != angle2
        
        # Test angle normalization
        angle3 = Angle(370)  # Should normalize to 10 degrees
        assert angle3.deg == 10
    
    def test_flatlib_multiple_locations(self):
        """Test chart calculations for different locations"""
        date = Datetime('2024/06/21', '12:00', '+00:00')
        
        locations = [
            ('51n30', '0w07', 'London'),
            ('40n42', '74w00', 'New York'),
            ('35n41', '139e41', 'Tokyo'),
            ('-33s52', '151e13', 'Sydney'),
        ]
        
        charts = []
        for lat, lon, name in locations:
            pos = GeoPos(lat, lon)
            chart = Chart(date, pos)
            charts.append((name, chart))
            
            sun = chart.get(const.SUN)
            assert sun is not None
            print(f"\n{name} - Sun: {sun}")
        
        assert len(charts) == 4