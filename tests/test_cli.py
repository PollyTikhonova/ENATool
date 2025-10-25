#!/usr/bin/env python
"""
Test script for ENATool CLI

This script demonstrates how to test the CLI without actually
downloading large files.
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and print output."""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print('='*60)
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    
    return result.returncode


def main():
    """Run CLI tests."""
    print("ENATool CLI Test Script")
    print("=" * 60)
    
    # Test 1: Version
    print("\n📌 Test 1: Check version")
    run_command("python -m ENATool.cli --version")
    
    # Test 2: Help
    print("\n📌 Test 2: Show help")
    run_command("python -m ENATool.cli --help")
    
    # Test 3: Fetch help
    print("\n📌 Test 3: Fetch command help")
    run_command("python -m ENATool.cli fetch --help")
    
    # Test 4: Download help
    print("\n📌 Test 4: Download command help")
    run_command("python -m ENATool.cli download --help")
    
    print("\n" + "=" * 60)
    print("✓ CLI tests complete!")
    print("=" * 60)
    print("\nTo test actual functionality:")
    print("  python -m ENATool.cli fetch PRJNA335681")
    print("  python -m ENATool.cli download PRJNA335681")
    print("\nOr after installation:")
    print("  enatool fetch PRJNA335681")
    print("  enatool download PRJNA335681")


if __name__ == "__main__":
    main()
