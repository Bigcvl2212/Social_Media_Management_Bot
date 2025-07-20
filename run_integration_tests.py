#!/usr/bin/env python3
"""
Integration Test Runner for Social Media Management Bot

This script runs all integration tests and generates a comprehensive test report.
It validates the core functionality of the Social Media Management Bot including:
- Authentication and user management
- Social media account linking
- Content posting and scheduling
- Analytics retrieval and reporting

Usage:
    python run_integration_tests.py [options]
    
Options:
    --verbose, -v     Enable verbose output
    --html-report     Generate HTML test report
    --coverage        Include coverage analysis
    --platform PLATFORM  Run tests for specific platform only
    --suite SUITE    Run specific test suite only
    
Examples:
    python run_integration_tests.py --verbose --html-report
    python run_integration_tests.py --suite authentication
    python run_integration_tests.py --platform instagram --coverage
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

def print_banner():
    """Print the test runner banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║           Social Media Management Bot - Integration Tests      ║
    ║                                                               ║ 
    ║  Testing core functionality:                                  ║
    ║  • Authentication & User Management                           ║
    ║  • Social Media Account Linking                               ║
    ║  • Content Posting & Scheduling                               ║
    ║  • Analytics Retrieval & Reporting                            ║
    ║  • Monetization & Brand Collaboration                         ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def validate_environment():
    """Validate that the test environment is properly set up."""
    print("🔍 Validating test environment...")
    
    # Check if required directories exist
    required_dirs = [
        project_root / "tests" / "integration",
        project_root / "backend" / "app",
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"❌ Required directory not found: {dir_path}")
            return False
    
    # Check if test files exist
    test_files = [
        "test_authentication.py",
        "test_social_accounts.py", 
        "test_content_posting.py",
        "test_analytics.py",
        "test_monetization.py"
    ]
    
    integration_dir = project_root / "tests" / "integration"
    missing_files = []
    for test_file in test_files:
        if not (integration_dir / test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"⚠️  Some test files not found: {', '.join(missing_files)}")
        print("✅ Environment validation passed (with warnings)")
    else:
        print("✅ Environment validation passed")
    
    return True

def install_dependencies():
    """Install required dependencies for testing."""
    print("📦 Checking test dependencies...")
    
    try:
        import pytest
        import asyncio
        print("✅ Core dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"], check=True)

def run_test_suite(suite_name=None, platform=None, verbose=False, html_report=False, coverage=False):
    """Run the integration test suite."""
    print(f"🧪 Running integration tests...")
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test directory
    integration_dir = project_root / "tests" / "integration"
    
    if suite_name:
        # Run specific test suite
        test_file_map = {
            "authentication": "test_authentication.py",
            "social_accounts": "test_social_accounts.py",
            "content": "test_content_posting.py", 
            "analytics": "test_analytics.py",
            "monetization": "test_monetization.py"
        }
        
        if suite_name in test_file_map:
            cmd.append(str(integration_dir / test_file_map[suite_name]))
        else:
            print(f"❌ Unknown test suite: {suite_name}")
            print(f"Available suites: {', '.join(test_file_map.keys())}")
            return False
    else:
        # Run all integration tests
        cmd.append(str(integration_dir))
    
    # Add pytest options
    if verbose:
        cmd.extend(["-v", "-s"])
    
    if html_report:
        reports_dir = project_root / "test_reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = reports_dir / f"integration_test_report_{timestamp}.html"
        cmd.extend(["--html", str(html_file), "--self-contained-html"])
    
    if coverage:
        cmd.extend(["--cov=backend/app", "--cov-report=html", "--cov-report=term"])
    
    # Add platform filter if specified
    if platform:
        cmd.extend(["-k", platform])
    
    # Run tests
    start_time = time.time()
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 80)
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        execution_time = time.time() - start_time
        
        print("=" * 80)
        print(f"⏱️  Test execution completed in {execution_time:.2f} seconds")
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print(f"❌ Tests failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def generate_test_summary():
    """Generate a summary of test results and coverage."""
    print("\n📊 Test Summary")
    print("=" * 50)
    
    test_suites = [
        ("Authentication & User Management", "Validates user registration, login, permissions"),
        ("Social Media Account Linking", "Tests OAuth flows and account management"),
        ("Content Posting & Scheduling", "Verifies posting and scheduling functionality"),
        ("Analytics Retrieval", "Tests analytics data collection and reporting"),
        ("Monetization & Brand Collaboration", "Tests brand profiles, campaigns, and affiliate marketing")
    ]
    
    for suite_name, description in test_suites:
        print(f"📋 {suite_name}")
        print(f"   {description}")
        print()
    
    print("🎯 Key Test Areas:")
    print("   • User authentication and authorization")
    print("   • Multi-platform social media integration")
    print("   • Content management and automation")
    print("   • Real-time analytics and insights")
    print("   • Brand collaboration marketplace")
    print("   • Campaign management and tracking")
    print("   • Affiliate marketing and reporting")
    print("   • Cross-platform functionality")
    print("   • Error handling and edge cases")

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run integration tests for Social Media Management Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML test report")
    parser.add_argument("--coverage", action="store_true", help="Include coverage analysis")
    parser.add_argument("--platform", help="Run tests for specific platform only")
    parser.add_argument("--suite", help="Run specific test suite only", 
                        choices=["authentication", "social_accounts", "content", "analytics", "monetization"])
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Validate environment
    if not validate_environment():
        print("❌ Environment validation failed. Please check your setup.")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Run tests
    success = run_test_suite(
        suite_name=args.suite,
        platform=args.platform,
        verbose=args.verbose,
        html_report=args.html_report,
        coverage=args.coverage
    )
    
    # Generate summary
    generate_test_summary()
    
    if args.html_report:
        print(f"\n📄 HTML report generated in: {project_root}/test_reports/")
    
    if success:
        print("\n🎉 Integration testing completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()