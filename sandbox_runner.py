import subprocess
import os

def run_tests_in_docker(patch_code, test_code, work_dir="sandbox_temp"):
    """
    Writes the patch and tests to files, runs them inside the Docker
    container, and returns whether the tests passed plus the output.
    """
    os.makedirs(work_dir, exist_ok=True)

    with open(os.path.join(work_dir, "calculate.py"), "w") as f:
        f.write(patch_code)

    with open(os.path.join(work_dir, "test_calculate.py"), "w") as f:
        f.write(test_code)

    abs_path = os.path.abspath(work_dir)
    result = subprocess.run(
        ["docker", "run", "-v", f"{abs_path}:/app", "pytest-sandbox", "pytest"],
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr
    passed = result.returncode == 0

    return {
        "passed": passed,
        "output": output
    }

if __name__ == "__main__":
    fake_patch = "def add(a, b):\n    return a + b\n"
    fake_tests = "from calculate import add\n\ndef test_add():\n    assert add(2, 2) == 4\n"
    result = run_tests_in_docker(fake_patch, fake_tests)
    print("PASSED:", result["passed"])
    print(result["output"])