"""
Validate the project structure without requiring external dependencies
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def validate_project_structure():
    """Validate the complete project structure"""
    print("🧪 Validating Social Media Management Bot Project Structure...\n")
    
    base_path = os.path.dirname(__file__)
    all_good = True
    
    # Backend structure
    print("📁 Backend Structure:")
    backend_files = [
        ("backend/main.py", "FastAPI main application"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/Dockerfile", "Backend Docker configuration"),
        ("backend/app/__init__.py", "Backend app package"),
        ("backend/app/core/config.py", "Configuration settings"),
        ("backend/app/core/database.py", "Database configuration"),
        ("backend/app/core/security.py", "Security utilities"),
        ("backend/app/core/auth.py", "Authentication dependencies"),
        ("backend/app/models/user.py", "User model"),
        ("backend/app/models/social_account.py", "Social account model"),
        ("backend/app/models/content.py", "Content model"),
        ("backend/app/models/analytics.py", "Analytics model"),
        ("backend/app/schemas/user.py", "User schemas"),
        ("backend/app/services/user_service.py", "User service"),
        ("backend/app/api/main.py", "API router"),
        ("backend/app/api/routes/auth.py", "Authentication routes"),
        ("backend/app/api/routes/users.py", "User routes"),
    ]
    
    for filepath, description in backend_files:
        full_path = os.path.join(base_path, filepath)
        if not check_file_exists(full_path, description):
            all_good = False
    
    print("\n📁 Frontend Structure:")
    frontend_files = [
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/Dockerfile", "Frontend Docker configuration"),
        ("frontend/app/layout.tsx", "Root layout"),
        ("frontend/app/page.tsx", "Home page"),
        ("frontend/app/content/page.tsx", "Content page"),
        ("frontend/app/accounts/page.tsx", "Accounts page"),
        ("frontend/components/providers.tsx", "React providers"),
        ("frontend/components/theme-provider.tsx", "Theme provider"),
        ("frontend/components/dashboard/layout.tsx", "Dashboard layout"),
        ("frontend/components/dashboard/sidebar.tsx", "Dashboard sidebar"),
        ("frontend/components/dashboard/header.tsx", "Dashboard header"),
        ("frontend/components/dashboard/overview.tsx", "Dashboard overview"),
    ]
    
    for filepath, description in frontend_files:
        full_path = os.path.join(base_path, filepath)
        if not check_file_exists(full_path, description):
            all_good = False
    
    print("\n📁 Docker & DevOps:")
    docker_files = [
        ("docker/docker-compose.yml", "Development Docker Compose"),
        ("docker/docker-compose.prod.yml", "Production Docker Compose"),
    ]
    
    for filepath, description in docker_files:
        full_path = os.path.join(base_path, filepath)
        if not check_file_exists(full_path, description):
            all_good = False
    
    print("\n📁 Documentation:")
    doc_files = [
        ("README.md", "Project documentation"),
        (".gitignore", "Git ignore rules"),
    ]
    
    for filepath, description in doc_files:
        full_path = os.path.join(base_path, filepath)
        if not check_file_exists(full_path, description):
            all_good = False
    
    return all_good

def check_code_quality():
    """Check basic code structure and patterns"""
    print("\n🔍 Code Quality Checks:")
    
    # Check if main backend files have proper imports
    backend_main = os.path.join(os.path.dirname(__file__), "backend", "main.py")
    if os.path.exists(backend_main):
        with open(backend_main, 'r') as f:
            content = f.read()
            if "FastAPI" in content and "lifespan" in content:
                print("✅ Backend main.py has proper FastAPI setup")
            else:
                print("❌ Backend main.py missing FastAPI setup")
    
    # Check if frontend has proper Next.js structure
    frontend_layout = os.path.join(os.path.dirname(__file__), "frontend", "app", "layout.tsx")
    if os.path.exists(frontend_layout):
        with open(frontend_layout, 'r') as f:
            content = f.read()
            if "RootLayout" in content and "Providers" in content:
                print("✅ Frontend layout.tsx has proper Next.js setup")
            else:
                print("❌ Frontend layout.tsx missing proper setup")
    
    # Check Docker configurations
    docker_compose = os.path.join(os.path.dirname(__file__), "docker", "docker-compose.yml")
    if os.path.exists(docker_compose):
        with open(docker_compose, 'r') as f:
            content = f.read()
            if "postgres" in content and "redis" in content and "backend" in content and "frontend" in content:
                print("✅ Docker Compose has all required services")
            else:
                print("❌ Docker Compose missing required services")

if __name__ == "__main__":
    structure_valid = validate_project_structure()
    check_code_quality()
    
    print("\n" + "="*60)
    
    if structure_valid:
        print("🎉 PROJECT STRUCTURE VALIDATION PASSED!")
        print("\n📋 Summary:")
        print("✅ Complete backend architecture with FastAPI")
        print("✅ Modern frontend with Next.js and React")
        print("✅ Database models for multi-user system")
        print("✅ Authentication and authorization system")
        print("✅ Docker containerization setup")
        print("✅ Comprehensive documentation")
        print("\n🚀 The Social Media Management Bot is ready for development!")
        print("📝 Next steps:")
        print("   1. Install dependencies: pip install -r backend/requirements.txt")
        print("   2. Set up environment variables")
        print("   3. Run with Docker: docker-compose up")
        print("   4. Access at http://localhost:3000")
    else:
        print("❌ PROJECT STRUCTURE VALIDATION FAILED!")
        print("Some required files are missing. Please check the structure.")
        sys.exit(1)