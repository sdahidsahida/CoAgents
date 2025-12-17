import pytest
from py_iztro import Astro


class TestPyIztro:
    """Test cases for the py-iztro Zi Wei Dou Shu library"""
    
    def test_astro_basic_creation(self):
        """Test basic Astro object creation"""
        astro = Astro()
        assert astro is not None
    
    def test_solar_date_chart(self):
        """Test chart creation with solar date"""
        astro = Astro()
        
        # Test with solar date
        result = astro.by_solar("2000-08-16", 2, "女")
        
        assert result is not None
        assert hasattr(result, 'gender')
        assert hasattr(result, 'solar_date')
        assert hasattr(result, 'lunar_date')
        assert hasattr(result, 'chinese_date')
        assert hasattr(result, 'soul')
        assert hasattr(result, 'body')
        
        # Check the values
        assert result.gender == "女"
        assert result.solar_date == "2000-08-16"
        assert result.soul is not None
        assert result.body is not None
        
        print(f"\nZi Wei Chart for {result.solar_date}:")
        print(f"Gender: {result.gender}")
        print(f"Solar Date: {result.solar_date}")
        print(f"Lunar Date: {result.lunar_date}")
        print(f"Chinese Date: {result.chinese_date}")
        print(f"Soul Palace: {result.soul}")
        print(f"Body Palace: {result.body}")
    
    def test_lunar_date_chart(self):
        """Test chart creation with lunar date"""
        astro = Astro()
        
        # Test with lunar date
        result = astro.by_lunar("2000-07-17", 2, "女", "寅")
        
        assert result is not None
        assert result.gender == "女"
        assert result.lunar_date is not None
        print(f"\nLunar date chart result: {result.lunar_date}")
    
    def test_different_dates(self):
        """Test chart creation with different dates"""
        astro = Astro()
        
        test_cases = [
            ("1990-05-15", 1, "男"),
            ("1988-12-25", 3, "女"),
            ("2024-02-29", 4, "男"),  # Leap year
            ("2010-10-10", 6, "女"),
        ]
        
        for date, hour, gender in test_cases:
            result = astro.by_solar(date, hour, gender)
            assert result is not None
            assert result.solar_date == date
            assert result.gender == gender
            assert result.soul is not None
    
    def test_palace_information(self):
        """Test palace information in the chart"""
        astro = Astro()
        result = astro.by_solar("2000-08-16", 2, "女")
        
        # Check if palace information is available
        assert hasattr(result, 'earthly_branch_of_soul_palace')
        assert hasattr(result, 'earthly_branch_of_body_palace')
        
        print(f"\nPalace Information:")
        print(f"Soul Palace Branch: {result.earthly_branch_of_soul_palace}")
        print(f"Body Palace Branch: {result.earthly_branch_of_body_palace}")
    
    def test_astrological_signs(self):
        """Test Western astrological signs"""
        astro = Astro()
        result = astro.by_solar("2000-08-16", 2, "女")
        
        assert hasattr(result, 'sign')
        assert hasattr(result, 'zodiac')
        
        print(f"\nAstrological Signs:")
        print(f"Western Sign: {result.sign}")
        print(f"Chinese Zodiac: {result.zodiac}")
    
    def test_time_information(self):
        """Test time-related information"""
        astro = Astro()
        result = astro.by_solar("2000-08-16", 2, "女")
        
        assert hasattr(result, 'time')
        assert hasattr(result, 'time_range')
        
        print(f"\nTime Information:")
        print(f"Time: {result.time}")
        print(f"Time Range: {result.time_range}")
    
    def test_five_elements(self):
        """Test five elements classification"""
        astro = Astro()
        result = astro.by_solar("2000-08-16", 2, "女")
        
        # Check if five elements info is available
        if hasattr(result, 'five_elements_class'):
            print(f"\nFive Elements Class: {result.five_elements_class}")
    
    def test_chart_json_export(self):
        """Test exporting chart to JSON"""
        astro = Astro()
        result = astro.by_solar("2000-08-16", 2, "女")
        
        # Test JSON export
        try:
            json_str = result.model_dump_json(by_alias=True, indent=2)
            assert json_str is not None
            assert len(json_str) > 0
            print(f"\nJSON export successful, length: {len(json_str)} characters")
        except Exception as e:
            print(f"JSON export failed: {e}")
            pytest.fail("JSON export should work for chart result")
    
    def test_invalid_date_handling(self):
        """Test handling of invalid dates"""
        astro = Astro()
        
        # Test with invalid date format
        try:
            astro.by_solar("invalid-date", 2, "女")
            assert False, "Should have raised an exception for invalid date"
        except Exception:
            assert True  # Expected to raise an exception
    
    def test_chart_consistency(self):
        """Test chart consistency for same inputs"""
        astro = Astro()
        
        # Create chart twice with same parameters
        result1 = astro.by_solar("2000-08-16", 2, "女")
        result2 = astro.by_solar("2000-08-16", 2, "女")
        
        # Check if results are consistent
        assert result1.soul == result2.soul
        assert result1.body == result2.body
        assert result1.chinese_date == result2.chinese_date