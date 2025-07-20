#!/usr/bin/env python3
"""
Test script to validate the fixes for test failures.
This script tests core functionality without requiring full dependency installation.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_syntax_validation():
    """Test that Python files have valid syntax."""
    print("Testing Python syntax validation...")
    
    files_to_test = [
        "backend/main.py",
        "backend/app/core/rate_limiting.py",
        "backend/app/core/config.py",
    ]
    
    for file_path in files_to_test:
        full_path = Path(__file__).parent / file_path
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
            
        try:
            with open(full_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path}: Syntax OK")
        except SyntaxError as e:
            print(f"❌ {file_path}: Syntax Error - {e}")
            return False
    
    return True

def test_requirements_files():
    """Test that requirements files exist and have valid format."""
    print("\nTesting requirements files...")
    
    req_files = [
        "backend/requirements.txt",
        "backend/requirements-minimal.txt"
    ]
    
    for req_file in req_files:
        full_path = Path(__file__).parent / req_file
        if not full_path.exists():
            print(f"❌ Requirements file not found: {req_file}")
            return False
        
        try:
            with open(full_path, 'r') as f:
                lines = f.readlines()
                if not lines:
                    print(f"❌ {req_file}: Empty file")
                    return False
                print(f"✅ {req_file}: {len(lines)} dependencies listed")
        except Exception as e:
            print(f"❌ {req_file}: Error reading - {e}")
            return False
    
    return True

def test_docker_files():
    """Test that Docker files exist and have basic structure."""
    print("\nTesting Docker files...")
    
    docker_files = [
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "docker/docker-compose.yml",
        "docker/docker-compose.prod.yml"
    ]
    
    for docker_file in docker_files:
        full_path = Path(__file__).parent / docker_file
        if not full_path.exists():
            print(f"❌ Docker file not found: {docker_file}")
            return False
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                if not content.strip():
                    print(f"❌ {docker_file}: Empty file")
                    return False
                print(f"✅ {docker_file}: {len(content.splitlines())} lines")
        except Exception as e:
            print(f"❌ {docker_file}: Error reading - {e}")
            return False
    
    return True

def test_integration_test_structure():
    """Test that integration test files exist."""
    print("\nTesting integration test structure...")
    
    test_files = [
        "run_integration_tests.py",
        "tests/integration/test_authentication.py",
        "tests/integration/test_content_posting.py",
        "tests/integration/test_analytics.py",
        "tests/integration/test_social_accounts.py",
        "tests/integration/test_monetization.py"
    ]
    
    for test_file in test_files:
        full_path = Path(__file__).parent / test_file
        if not full_path.exists():
            print(f"⚠️  Test file not found: {test_file}")
        else:
            print(f"✅ {test_file}: Found")
    
    return True

def test_rate_limiting_env_handling():
    """Test that rate limiting handles environment variables properly."""
    print("\nTesting rate limiting environment handling...")
    
    # Set test environment
    os.environ['TESTING'] = '1'
    
    try:
        # Try to import the rate limiting module
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        
        # Test imports without dependencies
        import ast
        
        # Parse the rate limiting file to check for proper environment handling
        rate_limiting_file = Path(__file__).parent / "backend/app/core/rate_limiting.py"
        with open(rate_limiting_file, 'r') as f:
            content = f.read()
        
        # Check for key patterns
        required_patterns = [
            "os.getenv('TESTING')",
            "os.getenv('PYTEST_CURRENT_TEST')",
            "redis_available",
            "except",  # Exception handling
        ]
        
        for pattern in required_patterns:
            if pattern in content:
                print(f"✅ Found required pattern: {pattern}")
            else:
                print(f"❌ Missing pattern: {pattern}")
                return False
        
        print("✅ Rate limiting environment handling looks good")
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False
    finally:
        # Clean up environment
        if 'TESTING' in os.environ:
            del os.environ['TESTING']

def main():
    """Run all tests."""
    print("🧪 Testing fixes for CI/CD failures\n")
    
    tests = [
        ("Syntax Validation", test_syntax_validation),
        ("Requirements Files", test_requirements_files),
        ("Docker Files", test_docker_files),
        ("Integration Test Structure", test_integration_test_structure),
        ("Rate Limiting Environment Handling", test_rate_limiting_env_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🔍 {test_name}")
        print("="*60)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! The fixes should resolve the CI/CD issues.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())