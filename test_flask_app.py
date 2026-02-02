"""
Test script to verify Flask app is working correctly
Run this before deploying to PythonAnywhere
"""

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print(f"✓ Flask {flask.__version__}")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import flask_session
        print(f"✓ Flask-Session installed")
    except ImportError as e:
        print(f"✗ Flask-Session import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print(f"✓ PyPDF2 installed")
    except ImportError as e:
        print(f"✗ PyPDF2 import failed: {e}")
        return False
    
    try:
        import fitz
        print(f"✓ PyMuPDF (fitz) installed")
    except ImportError as e:
        print(f"✗ PyMuPDF import failed: {e}")
        return False
    
    print("\nAll imports successful!\n")
    return True


def test_app_structure():
    """Test that Flask app can be imported and has required routes"""
    print("Testing Flask app structure...")
    
    try:
        from app import app
        print("✓ Flask app imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Flask app: {e}")
        return False
    
    # Check for required routes
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    required_routes = [
        '/',
        '/upload',
        '/new',
        '/merge',
        '/extract',
        '/validate',
    ]
    
    missing_routes = []
    for route in required_routes:
        if route in routes:
            print(f"✓ Route {route} exists")
        else:
            print(f"✗ Route {route} missing")
            missing_routes.append(route)
    
    if missing_routes:
        print(f"\nMissing routes: {missing_routes}")
        return False
    
    print("\nApp structure looks good!\n")
    return True


def test_pdf_manager():
    """Test that pdf_manager.py works"""
    print("Testing PDF manager...")
    
    try:
        from pdf_manager import PDFManager
        manager = PDFManager()
        print("✓ PDFManager instantiated successfully")
        
        # Test basic methods exist
        assert hasattr(manager, 'add_pdf')
        assert hasattr(manager, 'remove_pdf')
        assert hasattr(manager, 'merge_all')
        assert hasattr(manager, 'extract_question_pages')
        assert hasattr(manager, 'validate_question_continuity')
        print("✓ All required methods exist")
        
    except Exception as e:
        print(f"✗ PDF manager test failed: {e}")
        return False
    
    print("\nPDF manager working!\n")
    return True


def test_directories():
    """Test that required directories exist or can be created"""
    print("Testing directory structure...")
    
    import os
    from pathlib import Path
    
    required_dirs = [
        'templates',
        'static',
        'uploads',
        'flask_session',
    ]
    
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists():
            print(f"✓ {dir_name}/ exists")
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✓ {dir_name}/ created")
            except Exception as e:
                print(f"✗ Failed to create {dir_name}/: {e}")
                return False
    
    # Check for template files
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/pdf_view.html',
        'templates/extract.html',
        'templates/validate.html',
        'templates/task_status.html',
    ]
    
    missing_templates = []
    for template in template_files:
        if Path(template).exists():
            print(f"✓ {template} exists")
        else:
            print(f"✗ {template} missing")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"\nMissing templates: {missing_templates}")
        return False
    
    print("\nDirectory structure is good!\n")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Flask PDF Editor - Pre-Deployment Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("App Structure Test", test_app_structure),
        ("PDF Manager Test", test_pdf_manager),
        ("Directory Structure Test", test_directories),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Running: {name}")
        print('=' * 60)
        success = test_func()
        results.append((name, success))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {name}")
        if not success:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Ready to deploy.")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Test all features manually")
        print("4. Follow DEPLOYMENT_GUIDE.md for PythonAnywhere deployment")
    else:
        print("\n✗ Some tests failed. Please fix issues before deploying.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Check that all files are present")
        print("- Verify file permissions")
    
    print()


if __name__ == '__main__':
    main()
