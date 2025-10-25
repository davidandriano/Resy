#!/usr/bin/env python3
"""
Setup Verification Script
Run this to check if everything is configured correctly
"""
import sys
import os

def print_status(message, status):
    """Print a status message with emoji"""
    symbol = "✓" if status else "✗"
    print(f"{symbol} {message}")
    return status

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status(f"Python version {version.major}.{version.minor}.{version.micro} is compatible", True)
        return True
    else:
        print_status(f"Python version {version.major}.{version.minor}.{version.micro} is too old (need 3.8+)", False)
        return False

def check_env_file():
    """Check if .env file exists and has required fields"""
    if not os.path.exists(".env"):
        print_status(".env file exists", False)
        print("  → You need to create a .env file. Copy .env.example and rename it to .env")
        return False

    print_status(".env file exists", True)

    # Check if it has content
    with open(".env", "r") as f:
        content = f.read()

    has_email = "RESY_EMAIL=" in content and "your.email@example.com" not in content
    has_password = "RESY_PASSWORD=" in content and "your_password_here" not in content

    if has_email:
        print_status(".env has email configured", True)
    else:
        print_status(".env has email configured", False)
        print("  → Add your Resy email to .env file")

    if has_password:
        print_status(".env has password configured", True)
    else:
        print_status(".env has password configured", False)
        print("  → Add your Resy password to .env file")

    return has_email and has_password

def check_dependencies():
    """Check if required packages are installed"""
    required = ["requests", "dotenv", "schedule", "pydantic", "dateutil", "pytz"]
    all_installed = True

    for package in required:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "dateutil":
                __import__("dateutil")
            else:
                __import__(package)
            print_status(f"Package '{package}' is installed", True)
        except ImportError:
            print_status(f"Package '{package}' is installed", False)
            all_installed = False

    if not all_installed:
        print("\n  → Run: pip3 install -r requirements.txt")

    return all_installed

def check_resy_connection():
    """Try to connect to Resy"""
    try:
        from config import load_settings
        from resy_client import ResyClient

        settings = load_settings()
        client = ResyClient(settings.resy_email, settings.resy_password)

        print("\nTesting Resy connection...")
        success = client.login()

        if success:
            print_status("Successfully connected to Resy!", True)

            # Get payment methods
            payment_methods = client.get_payment_methods()
            if payment_methods:
                pm = payment_methods[0]
                print_status(f"Payment method found: {pm.get('provider_name')} ending in {pm.get('last_four')}", True)
            else:
                print_status("No payment method found", False)
                print("  → Add a credit card to your Resy account at resy.com")

            return True
        else:
            print_status("Failed to connect to Resy", False)
            print("  → Check your email and password in .env file")
            return False

    except Exception as e:
        print_status(f"Error testing connection: {str(e)}", False)
        return False

def main():
    print("="*60)
    print("RESY BOT SETUP CHECKER")
    print("="*60)
    print()

    checks = []

    print("Checking Python version...")
    checks.append(check_python_version())
    print()

    print("Checking for .env file...")
    checks.append(check_env_file())
    print()

    print("Checking dependencies...")
    checks.append(check_dependencies())
    print()

    if all(checks[:3]):  # Only test connection if other checks pass
        checks.append(check_resy_connection())

    print()
    print("="*60)
    if all(checks):
        print("✓ ALL CHECKS PASSED!")
        print("="*60)
        print()
        print("You're ready to use the bot!")
        print()
        print("Next steps:")
        print("1. Edit example_book.py with your restaurant details")
        print("2. Run: python3 example_book.py")
        print()
        print("Or see BEGINNER_GUIDE.md for detailed instructions")
    else:
        print("✗ SOME CHECKS FAILED")
        print("="*60)
        print()
        print("Please fix the issues above, then run this script again.")
        print()
        print("For help, see BEGINNER_GUIDE.md")
    print()

if __name__ == "__main__":
    main()
