#!/usr/bin/env python3
"""
Simple test script to verify IRSSG package installation
"""

try:
    import irssg
    print("✓ IRSSG package imported successfully")
    print(f"Version: {irssg.__version__}")
    
    # Test utility functions
    from irssg.utils import list_available_space_groups
    space_groups = list_available_space_groups()
    print(f"Available space groups: {len(space_groups)}")
    
    print("✓ All tests passed!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

