# -*- coding: utf-8 -*-
"""Simple example of using Blueski session programmatically.

This is a minimal example showing how to use the Blueski session.
For full testing with wx dialogs, use test_atproto_session.py instead.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sessions.blueski import session
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def main():
    print("Blueski Session Simple Example")
    print("=" * 50)
    
    # Create session
    print("\n1. Creating session...")
    s = session.Session(session_id="example_blueski")
    
    # Try to get configuration (will create folder if needed)
    print("2. Loading configuration...")
    s.get_configuration()
    
    # Try to login (will fail if no stored credentials)
    print("3. Attempting login...")
    try:
        s.login()
        print(f"   ✓ Logged in as: {s.get_name()}")
        print(f"   User DID: {s.db.get('user_id', 'unknown')}")
        
    except Exception as e:
        print(f"   ✗ Login failed: {e}")
        print("\n   To authorize a new session:")
        print("   - Run test_atproto_session.py for GUI-based auth")
        print("   - Or manually call s.authorise() after importing wx")
        return
    
    # Show session info
    print("\n4. Session information:")
    print(f"   Logged: {s.logged}")
    print(f"   Handle: {s.settings['blueski']['handle']}")
    print(f"   Service: {s.settings['blueski'].get('service_url', '')}")
    print(f"   Has session_string: {bool(s.settings['blueski']['session_string'])}")
    
    # Test logout
    print("\n5. Testing logout...")
    s.logout()
    print(f"   Logged: {s.logged}")
    print(f"   Session string cleared: {not s.settings['blueski']['session_string']}")
    
    print("\n" + "=" * 50)
    print("Example complete!")

if __name__ == "__main__":
    main()
