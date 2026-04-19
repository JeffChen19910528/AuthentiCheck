"""Convenience script: python run_tests.py"""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    cwd=str(__import__("pathlib").Path(__file__).parent),
)
sys.exit(result.returncode)
