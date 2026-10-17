"""Live smoke test. Run from the project root:  python -m agent.try_tools"""
from agent.tools import KaliSession

CALLS = [
    ("check_service", {"name": "postgresql"}),
    ("run_readonly", {"cmd": "df -h"}),
    ("read_file", {"path": "/etc/os-release"}),
    ("search_logs", {"unit": "ssh", "lines": 5}),
    ("check_package", {"name": "metasploit-framework"}),
    ("run_readonly", {"cmd": "cat /etc/shadow"}),                 # must be BLOCKED
    ("run_readonly", {"cmd": "systemctl restart postgresql"}),    # must be BLOCKED
    ("run_readonly", {"cmd": "df -h"}),                           # must be flagged as a repeat
    ("search_documentation", {"query": "msfdb init fails and postgresql is not running"}),
]

with KaliSession(run_label="smoke") as session:
    for name, args in CALLS:
        result = session.call_tool(name, args)
        print(f"\n=== {name} {args}")
        print(result["output"][:600])
    print("\nAudit log written to:", session.log_path)