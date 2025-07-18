"""
Test basic backend functionality without external dependencies
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_import_structure():
    """Test that our backend modules can be imported"""
    try:
        # Test core modules
        from app.core.config import Settings
        from app.models.user import User, UserRole
        from app.models.social_account import SocialAccount, SocialPlatform
        from app.models.content import Content, ContentType
        from app.schemas.user import UserCreate, UserResponse
        
        print("✅ All backend modules imported successfully")
        
        # Test basic functionality
        settings = Settings()
        print(f"✅ Settings loaded: {settings.PROJECT_NAME}")
        
        # Test enum values
        assert UserRole.OWNER == "owner"
        assert SocialPlatform.INSTAGRAM == "instagram"
        assert ContentType.VIDEO == "video"
        
        print("✅ All enums working correctly")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Social Media Management Bot Backend Structure...")
    success = test_import_structure()
    
    if success:
        print("\n🎉 All backend structure tests passed!")
        print("The backend is properly structured and ready for development.")
    else:
        print("\n💥 Some tests failed. Check the backend structure.")
        sys.exit(1)