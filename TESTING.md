# Testing Documentation

## Overview

This document provides comprehensive testing information for the Social Media Management Bot, including setup instructions, test execution procedures, and expected results.

## Table of Contents

1. [Test Architecture](#test-architecture)
2. [Setup Instructions](#setup-instructions)
3. [Running Tests](#running-tests)
4. [Integration Tests](#integration-tests)
5. [Test Results & Reporting](#test-results--reporting)
6. [Troubleshooting](#troubleshooting)

## Test Architecture

The Social Media Management Bot uses a comprehensive testing framework that includes:

### Test Types

- **Unit Tests**: Located in `backend/tests/` for individual component testing
- **Integration Tests**: Located in `tests/integration/` for end-to-end functionality testing
- **API Tests**: HTTP endpoint testing for all REST API functionality
- **Authentication Tests**: OAuth flows and security validation
- **Database Tests**: Data persistence and retrieval validation

### Test Framework

- **Primary Framework**: pytest with asyncio support
- **Test Organization**: Modular test suites by functionality
- **Mocking**: Comprehensive mocking for external API calls
- **Reporting**: HTML reports with coverage analysis

## Setup Instructions

### Prerequisites

Before running tests, ensure you have:

1. **Python 3.11+** installed
2. **Git** for repository access
3. **Virtual environment** (recommended)
4. **Backend dependencies** installed

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Bigcvl2212/Social_Media_Management_Bot.git
   cd Social_Media_Management_Bot
   ```

2. **Set up backend environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install additional test dependencies**:
   ```bash
   pip install pytest pytest-asyncio pytest-html pytest-cov
   ```

4. **Configure test environment**:
   ```bash
   cp .env.example .env
   # Edit .env with test configuration values
   ```

### Test Database Setup

For integration tests, the system uses an in-memory SQLite database:

```python
# Automatically configured in test fixtures
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

No additional database setup is required for testing.

## Running Tests

### Quick Start

Run all integration tests with the provided test runner:

```bash
# From project root
python run_integration_tests.py --verbose --html-report
```

### Test Runner Options

```bash
# Basic test run
python run_integration_tests.py

# Verbose output with HTML report
python run_integration_tests.py --verbose --html-report

# Run specific test suite
python run_integration_tests.py --suite authentication

# Run tests for specific platform
python run_integration_tests.py --platform instagram

# Include coverage analysis
python run_integration_tests.py --coverage
```

### Manual Test Execution

You can also run tests manually using pytest:

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_authentication.py -v

# Run with coverage
pytest tests/integration/ --cov=backend/app --cov-report=html

# Generate HTML report
pytest tests/integration/ --html=reports/test_report.html --self-contained-html
```

## Integration Tests

### Test Suites Overview

#### 1. Authentication Tests (`test_authentication.py`)

**Purpose**: Validates user management and authentication flows

**Test Cases**:
- User registration flow
- User login and token generation
- Protected route access
- Token refresh functionality
- User profile management
- Password change flow
- Account deactivation
- Role-based access control
- Team collaboration permissions

**Expected Results**:
- All authentication flows complete successfully
- JWT tokens are generated and validated correctly
- Permissions are enforced based on user roles
- Security measures prevent unauthorized access

#### 2. Social Account Linking Tests (`test_social_accounts.py`)

**Purpose**: Tests social media platform integration

**Test Cases**:
- Instagram account linking via OAuth
- Twitter account linking and authentication
- TikTok account connection flow
- Multiple platform management
- Account disconnection and cleanup
- Account reauthorization for expired tokens
- Account health checks and validation
- Permission scope validation
- Account synchronization status

**Expected Results**:
- OAuth flows complete successfully for all platforms
- Account tokens are securely stored and managed
- Platform-specific permissions are correctly validated
- Account health monitoring functions properly

#### 3. Content Posting Tests (`test_content_posting.py`)

**Purpose**: Validates content creation, posting, and scheduling

**Test Cases**:
- Instagram text post creation
- Instagram image post with media
- Twitter tweet posting
- TikTok video post upload
- Multi-platform simultaneous posting
- Single post scheduling
- Bulk content scheduling
- Recurring post schedules
- Schedule modification and cancellation
- Content library management
- Content template creation and usage
- Content analytics integration

**Expected Results**:
- Content posts successfully to all platforms
- Scheduling system works reliably
- Content management features function correctly
- Analytics integration captures post performance

#### 4. Analytics Tests (`test_analytics.py`)

**Purpose**: Tests analytics data retrieval and reporting

**Test Cases**:
- Instagram analytics data retrieval
- Twitter analytics and metrics
- TikTok performance analytics
- Cross-platform analytics comparison
- Dashboard overview generation
- Custom analytics report creation
- Automated AI insights generation
- Analytics export functionality
- Real-time monitoring and alerts

**Expected Results**:
- Analytics data is accurately retrieved from all platforms
- Reports generate comprehensive insights
- Dashboard provides meaningful overview
- Real-time monitoring detects performance changes

### Test Data and Mocking

All integration tests use comprehensive mocking to simulate:

- **Social Media API Responses**: Realistic platform API data
- **Authentication Flows**: OAuth and JWT token handling
- **Analytics Data**: Platform-specific metrics and insights
- **Content Posting**: Platform response formats
- **Error Scenarios**: Rate limiting, authentication failures

### Sample Test Execution

```bash
$ python run_integration_tests.py --verbose

    ╔═══════════════════════════════════════════════════════════════╗
    ║           Social Media Management Bot - Integration Tests      ║
    ║                                                               ║ 
    ║  Testing core functionality:                                  ║
    ║  • Authentication & User Management                           ║
    ║  • Social Media Account Linking                               ║
    ║  • Content Posting & Scheduling                               ║
    ║  • Analytics Retrieval & Reporting                            ║
    ╚═══════════════════════════════════════════════════════════════╝

🔍 Validating test environment...
✅ Environment validation passed
📦 Checking test dependencies...
✅ Core dependencies available
🧪 Running integration tests...

tests/integration/test_authentication.py::TestAuthentication::test_user_registration_flow ✓
tests/integration/test_authentication.py::TestAuthentication::test_user_login_flow ✓
tests/integration/test_authentication.py::TestAuthentication::test_protected_route_access ✓
... [additional test results] ...

✅ All tests passed!
📊 Test Summary
📋 Authentication & User Management
   Validates user registration, login, permissions
```

## Test Results & Reporting

### HTML Reports

When using `--html-report`, detailed HTML reports are generated in the `test_reports/` directory:

- **Test Results**: Pass/fail status for each test
- **Execution Time**: Performance metrics for test runs
- **Coverage Data**: Code coverage analysis
- **Error Details**: Detailed failure information

### Coverage Analysis

Use `--coverage` to generate coverage reports:

```bash
# Generate coverage report
python run_integration_tests.py --coverage

# View HTML coverage report
open htmlcov/index.html
```

### Expected Test Results

**All Tests Passing**: 
- Total tests: ~50+ integration tests
- Authentication: 8 test cases
- Social Accounts: 12 test cases  
- Content Posting: 15 test cases
- Analytics: 15 test cases

**Performance Expectations**:
- Test execution time: < 30 seconds
- Memory usage: < 100MB
- No external API calls (all mocked)

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure backend path is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

#### Dependency Issues
```bash
# Error: Missing pytest or other dependencies
# Solution: Install all required packages
pip install pytest pytest-asyncio pytest-html pytest-cov
```

#### Path Issues
```bash
# Error: Test files not found
# Solution: Run from project root directory
cd Social_Media_Management_Bot
python run_integration_tests.py
```

### Debug Mode

For detailed debugging, run tests with maximum verbosity:

```bash
pytest tests/integration/ -vvv -s --tb=long
```

### Environment Variables

Set these environment variables for enhanced testing:

```bash
export TESTING=true
export LOG_LEVEL=debug
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
```

### Platform-Specific Testing

Test individual platforms in isolation:

```bash
# Test only Instagram functionality
python run_integration_tests.py --platform instagram

# Test only authentication
python run_integration_tests.py --suite authentication
```

## Continuous Integration

For CI/CD integration, use:

```bash
# CI-friendly test execution
python run_integration_tests.py --verbose --html-report --coverage
```

Expected CI outcomes:
- All tests pass (exit code 0)
- Coverage > 80%
- No security vulnerabilities
- Performance within acceptable limits

---

**Note**: These integration tests use mocked external APIs to ensure reliable, fast execution without requiring actual social media platform credentials. For production testing with real APIs, see the separate API testing documentation.