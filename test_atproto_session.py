# -*- coding: utf-8 -*-
"""Test script for Blueski session functionality.

This script demonstrates how to use the Blueski session implementation.
It can be used to verify that the authentication flow works correctly.

Usage:
    python test_atproto_session.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import required modules
from sessions.blueski import session
import paths
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_authorization():
    """Test the authorization flow."""
    print("\n" + "="*60)
    print("Blueski Session Authorization Test")
    print("="*60)
    print("\nThis test will:")
    print("1. Create a new Blueski session")
    print("2. Walk you through the authorization process")
    print("3. Verify the session was created correctly")
    print("\nNOTE: You'll need:")
    print("  - Your Blueski handle (e.g., user.bsky.social)")
    print("  - An app password (NOT your main password)")
    print("\n" + "="*60 + "\n")
    
    # Create a test session
    test_session_id = "test_blueski_001"
    print(f"Creating session with ID: {test_session_id}")
    
    s = session.Session(session_id=test_session_id)
    
    try:
        # Try to login first (should fail for new session)
        print("\nAttempting to login with existing credentials...")
        s.get_configuration()
        s.login()
        print("✓ Login successful! Session already exists.")
        print(f"  Session name: {s.get_name()}")
        print(f"  Logged in: {s.logged}")
        
    except Exception as e:
        # Expected for first run
        print(f"✗ Login failed (expected): {type(e).__name__}")
        print("\nStarting authorization process...")
        print("(GUI dialogs will open for handle and password)")
        
        try:
            result = s.authorise()
            
            if result:
                print("\n✓ Authorization successful!")
                print(f"  Session name: {s.get_name()}")
                print(f"  Logged in: {s.logged}")
                print(f"  User DID: {s.settings['blueski']['did']}")
                print(f"  Handle: {s.settings['blueski']['handle']}")
                
                # Check that session_string was saved
                if s.settings['blueski']['session_string']:
                    print("  ✓ Session string saved")
                else:
                    print("  ✗ WARNING: Session string not saved!")
                
                # Check that app_password was cleared
                if not s.settings['blueski']['app_password']:
                    print("  ✓ App password cleared (secure)")
                else:
                    print("  ✗ WARNING: App password still in config!")
                
                print(f"\nSession configuration saved to:")
                print(f"  {os.path.join(paths.config_path(), test_session_id, 'session.conf')}")
                
                return s
            else:
                print("\n✗ Authorization cancelled or failed")
                return None
                
        except Exception as e:
            print(f"\n✗ Authorization error: {e}")
            import traceback
            traceback.print_exc()
            return None

def test_logout(s):
    """Test the logout functionality."""
    if not s:
        print("\nSkipping logout test (no active session)")
        return
    
    print("\n" + "="*60)
    print("Testing logout functionality")
    print("="*60)
    
    print(f"\nCurrent state: logged={s.logged}")
    
    s.logout()
    
    print(f"After logout: logged={s.logged}")
    
    # Check that session_string was cleared
    if not s.settings['blueski']['session_string']:
        print("✓ Session string cleared")
    else:
        print("✗ WARNING: Session string not cleared!")
    
    print("\nLogout test complete")

def test_session_restoration():
    """Test restoring a session from saved credentials."""
    print("\n" + "="*60)
    print("Testing session restoration")
    print("="*60)
    
    test_session_id = "test_blueski_001"
    print(f"\nCreating new session object with ID: {test_session_id}")
    
    s = session.Session(session_id=test_session_id)
    
    try:
        s.get_configuration()
        s.login()
        print("✓ Session restored successfully!")
        print(f"  Session name: {s.get_name()}")
        print(f"  Logged in: {s.logged}")
        return s
    except Exception as e:
        print(f"✗ Failed to restore session: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function."""
    print("\nBlueski Session Test Suite")
    print("Ensure you have wxPython installed for GUI dialogs\n")
    
    # Test 1: Authorization
    session_obj = test_authorization()
    
    if not session_obj:
        print("\nTests aborted (authorization failed)")
        return
    
    input("\nPress Enter to test session restoration...")
    
    # Test 2: Logout
    test_logout(session_obj)
    
    input("\nPress Enter to test session restoration after logout...")
    
    # Test 3: Try to restore (should fail after logout)
    restored_session = test_session_restoration()
    
    if not restored_session:
        print("\n✓ Session restoration correctly failed after logout")
    else:
        print("\n✗ WARNING: Session was restored after logout (unexpected)")
    
    print("\n" + "="*60)
    print("All tests complete!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
