import asyncio
import base64

import httpx

from app.config import settings

LANGUAGE_MAP = {
    "python": 71,
    "java": 62,
    "javascript": 63,
}

STATUS_MAP = {
    1: "pending",
    2: "pending",
    3: "accepted",
    4: "wrong_answer",
    5: "time_limit",
    6: "compile_error",
    7: "runtime_error",
    8: "runtime_error",
    9: "runtime_error",
    10: "runtime_error",
    11: "runtime_error",
    12: "runtime_error",
    13: "runtime_error",
    14: "runtime_error",
}


def _encode(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def _decode(s: str | None) -> str:
    if not s:
        return ""
    return base64.b64decode(s).decode(errors="replace")


async def execute_code(code: str, language: str, test_cases: list) -> dict:
    lang_id = LANGUAGE_MAP.get(language)
    if lang_id is None:
        raise ValueError(f"Unsupported language: {language}")

    submissions = [
        {
            "source_code": _encode(code),
            "language_id": lang_id,
            "stdin": _encode(tc.input),
            "expected_output": _encode(tc.expected_output),
            "cpu_time_limit": settings.judge0_cpu_limit,
            "memory_limit": settings.judge0_memory_limit,
            "base64_encoded": True,
        }
        for tc in test_cases
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.judge0_url}/submissions/batch?base64_encoded=true",
            json={"submissions": submissions},
        )
        resp.raise_for_status()
        tokens = [s["token"] for s in resp.json()]
        results = await _poll_results(client, tokens)

    return _aggregate_results(results, test_cases)


async def _poll_results(client: httpx.AsyncClient, tokens: list[str]) -> list[dict]:
    token_str = ",".join(tokens)
    for _ in range(20):  # max ~10s of polling
        await asyncio.sleep(0.5)
        resp = await client.get(
            f"{settings.judge0_url}/submissions/batch",
            params={"tokens": token_str, "base64_encoded": "true",
                    "fields": "token,status,stdout,stderr,time,memory,compile_output"},
        )
        resp.raise_for_status()
        data = resp.json()["submissions"]
        # Status IDs 1 & 2 mean still processing
        if all(s["status"]["id"] not in (1, 2) for s in data):
            return data
    return data  # return whatever we have after timeout


def _aggregate_results(judge0_results: list[dict], test_cases: list) -> dict:
    passed = 0
    failed_case = None
    overall_status = "accepted"
    stderr = ""
    runtime_ms = 0
    memory_kb = 0

    for i, result in enumerate(judge0_results):
        sid = result["status"]["id"]
        status = STATUS_MAP.get(sid, "runtime_error")

        if result.get("time"):
            runtime_ms = max(runtime_ms, int(float(result["time"]) * 1000))
        if result.get("memory"):
            memory_kb = max(memory_kb, int(result["memory"]))
        if result.get("stderr"):
            stderr = _decode(result["stderr"])
        if result.get("compile_output"):
            stderr = _decode(result["compile_output"])

        if status == "accepted":
            passed += 1
        else:
            if overall_status == "accepted":
                overall_status = status
            if failed_case is None:
                actual_output = _decode(result.get("stdout", "")).strip()
                failed_case = {
                    "input": test_cases[i].input,
                    "expected": test_cases[i].expected_output,
                    "actual": actual_output,
                }

    results = {
        "total_test_cases": len(judge0_results),
        "passed_test_cases": passed,
        "failed_test_case": failed_case,
        "runtime_ms": runtime_ms,
        "memory_kb": memory_kb,
        "stderr": stderr,
    }
    return {"status": overall_status, "results": results}
