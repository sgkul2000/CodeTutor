"""
Local subprocess-based code executor for development.

Runs code directly using the host's Python/Node.js/Java interpreters.
No containers, no namespaces — just subprocess + timeout.

PRODUCTION NOTE: swap the import in submissions.py to piston_service
when deploying against a real Piston (or Judge0) instance.

Supported languages (requires interpreters on PATH):
  python      → python3
  javascript  → node
  java        → javac + java
"""

import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.config import settings

# ── Interpreter config ────────────────────────────────────────────────────────

_TIMEOUT_S = settings.piston_run_timeout / 1000   # convert ms → seconds
_COMPILE_TIMEOUT_S = settings.piston_compile_timeout / 1000


def _run_python(code: str, stdin: str, tmpdir: Path) -> dict:
    src = tmpdir / "solution.py"
    src.write_text(code)
    result = subprocess.run(
        ["python3", str(src)],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_S,
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


def _run_javascript(code: str, stdin: str, tmpdir: Path) -> dict:
    src = tmpdir / "solution.js"
    src.write_text(code)
    result = subprocess.run(
        ["node", str(src)],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_S,
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


def _run_java(code: str, stdin: str, tmpdir: Path) -> dict:
    src = tmpdir / "Solution.java"
    src.write_text(code)

    # Compile
    compile_result = subprocess.run(
        ["javac", str(src)],
        capture_output=True,
        text=True,
        cwd=str(tmpdir),
        timeout=_COMPILE_TIMEOUT_S,
    )
    if compile_result.returncode != 0:
        return {
            "compile_error": True,
            "stderr": compile_result.stderr or compile_result.stdout,
            "stdout": "",
            "returncode": compile_result.returncode,
        }

    # Run
    result = subprocess.run(
        ["java", "-cp", str(tmpdir), "Solution"],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=str(tmpdir),
        timeout=_TIMEOUT_S,
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}


_RUNNERS = {
    "python": _run_python,
    "javascript": _run_javascript,
    "java": _run_java,
}


# ── Public interface (matches piston_service.execute_code) ────────────────────

async def execute_code(code: str, language: str, test_cases: list) -> dict:
    """
    Run `code` against every test case via subprocess.
    Returns the same dict shape as piston_service.execute_code.
    """
    runner = _RUNNERS.get(language)
    if runner is None:
        raise ValueError(f"Unsupported language: {language}")

    loop = asyncio.get_event_loop()
    # Run all test cases concurrently in thread pool (subprocess is blocking)
    tasks = [
        loop.run_in_executor(None, _run_one, runner, code, tc)
        for tc in test_cases
    ]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    return _aggregate(raw_results, test_cases)


def _run_one(runner, code: str, tc) -> dict:
    tmpdir = Path(tempfile.mkdtemp())
    try:
        return runner(code, tc.input, tmpdir)
    except subprocess.TimeoutExpired:
        return {"timeout": True, "stdout": "", "stderr": "", "returncode": -1}
    except FileNotFoundError as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Interpreter not found: {e}. Install it with Homebrew.",
        }
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _aggregate(raw_results: list, test_cases: list) -> dict:
    passed = 0
    failed_case = None
    overall_status = "accepted"
    stderr_out = ""

    for i, result in enumerate(raw_results):
        tc = test_cases[i]

        # ── Unexpected exception (e.g. asyncio/executor error) ────────────────
        if isinstance(result, Exception):
            if overall_status == "accepted":
                overall_status = "runtime_error"
            if failed_case is None:
                failed_case = {"input": tc.input, "expected": tc.expected_output, "actual": ""}
            continue

        # ── Timeout ───────────────────────────────────────────────────────────
        if result.get("timeout"):
            if overall_status == "accepted":
                overall_status = "time_limit"
            if failed_case is None:
                failed_case = {"input": tc.input, "expected": tc.expected_output, "actual": ""}
            continue

        # ── Compile error ─────────────────────────────────────────────────────
        if result.get("compile_error"):
            if overall_status == "accepted":
                overall_status = "compile_error"
            stderr_out = result.get("stderr", "").strip()
            if failed_case is None:
                failed_case = {"input": tc.input, "expected": tc.expected_output, "actual": ""}
            continue

        stdout = result.get("stdout", "").strip()
        stderr = result.get("stderr", "").strip()
        returncode = result.get("returncode", 0)

        # ── Runtime error (non-zero exit) ─────────────────────────────────────
        if returncode != 0:
            if overall_status == "accepted":
                overall_status = "runtime_error"
            if stderr:
                stderr_out = stderr
            if failed_case is None:
                failed_case = {"input": tc.input, "expected": tc.expected_output, "actual": stdout}
            continue

        # ── Output comparison ─────────────────────────────────────────────────
        expected = tc.expected_output.strip()
        if stdout == expected:
            passed += 1
        else:
            if overall_status == "accepted":
                overall_status = "wrong_answer"
            if failed_case is None:
                failed_case = {"input": tc.input, "expected": expected, "actual": stdout}

    return {
        "status": overall_status,
        "results": {
            "total_test_cases": len(test_cases),
            "passed_test_cases": passed,
            "failed_test_case": failed_case,
            "runtime_ms": 0,
            "memory_kb": 0,
            "stderr": stderr_out,
        },
    }
