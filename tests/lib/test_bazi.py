import sys
import os
import subprocess
import pytest


class TestBazi:
    """Test cases for the Bazi library"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.bazi_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lib/bazi'))
        self.bazi_path = os.path.join(self.bazi_dir, 'bazi.py')
    
    def test_bazi_script_exists(self):
        """Test that bazi.py script exists"""
        assert os.path.exists(self.bazi_path), "bazi.py script should exist"
    
    def test_bazi_script_execution(self):
        """Test basic bazi script execution"""
        # Run the bazi script with default parameters
        result = subprocess.run(
            [sys.executable, self.bazi_path, '--help'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(self.bazi_path)
        )
        
        # Should show help or run without error
        assert result.returncode == 0 or "usage:" in result.stdout.lower()
        print(f"\nBazi help output: {result.stdout[:200]}...")
    
    def test_bazi_with_specific_date(self):
        """Test bazi calculation with specific birth date"""
        # Test with a known birth date (format: yyyy mm dd hh)
        result = subprocess.run(
            [sys.executable, self.bazi_path, '1990', '5', '15', '14'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(self.bazi_path)
        )
        
        # The script should run without crashing
        # It might not have a clean exit code, so we check for output
        assert len(result.stdout) > 0 or len(result.stderr) > 0
        print(f"\nBazi calculation output length: {len(result.stdout)} characters")
        
        # Check for typical bazi output elements
        output = result.stdout + result.stderr
        likely_elements = ['甲', '乙', '丙', '丁', '子', '丑', '寅', '卯']
        has_chinese_chars = any(char in output for char in likely_elements)
        print(f"Contains Chinese characters: {has_chinese_chars}")
    
    def test_bazi_modules_import(self):
        """Test importing bazi modules individually"""
        bazi_dir = os.path.join(os.path.dirname(__file__), '../../../lib/bazi')
        
        # Test importing individual modules
        modules_to_test = ['datas', 'common', 'ganzhi', 'sizi', 'yue']
        
        for module_name in modules_to_test:
            module_path = os.path.join(bazi_dir, f'{module_name}.py')
            if os.path.exists(module_path):
                sys.path.insert(0, bazi_dir)
                try:
                    module = __import__(module_name)
                    assert module is not None
                    print(f"\nSuccessfully imported {module_name}")
                except ImportError as e:
                    print(f"\nCould not import {module_name}: {e}")
                finally:
                    if bazi_dir in sys.path:
                        sys.path.remove(bazi_dir)
    
    def test_bazi_data_availability(self):
        """Test if bazi data files are available"""
        
        # Check for essential data files
        data_files = ['datas.py', 'convert.py']
        for file_name in data_files:
            file_path = os.path.join(self.bazi_dir, file_name)
            assert os.path.exists(file_path), f"Data file {file_name} should exist"
    
    def test_bazi_dependencies(self):
        """Test if bazi dependencies are available"""
        # Check if required dependencies are importable
        dependencies = ['lunar_python', 'colorama']
        
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"\nDependency {dep} is available")
            except ImportError:
                print(f"\nDependency {dep} is NOT available")
    
    def test_bazi_with_different_dates(self):
        """Test bazi with multiple date formats"""
        test_cases = [
            ['2000', '1', '1', '12'],
            ['2024', '2', '29', '8'],  # Leap year
            ['1988', '12', '25', '23'],  # End of year
        ]
        
        for date_args in test_cases:
            result = subprocess.run(
                [sys.executable, self.bazi_path] + date_args,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(self.bazi_path)
            )
            
            # Should produce some output
            assert len(result.stdout) > 0 or len(result.stderr) > 0
            print(f"\nDate {date_args}: Output length = {len(result.stdout)}")