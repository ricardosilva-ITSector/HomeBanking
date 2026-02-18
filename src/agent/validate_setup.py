"""
Setup validation script for HomeBanking Agent Service.
Run this to verify all dependencies are installed and imports work.
"""
import sys

def validate_imports():
    """Validate all required imports."""
    print("Validating imports...")
    
    try:
        import agent_framework
        print(f"✓ agent-framework-core: {agent_framework.__version__}")
    except ImportError as e:
        print(f"✗ agent-framework-core: {e}")
        return False
    
    try:
        from azure.ai.projects import AIProjectClient
        print("✓ azure-ai-projects (Foundry SDK)")
    except ImportError as e:
        print(f"✗ azure-ai-projects: {e}")
        return False
    
    try:
        from azure.identity import DefaultAzureCredential
        print("✓ azure-identity")
    except ImportError as e:
        print(f"✗ azure-identity: {e}")
        return False
    
    try:
        import httpx
        print(f"✓ httpx: {httpx.__version__}")
    except ImportError as e:
        print(f"✗ httpx: {e}")
        return False
    
    try:
        import structlog
        print(f"✓ structlog: {structlog.__version__}")
    except ImportError as e:
        print(f"✗ structlog: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False
    
    try:
        import pytest
        print(f"✓ pytest: {pytest.__version__}")
    except ImportError as e:
        print(f"✗ pytest: {e}")
        return False
    
    print("\n✅ All required imports successful!")
    return True


def validate_module_structure():
    """Validate local module structure."""
    print("\nValidating local modules...")
    
    try:
        from config import AgentConfig
        print("✓ config.py: AgentConfig class available")
    except ImportError as e:
        print(f"✗ config.py: {e}")
        return False
    
    try:
        from tools import HomeBankingTools
        print("✓ tools.py: HomeBankingTools class available")
    except ImportError as e:
        print(f"✗ tools.py: {e}")
        return False
    
    print("\n✅ All local modules valid!")
    return True


def validate_python_version():
    """Validate Python version meets requirements."""
    print("Validating Python version...")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("✓ Python 3.10+ requirement met")
        return True
    else:
        print("✗ Python 3.10+ required")
        return False


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("HomeBanking Agent Service - Setup Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", validate_python_version),
        ("Package Imports", validate_imports),
        ("Module Structure", validate_module_structure),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with exception: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 Setup validation successful!")
        print("Next: Configure .env file with Foundry credentials")
        return 0
    else:
        print("⚠️  Some checks failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
