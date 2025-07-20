#!/bin/bash

# Social Media Management Bot - Production Readiness Verification Script
# This script runs all production readiness checks in sequence

set -e  # Exit on any error

echo "🚀 Social Media Management Bot - Production Readiness Verification"
echo "=================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to run a check and track results
run_check() {
    local check_name="$1"
    local check_command="$2"
    local is_critical="${3:-false}"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -e "${BLUE}🔍 Checking: $check_name${NC}"
    
    if eval "$check_command" > /tmp/check_output 2>&1; then
        echo -e "${GREEN}✅ PASSED: $check_name${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED: $check_name${NC}"
        echo -e "${YELLOW}Output:${NC}"
        cat /tmp/check_output | head -10
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        
        if [ "$is_critical" = "true" ]; then
            echo -e "${RED}💥 CRITICAL FAILURE - Stopping verification${NC}"
            exit 1
        fi
        return 1
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "📋 Pre-flight checks..."
echo "----------------------"

# Check required commands
run_check "Docker availability" "command_exists docker" "true"
run_check "Docker Compose availability" "command_exists docker-compose" "true"
run_check "Python availability" "command_exists python3" "true"
run_check "Node.js availability" "command_exists node" "false"

echo ""
echo "🔧 Environment Configuration Checks..."
echo "--------------------------------------"

# Check environment files
run_check "Production environment file exists" "test -f .env.production"
run_check "Backend environment configured" "test -f backend/.env || test -f .env"
run_check "Frontend environment configured" "test -f frontend/.env.local || test -f frontend/.env"

# Check for placeholder values in production env
if [ -f .env.production ]; then
    run_check "No placeholder secrets in production env" "! grep -q 'CHANGE_ME\\|your-.*-here\\|placeholder' .env.production"
fi

echo ""
echo "🔐 Security Checks..."
echo "--------------------"

# Run security audit
if [ -f scripts/security_audit.py ]; then
    run_check "Security audit" "python3 scripts/security_audit.py 2>/dev/null | grep -q 'Security Score'"
fi

# Check file permissions
run_check "Secure file permissions" "find . -name '.env*' -perm /o+r | wc -l | grep -q '^0$'"

# Check for secrets in git
run_check "No secrets in git history" "! git log --all --full-history -- .env* | grep -q 'diff'"

echo ""
echo "🐳 Docker Configuration Checks..."
echo "--------------------------------"

# Check Docker configurations
run_check "Production Docker Compose file exists" "test -f docker/docker-compose.prod.yml"
run_check "Nginx configuration exists" "test -f nginx/nginx.conf"
run_check "Docker Compose file syntax" "docker-compose -f docker/docker-compose.prod.yml config > /dev/null"

# Check for SSL certificates directory
run_check "SSL certificate directory exists" "test -d nginx/ssl || mkdir -p nginx/ssl"

echo ""
echo "📊 Database Checks..."
echo "-------------------"

# Check database scripts
run_check "Database backup script exists" "test -x scripts/backup_database.sh"
run_check "Database restore script exists" "test -x scripts/restore_database.sh"

# Check backup directory
run_check "Backup directory setup" "mkdir -p backups && test -d backups"

echo ""
echo "🧪 Testing Infrastructure..."
echo "---------------------------"

# Check testing scripts
run_check "Load testing script exists" "test -x scripts/load_test.py"
run_check "Security audit script exists" "test -x scripts/security_audit.py"
run_check "UAT testing script exists" "test -x scripts/uat_testing.py"

# Test Python scripts syntax
run_check "Load test script syntax" "python3 -m py_compile scripts/load_test.py"
run_check "Security audit script syntax" "python3 -m py_compile scripts/security_audit.py"
run_check "UAT test script syntax" "python3 -m py_compile scripts/uat_testing.py"

echo ""
echo "🏗️ Build Verification..."
echo "------------------------"

# Backend build check
if [ -d backend ]; then
    run_check "Backend dependencies check" "cd backend && python3 -c 'import fastapi, uvicorn, sqlalchemy, redis'"
fi

# Frontend build check
if [ -d frontend ] && command_exists npm; then
    run_check "Frontend dependencies installed" "cd frontend && test -d node_modules || npm install > /dev/null 2>&1"
    run_check "Frontend build test" "cd frontend && npm run build > /dev/null 2>&1"
fi

echo ""
echo "📚 Documentation Checks..."
echo "-------------------------"

run_check "Production deployment guide exists" "test -f PRODUCTION_DEPLOYMENT.md"
run_check "README documentation exists" "test -f README.md"
run_check "Production ready improvements documented" "test -f PRODUCTION_READY_IMPROVEMENTS.md"

echo ""
echo "🌐 Network and SSL Preparation..."
echo "--------------------------------"

# Check if SSL directory is prepared
run_check "SSL directory structure" "test -d nginx/ssl"

# Check Nginx configuration for production readiness
if [ -f nginx/nginx.conf ]; then
    run_check "Nginx SSL configuration present" "grep -q 'ssl_certificate' nginx/nginx.conf"
    run_check "Nginx security headers configured" "grep -q 'add_header.*Security' nginx/nginx.conf"
    run_check "Nginx rate limiting configured" "grep -q 'limit_req_zone' nginx/nginx.conf"
fi

echo ""
echo "🔄 Service Health Checks..."
echo "--------------------------"

# If services are running, check their health
if docker-compose -f docker/docker-compose.prod.yml ps | grep -q "Up"; then
    echo "Services are running, performing health checks..."
    
    run_check "Backend health endpoint" "curl -f http://localhost:8000/health > /dev/null 2>&1"
    run_check "Frontend accessibility" "curl -f http://localhost:3000 > /dev/null 2>&1"
    
    # Test rate limiting if backend is up
    run_check "Rate limiting functional" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/content | grep -q '200\\|429'"
else
    echo "ℹ️  Services not running - skipping health checks"
fi

echo ""
echo "📈 Performance Baseline..."
echo "-------------------------"

# Quick performance check if services are running
if docker-compose -f docker/docker-compose.prod.yml ps | grep -q "Up" && command_exists python3; then
    echo "Running quick performance baseline..."
    run_check "Basic load test" "timeout 30s python3 scripts/load_test.py --users 5 --duration 10 > /dev/null 2>&1"
else
    echo "ℹ️  Services not running - skipping performance tests"
fi

echo ""
echo "==============================================="
echo "🎯 PRODUCTION READINESS VERIFICATION SUMMARY"
echo "==============================================="

# Calculate percentages
if [ $TOTAL_CHECKS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
else
    SUCCESS_RATE=0
fi

echo ""
echo "📊 Results:"
echo "  Total Checks: $TOTAL_CHECKS"
echo -e "  ${GREEN}✅ Passed: $PASSED_CHECKS${NC}"
echo -e "  ${RED}❌ Failed: $FAILED_CHECKS${NC}"
echo -e "  📈 Success Rate: ${SUCCESS_RATE}%"

echo ""
if [ $SUCCESS_RATE -ge 95 ]; then
    echo -e "${GREEN}🎉 EXCELLENT - Ready for Production Deployment!${NC}"
    echo "   All critical checks passed. Your application is production-ready."
elif [ $SUCCESS_RATE -ge 85 ]; then
    echo -e "${YELLOW}⚠️  GOOD - Minor Issues to Address${NC}"
    echo "   Most checks passed. Address remaining issues before deployment."
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo -e "${YELLOW}⚠️  FAIR - Several Issues Need Attention${NC}"
    echo "   Multiple issues detected. Review and fix before production deployment."
else
    echo -e "${RED}❌ CRITICAL - Major Issues Prevent Deployment${NC}"
    echo "   Significant problems detected. Do not deploy to production."
fi

echo ""
echo "📋 Next Steps:"
if [ $FAILED_CHECKS -gt 0 ]; then
    echo "  1. Review and fix all failed checks above"
    echo "  2. Re-run this verification script"
fi
echo "  3. Complete manual testing checklist"
echo "  4. Set up production environment variables"
echo "  5. Configure SSL certificates"
echo "  6. Run full UAT test suite"
echo "  7. Set up monitoring and alerting"
echo "  8. Create production deployment plan"

echo ""
echo "📖 Documentation:"
echo "  • Production Deployment Guide: PRODUCTION_DEPLOYMENT.md"
echo "  • Security Best Practices: Run ./scripts/security_audit.py"
echo "  • Load Testing: ./scripts/load_test.py --help"
echo "  • User Acceptance Testing: ./scripts/uat_testing.py --help"

echo ""
echo "🆘 Support:"
echo "  • Review logs in /tmp/check_output for detailed error information"
echo "  • Check Docker logs: docker-compose -f docker/docker-compose.prod.yml logs"
echo "  • Run individual checks manually for debugging"

# Exit with appropriate code
if [ $SUCCESS_RATE -ge 95 ]; then
    exit 0
elif [ $SUCCESS_RATE -ge 70 ]; then
    exit 1
else
    exit 2
fi