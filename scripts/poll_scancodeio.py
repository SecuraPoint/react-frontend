#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time
import json
from typing import Optional
import requests

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_project(base_url: str, token: str, project_uuid: str, timeout: float = 10.0) -> dict:
    url = f"{base_url.rstrip('/')}/api/projects/{project_uuid}/"
    headers = {"Authorization": f"Token {token}", "Accept": "application/json"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def extract_run_status(project: dict) -> Optional[str]:
    runs = project.get("runs") or []
    if not runs:
        return None
    return runs[0].get("status")

def main():
    parser = argparse.ArgumentParser(description="Poll ScanCode.io project until success.")
    parser.add_argument("--base-url", default=os.getenv("SCANCODEIO_BASE"), required=False,
                        help="Base URL of ScanCode.io (e.g., https://hetzner.scancodeio.securapoint.de)")
    parser.add_argument("--token", default=os.getenv("SCANCODEIO_TOKEN"), required=False,
                        help="API token for ScanCode.io")
    parser.add_argument("--project-uuid", default=os.getenv("SCANCODEIO_PROJECT_UUID"), required=False,
                        help="Project UUID to poll")
    parser.add_argument("--interval", type=float, default=float(os.getenv("POLL_INTERVAL_SEC", "10")),
                        help="Polling interval in seconds")
    parser.add_argument("--timeout", type=float, default=float(os.getenv("POLL_TIMEOUT_SEC", "7200")),
                        help="Overall timeout in seconds (default 2h)")
    parser.add_argument("--request-timeout", type=float, default=15.0,
                        help="Per-request timeout in seconds")
    args = parser.parse_args()

    missing = []
    if not args.base_url: missing.append("SCANCODEIO_BASE/--base-url")
    if not args.token: missing.append("SCANCODEIO_TOKEN/--token")
    if not args.project_uuid: missing.append("SCANCODEIO_PROJECT_UUID/--project-uuid")
    if missing:
        eprint(f"Missing required settings: {', '.join(missing)}")
        sys.exit(2)

    start = time.monotonic()
    last_status = None
    eprint(f"Polling ScanCode.io project {args.project_uuid} @ {args.base_url} every {args.interval:.0f}s (timeout {args.timeout:.0f}s)…")

    # Acceptable terminal states; treat anything other than 'success' as failure
    terminal_success = {"success"}
    terminal_failure = {"failure", "stopped", "aborted", "error"}

    # Non-started states to keep polling
    in_progress_states = {"queued", "not_started", "running", "started", "pending"}

    while True:
        elapsed = time.monotonic() - start
        if elapsed > args.timeout:
            eprint("Timed out while waiting for ScanCode.io run to finish.")
            sys.exit(124)

        try:
            project = get_project(args.base_url, args.token, args.project_uuid, timeout=args.request_timeout)
        except requests.HTTPError as ex:
            code = ex.response.status_code if ex.response is not None else "?"
            eprint(f"HTTP error while polling project: {code}")
            time.sleep(args.interval)
            continue
        except requests.RequestException as ex:
            eprint(f"Network error while polling project: {ex}")
            time.sleep(args.interval)
            continue

        status = extract_run_status(project) or "unknown"
        if status != last_status:
            eprint(f"Run status: {status}")
            last_status = status

        if status in terminal_success:
            # Optionally expose data to GitHub Actions
            run_uuid = (project.get("runs") or [{}])[0].get("uuid", "")
            results_url = project.get("results_url", "")
            summary_url = project.get("summary_url", "")
            # Write to $GITHUB_OUTPUT if available
            gh_out = os.getenv("GITHUB_OUTPUT")
            if gh_out:
                with open(gh_out, "a", encoding="utf-8") as fh:
                    fh.write(f"run_status={status}\n")
                    fh.write(f"run_uuid={run_uuid}\n")
                    fh.write(f"results_url={results_url}\n")
                    fh.write(f"summary_url={summary_url}\n")
            # Also print a compact JSON line for logs (no secrets)
            print(json.dumps({
                "status": status,
                "run_uuid": run_uuid,
                "results_url": results_url,
                "summary_url": summary_url
            }))
            sys.exit(0)

        if status in terminal_failure:
            eprint("ScanCode.io run ended in a failure state.")
            eprint(json.dumps(project, indent=2))
            sys.exit(1)

        # Unknown or in-progress → keep polling
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
