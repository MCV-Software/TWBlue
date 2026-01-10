
import sys
import os
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import config_utils
from configobj import ConfigObj
import logging

# Setup simple logging
logging.basicConfig(level=logging.DEBUG)

def test_config_save():
    print("Beginning Config Save Test")
    
    # 1. Setup paths
    config_dir = os.path.join(os.getcwd(), 'test_config_dir')
    if os.path.exists(config_dir):
        shutil.rmtree(config_dir)
    os.mkdir(config_dir)
    
    session_id = "test_session"
    session_dir = os.path.join(config_dir, session_id)
    os.mkdir(session_dir)
    
    config_path = os.path.join(session_dir, "session.conf")
    # We use the ACTUAL atproto.defaults from src
    spec_path = os.path.join(os.getcwd(), 'src', 'atproto.defaults')
    
    print(f"Config Path: {config_path}")
    print(f"Spec Path: {spec_path}")
    
    if not os.path.exists(spec_path):
        print("ERROR: Spec file not found at", spec_path)
        return

    # 2. Simulate Load & Create
    print("\n--- Loading Config (create empty) ---")
    try:
        # Mimic session.get_configuration
        config = config_utils.load_config(config_path, spec_path)
    except Exception as e:
        print("Error loading config:", e)
        return

    # 3. Modify Values
    print("\n--- Modifying Values ---")
    
    # Check if section exists, if not, create it
    if 'atproto' not in config:
        print("Section 'atproto' missing (expected for new file). Using defaults from spec?")
        # ConfigObj with spec should automatically have sections if create_empty=True?
        # Actually config_utils.load_config sets create_empty=True
    
    # Let's inspect what we have
    print("Current Config Keys:", config.keys())
    
    # If section is missing (it might be if file was empty and defaults didn't force creation yet?), force create
    if 'atproto' not in config:
        print("Creating 'atproto' section manually (simulating what might happen if defaults don't auto-create structure)")
        config['atproto'] = {}
        
    config['atproto']['handle'] = "test_user.bsky.social"
    config['atproto']['session_string'] = "fake_session_string_12345"
    
    print(f"Set handle: {config['atproto']['handle']}")
    print(f"Set session_string: {config['atproto']['session_string']}")
    
    # 4. Write
    print("\n--- Writing Config ---")
    config.write()
    print("Write called.")
    
    # 5. Read Back from Disk (Raw)
    print("\n--- Reading Back (Raw Text) ---")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
            print("File Content:")
            print(content)
            
            if "session_string = fake_session_string_12345" in content:
                print("SUCCESS: Session string found in file.")
            else:
                print("FAILURE: Session string NOT found in file.")
    else:
        print("FAILURE: File does not exist.")
        
    # 6. Read Back (using config_utils again)
    print("\n--- Reading Back (config_utils) ---")
    config2 = config_utils.load_config(config_path, spec_path)
    val = config2['atproto']['session_string']
    print(f"Read session_string: {val}")
    
    if val == "fake_session_string_12345":
        print("SUCCESS: Read back correct value.")
    else:
        print("FAILURE: Read back mismatched value.")

if __name__ == "__main__":
    test_config_save()
