"""
Piston code execution service.

Replaces judge0_service.py. Key differences from Judge0:
  - Single REST call per execution (no token + polling)
  - No batch API → run test cases concurrently with asyncio.gather
  - No built-in pass/fail → we compare stdout vs expected_output
  - No cgroup v1 required → works on Podman + Fedora CoreOS 42

Piston API reference: https://github.com/engineer-man/piston#api-v2
"""

import asyncio

import httpx

from app.config import settings

# Maps our language keys → Piston language identifiers.
# Piston installs node as language="javascript" (see GET /api/v2/runtimes).
LANGUAGE_MAP = {
    "python": "python",
    "java": "java",
    "javascript": "javascript",
}

# Source-file extensions sent to Piston (affects compile behaviour for Java)
EXTENSIONS = {
    "python": "py",
    "java": "java",
    "javascript": "js",
}

# Cache: piston_language → installed version string (populated on first use)
_version_cache: dict[str, str] = {}


async def _ensure_version_cache(client: httpx.AsyncClient) -> None:
    """Fetch /api/v2/runtimes once and populate _version_cache."""
    if _version_cache:
        return
    resp = await client.get(f"{settings.piston_url}/api/v2/runtimes", timeout=10)
    resp.raise_for_status()
    for rt in resp.json():
        lang = rt["language"]
        # Keep the first (latest) entry per language — Piston returns them sorted
        if lang not in _version_cache:
            _version_cache[lang] = rt["version"]


async def _run_one(
    client: httpx.AsyncClient,
    code: str,
    piston_lang: str,
    version: str,
    stdin: str,
) -> dict:
    """Submit one (code, stdin) pair to Piston and return the raw response."""
    ext = EXTENSIONS.get(piston_lang, "txt")
    resp = await client.post(
        f"{settings.piston_url}/api/v2/execute",
        json={
            "language": piston_lang,
            "version": version,
            "files": [{"name": f"solution.{ext}", "content": code}],
            "stdin": stdin,
            "compile_timeout": settings.piston_compile_timeout,
            "run_timeout": settings.piston_run_timeout,
        },
        timeout=settings.piston_run_timeout / 1000 + 15,
    )
    resp.raise_for_status()
    return resp.json()


async def execute_code(code: str, language: str, test_cases: list) -> dict:
    """
    Run `code` against every test case and return aggregated results.

    Return shape (same contract as the old judge0_service):
        {
            "status": "accepted" | "wrong_answer" | "runtime_error"
                      | "time_limit" | "compile_error",
            "results": {
                "total_test_cases": int,
                "passed_test_cases": int,
                "failed_test_case": dict | None,
                "runtime_ms": int,
                "memory_kb": int,
                "stderr": str,
            },
        }
    """
    piston_lang = LANGUAGE_MAP.get(language)
    if piston_lang is None:
        raise ValueError(f"Unsupported language: {language}")

    async with httpx.AsyncClient() as client:
        await _ensure_version_cache(client)
        version = _version_cache.get(piston_lang)
        if not version:
            raise RuntimeError(
                f"Language '{piston_lang}' is not installed in Piston. "
                f"Run: podman exec piston piston ppman install {piston_lang}"
            )

        tasks = [
            _run_one(client, code, piston_lang, version, tc.input)
            for tc in test_cases
        ]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    return _aggregate(raw_results, test_cases)


def _aggregate(raw_results: list, test_cases: list) -> dict:
    passed = 0
    failed_case: dict | None = None
    overall_status = "accepted"
    stderr_out = ""

    for i, result in enumerate(raw_results):
        tc = test_cases[i]

        # ── Network / unexpected exception ────────────────────────────────────
        if isinstance(result, Exception):
            if overall_status == "accepted":
                overall_status = "runtime_error"
            if failed_case is None:
                failed_case = {
                    "input": tc.input,
                    "expected": tc.expected_output,
                    "actual": "",
                }
            continue

        # ── Compile error (Java, C++, etc.) ──────────────────────────────────
        compile_info = result.get("compile")
        if compile_info and compile_info.get("code", 0) != 0:
            if overall_status == "accepted":
                overall_status = "compile_error"
            stderr_out = (
                compile_info.get("stderr") or compile_info.get("output") or ""
            ).strip()
            if failed_case is None:
                failed_case = {
                    "input": tc.input,
                    "expected": tc.expected_output,
                    "actual": "",
                }
            continue

        run = result.get("run", {})
        stdout = (run.get("stdout") or "").strip()
        run_stderr = (run.get("stderr") or "").strip()
        exit_code = run.get("code", 0)
        signal = run.get("signal")

        # ── Time-limit exceeded — Piston sends SIGKILL ────────────────────────
        if signal == "SIGKILL":
            if overall_status == "accepted":
                overall_status = "time_limit"
            if failed_case is None:
                failed_case = {
                    "input": tc.input,
                    "expected": tc.expected_output,
                    "actual": stdout,
                }
            continue

        # ── Runtime error (non-zero exit, no signal) ──────────────────────────
        if exit_code != 0:
            if overall_status == "accepted":
                overall_status = "runtime_error"
            if run_stderr:
                stderr_out = run_stderr
            if failed_case is None:
                failed_case = {
                    "input": tc.input,
                    "expected": tc.expected_output,
                    "actual": stdout,
                }
            continue

        # ── Output comparison ─────────────────────────────────────────────────
        expected = tc.expected_output.strip()
        if stdout == expected:
            passed += 1
        else:
            if overall_status == "accepted":
                overall_status = "wrong_answer"
            if failed_case is None:
                failed_case = {
                    "input": tc.input,
                    "expected": expected,
                    "actual": stdout,
                }

    return {
        "status": overall_status,
        "results": {
            "total_test_cases": len(test_cases),
            "passed_test_cases": passed,
            "failed_test_case": failed_case,
            "runtime_ms": 0,   # Piston v2 API doesn't expose per-run timing
            "memory_kb": 0,
            "stderr": stderr_out,
        },
    }
