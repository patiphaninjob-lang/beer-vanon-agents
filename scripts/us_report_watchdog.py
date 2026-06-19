import argparse
import datetime as dt
import json
import os
from pathlib import Path


NON_BLOCKING_ISSUE_PREFIXES = ("fallback_analysis",)
VALID_PHASES = {"premarket", "postmarket"}


def utc_today() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def archive_key(report_date: str, phase: str) -> str:
    return f"{report_date}-{phase}"


def blocking_issues(issues: list) -> list:
    return [
        str(issue)
        for issue in issues
        if not str(issue).startswith(NON_BLOCKING_ISSUE_PREFIXES)
    ]


def evaluate_archive(root: Path, report_date: str, phase: str) -> dict:
    if phase not in VALID_PHASES:
        return {
            "dispatch": False,
            "reason": f"unsupported_phase:{phase}",
            "archive": "",
            "blocking_issues": [],
        }

    archive = root / "docs" / "data" / f"{archive_key(report_date, phase)}.json"
    if not archive.exists():
        return {
            "dispatch": True,
            "reason": "missing_archive",
            "archive": archive.as_posix(),
            "blocking_issues": ["missing_archive"],
        }

    try:
        payload = json.loads(archive.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "dispatch": True,
            "reason": "invalid_archive_json",
            "archive": archive.as_posix(),
            "blocking_issues": [str(exc)],
        }

    health = payload.get("health") or {}
    issues = blocking_issues(health.get("issues") or [])
    if issues:
        return {
            "dispatch": True,
            "reason": "blocking_health_issues",
            "archive": archive.as_posix(),
            "blocking_issues": issues,
        }

    return {
        "dispatch": False,
        "reason": "archive_ok",
        "archive": archive.as_posix(),
        "blocking_issues": [],
    }


def write_github_output(result: dict) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as fh:
        fh.write(f"dispatch={str(result['dispatch']).lower()}\n")
        fh.write(f"reason={result['reason']}\n")
        fh.write(f"archive={result['archive']}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=sorted(VALID_PHASES))
    parser.add_argument("--date", default=utc_today())
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    result = evaluate_archive(Path(args.root), args.date, args.phase)
    write_github_output(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
