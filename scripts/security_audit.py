#!/usr/bin/env python3
"""
Social Media Management Bot - Security Audit Script

This script performs automated security checks including:
- Dependency vulnerability scanning
- Configuration security analysis
- Common security misconfigurations
- File permission checks
- Environment variable validation
"""

import os
import subprocess
import json
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re
import requests
from dataclasses import dataclass
import hashlib


@dataclass
class SecurityIssue:
    """Container for security issue information."""
    severity: str  # "critical", "high", "medium", "low", "info"
    category: str
    title: str
    description: str
    file_path: str = None
    line_number: int = None
    recommendation: str = None


class SecurityAuditor:
    """Security audit framework for the Social Media Management Bot."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues: List[SecurityIssue] = []
        
    def add_issue(self, severity: str, category: str, title: str, description: str, 
                  file_path: str = None, line_number: int = None, recommendation: str = None):
        """Add a security issue to the report."""
        issue = SecurityIssue(
            severity=severity,
            category=category,
            title=title,
            description=description,
            file_path=file_path,
            line_number=line_number,
            recommendation=recommendation
        )
        self.issues.append(issue)
    
    def check_dependencies(self):
        """Check for vulnerable dependencies."""
        print("🔍 Checking for vulnerable dependencies...")
        
        # Check Python dependencies
        backend_requirements = self.project_root / "backend" / "requirements.txt"
        if backend_requirements.exists():
            try:
                # Run safety check for Python dependencies
                result = subprocess.run(
                    ["python", "-m", "pip", "install", "safety"],
                    capture_output=True, text=True, cwd=self.project_root
                )
                
                result = subprocess.run(
                    ["python", "-m", "safety", "check", "-r", str(backend_requirements)],
                    capture_output=True, text=True, cwd=self.project_root
                )
                
                if result.returncode != 0 and "No known security vulnerabilities found" not in result.stdout:
                    self.add_issue(
                        "high",
                        "dependencies",
                        "Vulnerable Python Dependencies",
                        f"Safety check found vulnerabilities: {result.stdout}",
                        str(backend_requirements),
                        recommendation="Update vulnerable packages to latest secure versions"
                    )
            except subprocess.SubprocessError as e:
                self.add_issue(
                    "medium",
                    "dependencies",
                    "Unable to Check Python Dependencies",
                    f"Could not run safety check: {e}",
                    recommendation="Install safety package and run manual dependency check"
                )
        
        # Check Node.js dependencies
        frontend_package_json = self.project_root / "frontend" / "package.json"
        if frontend_package_json.exists():
            try:
                result = subprocess.run(
                    ["npm", "audit", "--audit-level", "moderate"],
                    capture_output=True, text=True, cwd=self.project_root / "frontend"
                )
                
                if result.returncode != 0:
                    self.add_issue(
                        "medium",
                        "dependencies",
                        "Vulnerable Node.js Dependencies",
                        f"npm audit found vulnerabilities: {result.stdout}",
                        str(frontend_package_json),
                        recommendation="Run 'npm audit fix' to update vulnerable packages"
                    )
            except subprocess.SubprocessError as e:
                self.add_issue(
                    "medium",
                    "dependencies",
                    "Unable to Check Node.js Dependencies",
                    f"Could not run npm audit: {e}",
                    recommendation="Run manual npm audit check"
                )
    
    def check_environment_configuration(self):
        """Check environment variable configuration for security issues."""
        print("🔍 Checking environment configuration...")
        
        env_files = [
            ".env",
            ".env.example",
            ".env.production",
            "backend/.env",
            "frontend/.env.local"
        ]
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                self._check_env_file(env_path)
    
    def _check_env_file(self, env_path: Path):
        """Check individual environment file for security issues."""
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                lines = content.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Check for weak secrets
                    if any(keyword in key.upper() for keyword in ['SECRET', 'KEY', 'PASSWORD', 'TOKEN']):
                        if self._is_weak_secret(value):
                            self.add_issue(
                                "critical",
                                "configuration",
                                "Weak Secret in Environment File",
                                f"Weak or placeholder secret found: {key}",
                                str(env_path),
                                line_num,
                                "Generate strong, random secrets for production"
                            )
                    
                    # Check for hardcoded credentials
                    if self._contains_hardcoded_credentials(value):
                        self.add_issue(
                            "high",
                            "configuration",
                            "Hardcoded Credentials",
                            f"Potential hardcoded credentials in {key}",
                            str(env_path),
                            line_num,
                            "Use environment-specific configuration and secret management"
                        )
                    
                    # Check for insecure URLs
                    if 'http://' in value and 'localhost' not in value:
                        self.add_issue(
                            "medium",
                            "configuration",
                            "Insecure HTTP URL",
                            f"Non-HTTPS URL found in {key}: {value}",
                            str(env_path),
                            line_num,
                            "Use HTTPS URLs for production"
                        )
        
        except Exception as e:
            self.add_issue(
                "low",
                "configuration",
                "Unable to Check Environment File",
                f"Could not read {env_path}: {e}",
                recommendation="Manually review environment file"
            )
    
    def _is_weak_secret(self, value: str) -> bool:
        """Check if a secret value is weak or placeholder."""
        weak_patterns = [
            "change",
            "replace",
            "your-",
            "example",
            "test",
            "demo",
            "placeholder",
            "secret",
            "password",
            "123",
            "abc"
        ]
        
        value_lower = value.lower()
        
        # Check for common weak patterns
        if any(pattern in value_lower for pattern in weak_patterns):
            return True
        
        # Check for very short secrets
        if len(value) < 16:
            return True
        
        # Check for simple patterns
        if value == value.upper() or value == value.lower():
            return True
        
        return False
    
    def _contains_hardcoded_credentials(self, value: str) -> bool:
        """Check if value contains hardcoded credentials."""
        # Look for patterns that suggest real credentials
        patterns = [
            r"^[A-Za-z0-9+/]{40,}={0,2}$",  # Base64-like
            r"^sk-[A-Za-z0-9]{20,}$",      # OpenAI API key pattern
            r"^xoxb-[A-Za-z0-9-]{50,}$",   # Slack token pattern
            r"^ghp_[A-Za-z0-9]{36}$",      # GitHub token pattern
        ]
        
        for pattern in patterns:
            if re.match(pattern, value):
                return True
        
        return False
    
    def check_file_permissions(self):
        """Check file permissions for security issues."""
        print("🔍 Checking file permissions...")
        
        sensitive_files = [
            ".env",
            ".env.production",
            "backend/.env",
            "frontend/.env.local",
            "scripts/backup_database.sh",
            "scripts/restore_database.sh"
        ]
        
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                stat_info = full_path.stat()
                permissions = oct(stat_info.st_mode)[-3:]
                
                # Check if file is world-readable
                if int(permissions[2]) & 4:  # Others have read permission
                    self.add_issue(
                        "medium",
                        "permissions",
                        "Sensitive File World-Readable",
                        f"File {file_path} is readable by others (permissions: {permissions})",
                        str(full_path),
                        recommendation="Set file permissions to 600 (owner read/write only)"
                    )
    
    def check_docker_configuration(self):
        """Check Docker configuration for security issues."""
        print("🔍 Checking Docker configuration...")
        
        docker_files = [
            "docker/docker-compose.yml",
            "docker/docker-compose.prod.yml",
            "backend/Dockerfile",
            "frontend/Dockerfile"
        ]
        
        for docker_file in docker_files:
            docker_path = self.project_root / docker_file
            if docker_path.exists():
                self._check_docker_file(docker_path)
    
    def _check_docker_file(self, docker_path: Path):
        """Check individual Docker file for security issues."""
        try:
            with open(docker_path, 'r') as f:
                content = f.read()
            
            # Check for running as root
            if 'USER root' in content or 'USER 0' in content:
                self.add_issue(
                    "medium",
                    "docker",
                    "Container Running as Root",
                    "Container configured to run as root user",
                    str(docker_path),
                    recommendation="Create and use non-root user in container"
                )
            
            # Check for secrets in Docker files
            if any(keyword in content.upper() for keyword in ['PASSWORD=', 'SECRET=', 'TOKEN=']):
                self.add_issue(
                    "high",
                    "docker",
                    "Hardcoded Secrets in Docker File",
                    "Potential secrets hardcoded in Docker configuration",
                    str(docker_path),
                    recommendation="Use Docker secrets or environment variables"
                )
            
            # Check for privileged mode
            if 'privileged: true' in content:
                self.add_issue(
                    "high",
                    "docker",
                    "Privileged Container",
                    "Container running in privileged mode",
                    str(docker_path),
                    recommendation="Remove privileged mode unless absolutely necessary"
                )
        
        except Exception as e:
            self.add_issue(
                "low",
                "docker",
                "Unable to Check Docker File",
                f"Could not read {docker_path}: {e}",
                recommendation="Manually review Docker configuration"
            )
    
    def check_cors_configuration(self):
        """Check CORS configuration for security issues."""
        print("🔍 Checking CORS configuration...")
        
        # Check backend CORS configuration
        config_file = self.project_root / "backend" / "app" / "core" / "config.py"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                
                if 'ALLOWED_HOSTS: List[str] = ["*"]' in content:
                    self.add_issue(
                        "medium",
                        "cors",
                        "Permissive CORS Configuration",
                        "CORS allows all origins (*) which may be insecure for production",
                        str(config_file),
                        recommendation="Restrict ALLOWED_HOSTS to specific domains in production"
                    )
            except Exception as e:
                pass
        
        # Check Next.js configuration
        next_config = self.project_root / "frontend" / "next.config.js"
        if next_config.exists():
            try:
                with open(next_config, 'r') as f:
                    content = f.read()
                
                # Check for security headers
                security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Content-Security-Policy']
                missing_headers = []
                
                for header in security_headers:
                    if header not in content:
                        missing_headers.append(header)
                
                if missing_headers:
                    self.add_issue(
                        "medium",
                        "headers",
                        "Missing Security Headers",
                        f"Missing security headers: {', '.join(missing_headers)}",
                        str(next_config),
                        recommendation="Add all recommended security headers"
                    )
            except Exception as e:
                pass
    
    def check_ssl_configuration(self):
        """Check SSL/TLS configuration."""
        print("🔍 Checking SSL/TLS configuration...")
        
        # Check for HTTP URLs in production configuration
        prod_env = self.project_root / ".env.production"
        if prod_env.exists():
            try:
                with open(prod_env, 'r') as f:
                    content = f.read()
                
                # Look for HTTP URLs (excluding localhost)
                http_urls = re.findall(r'http://(?!localhost)[^\s]+', content)
                if http_urls:
                    self.add_issue(
                        "high",
                        "ssl",
                        "HTTP URLs in Production Configuration",
                        f"Found HTTP URLs in production config: {', '.join(http_urls)}",
                        str(prod_env),
                        recommendation="Replace with HTTPS URLs for production"
                    )
            except Exception as e:
                pass
    
    def run_audit(self):
        """Run complete security audit."""
        print("🛡️  Starting Security Audit for Social Media Management Bot")
        print("=" * 70)
        
        # Run all security checks
        self.check_dependencies()
        self.check_environment_configuration()
        self.check_file_permissions()
        self.check_docker_configuration()
        self.check_cors_configuration()
        self.check_ssl_configuration()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate and display security audit report."""
        print("\n" + "=" * 70)
        print("SECURITY AUDIT REPORT")
        print("=" * 70)
        
        if not self.issues:
            print("✅ No security issues found!")
            return
        
        # Group issues by severity
        severity_groups = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        
        for issue in self.issues:
            severity_groups[issue.severity].append(issue)
        
        # Summary
        total_issues = len(self.issues)
        print(f"\n📊 Summary: {total_issues} security issues found")
        
        for severity, issues in severity_groups.items():
            if issues:
                emoji = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "⚠️",
                    "low": "ℹ️",
                    "info": "ℹ️"
                }[severity]
                print(f"  {emoji} {severity.title()}: {len(issues)}")
        
        # Detailed issues
        for severity in ["critical", "high", "medium", "low", "info"]:
            issues = severity_groups[severity]
            if not issues:
                continue
            
            print(f"\n{severity.upper()} SEVERITY ISSUES:")
            print("-" * 50)
            
            for i, issue in enumerate(issues, 1):
                print(f"\n{i}. {issue.title}")
                print(f"   Category: {issue.category}")
                print(f"   Description: {issue.description}")
                
                if issue.file_path:
                    if issue.line_number:
                        print(f"   Location: {issue.file_path}:{issue.line_number}")
                    else:
                        print(f"   File: {issue.file_path}")
                
                if issue.recommendation:
                    print(f"   Recommendation: {issue.recommendation}")
        
        # Security score
        score = self._calculate_security_score()
        print(f"\n🔒 Security Score: {score}/100")
        
        if score >= 90:
            print("   ✅ Excellent security posture")
        elif score >= 70:
            print("   ⚠️  Good security, some improvements needed")
        elif score >= 50:
            print("   ⚠️  Moderate security, several issues to address")
        else:
            print("   🚨 Poor security posture, immediate attention required")
        
        # Action items
        print(f"\n📋 Next Steps:")
        print("  1. Address critical and high severity issues immediately")
        print("  2. Review and implement recommended security measures")
        print("  3. Set up automated security scanning in CI/CD pipeline")
        print("  4. Schedule regular security audits")
        print("  5. Keep dependencies updated")
    
    def _calculate_security_score(self) -> int:
        """Calculate security score based on issues found."""
        if not self.issues:
            return 100
        
        # Weight different severity levels
        weights = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3,
            "info": 1
        }
        
        total_deduction = 0
        for issue in self.issues:
            total_deduction += weights.get(issue.severity, 1)
        
        # Cap the maximum deduction
        max_deduction = 95  # Minimum score of 5
        total_deduction = min(total_deduction, max_deduction)
        
        return max(5, 100 - total_deduction)


def main():
    """Main function to run security audit."""
    project_root = os.getcwd()
    
    # Allow custom project root
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    
    auditor = SecurityAuditor(project_root)
    auditor.run_audit()


if __name__ == "__main__":
    main()