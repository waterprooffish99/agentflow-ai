import os
from app.core.config import settings

def verify_staging():
    print("Verifying staging parity...")
    
    # Check for production-like settings in staging
    if settings.app_env != "staging":
        print(f"Warning: APP_ENV is {settings.app_env}, expected staging")
        
    required_production_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "JWT_SECRET",
    ]
    
    for var in required_production_vars:
        if not os.getenv(var):
            print(f"Error: Required variable {var} is missing")
            return False
            
    print("Staging parity verification passed.")
    return True

if __name__ == "__main__":
    verify_staging()
