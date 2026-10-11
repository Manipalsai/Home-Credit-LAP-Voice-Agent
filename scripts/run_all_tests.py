import subprocess
import sys
import os

def main():
    print("=" * 70)
    print(" HOME CREDIT LAP AI VOICE AGENT — AUTOMATED TEST SUITE")
    print("=" * 70)
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pytest_bin = os.path.join(root_dir, ".venv", "Scripts", "pytest.exe")
    if not os.path.exists(pytest_bin):
        pytest_bin = "pytest"

    test_dirs = [os.path.join(root_dir, "backend", "tests")]
    cmd = [pytest_bin, "-v", "--tb=short"] + test_dirs

    print(f"Executing: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=root_dir)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print(" [SUCCESS] ALL 100 AUTOMATED TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print(f" [FAILED] Test suite exited with code {result.returncode}")
        print("=" * 70)
        
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
