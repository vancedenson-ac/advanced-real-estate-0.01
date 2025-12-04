@echo off
REM Quick test runner script for Real Estate AI Platform (Windows)
REM Runs all tests with coverage and generates reports

echo 🧪 Running Real Estate AI Platform Test Suite...
echo.

REM Check if we're in the backend directory or root
if exist backend (
    set TEST_DIR=backend
) else (
    set TEST_DIR=.
)

REM Change to backend directory
cd /d %TEST_DIR%

REM Check if pytest is installed
where pytest >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing test dependencies...
    pip install -r requirements.txt
)

REM Run tests with coverage
echo 🔍 Running tests with coverage...
echo.

REM Run tests
pytest --cov=app --cov-report=html --cov-report=term --cov-report=term-missing --verbose --tb=short tests/

REM Check if tests passed
if errorlevel 1 (
    echo.
    echo ❌ Some tests failed. Check the output above for details.
    exit /b 1
) else (
    echo.
    echo ✅ All tests passed!
    echo.
    echo 📊 Coverage report generated in htmlcov/index.html
    echo    Open it with: start htmlcov/index.html
    echo.
)

pause

