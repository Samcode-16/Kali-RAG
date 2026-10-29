"""
Tools the agent can call. Every command goes through agent.safety before it touches the VM,
and every call (allowed or blocked) is written to a JSONL audit log.

Run scripts that import this module from the project root, e.g.  python -m agent.try_tools
"""
import json
import os
from datetime import datetime
from pathlib import Path

from agent.safety import check_command, build_command, clean_output

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


TOOL_DESCRIPTIONS = """\
run_readonly(cmd): run one read-only shell command on the Kali VM. Only allow-listed commands work
    (systemctl status/is-active/is-enabled, journalctl -u, dpkg -s, apt-cache policy, apt-mark showhold,
    df -h, free -h, ps aux, ss -tlnp, ip a, uname -a, cat/ls/head/tail/grep on /etc and /var/log).
    No pipes, redirects, sudo, or shell tricks.
read_file(path): read a file under /etc or /var/log.
search_logs(unit, lines): last N journal lines for a systemd unit (lines max 200, default 50).
check_service(name): is-active, is-enabled and a short status for a systemd service.
check_package(name): dpkg status, apt policy, and any held packages.
search_documentation(query): search the official Kali docs; returns cited excerpts.
"""


class KaliSession:
    def __init__(self, host=None, user=None, key_path=None,
                 log_dir="results/agent_logs", run_label="run"):
        self.host = host or os.environ.get("KALI_HOST")
        self.user = user or os.environ.get("KALI_USER", "agent")
        self.key_path = key_path or os.path.expanduser("~/.ssh/id_ed25519")
        self.client = None
        self.seen = set()
        self.calls = 0
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        self.log_path = Path(log_dir) / f"{run_label}_{datetime.now():%Y%m%d_%H%M%S}.jsonl"

    # ---------------------------------------------------------------- connection
    def connect(self):
        import paramiko
        if not self.host:
            raise RuntimeError("KALI_HOST is not set. Add it to your .env file.")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # acceptable for a local VM
        client.connect(self.host, username=self.user, key_filename=self.key_path, timeout=10)
        self.client = client
        return self

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, *exc):
        self.close()

    def _exec(self, command, timeout=20):
        """Send one prepared command string over SSH. Returns (exit_code, stdout, stderr)."""
        _, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        return stdout.channel.recv_exit_status(), out, err

    # ------------------------------------------------------------------- logging
    def log(self, kind, **data):
        entry = {"ts": datetime.now().isoformat(timespec="seconds"), "kind": kind, **data}
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def reset_repeats(self):
        """Call after a fix is applied, so verification may re-run earlier checks."""
        self.seen.clear()

    # --------------------------------------------------------------------- tools
    def run_readonly(self, cmd):
        verdict = check_command(cmd)
        if not verdict.allowed:
            self.log("tool", tool="run_readonly", cmd=cmd, blocked=True, reason=verdict.reason)
            return {"ok": False, "blocked": True, "output": f"BLOCKED: {verdict.reason}"}
        code, out, err = self._exec(build_command(verdict.argv))
        text = out + (f"\n[stderr]\n{err}" if err.strip() else "")
        text = clean_output(text) or "(no output)"
        self.log("tool", tool="run_readonly", cmd=cmd, blocked=False, exit_code=code, output=text)
        return {"ok": True, "blocked": False, "exit_code": code, "output": text}

    def read_file(self, path):
        return self.run_readonly(f"cat {path}")

    def search_logs(self, unit, lines=50):
        try:
            n = max(1, min(int(lines), 200))
        except (TypeError, ValueError):
            n = 50
        return self.run_readonly(f"journalctl -u {unit} -n {n} --no-pager")

    def check_service(self, name):
        cmds = [f"systemctl is-active {name}",
                f"systemctl is-enabled {name}",
                f"systemctl status {name} --no-pager -n 15"]
        return self._combine(cmds)

    def check_package(self, name):
        cmds = [f"dpkg -s {name}", f"apt-cache policy {name}", "apt-mark showhold"]
        return self._combine(cmds)

    def search_documentation(self, query):
        from retrieval import chunks, hybrid_top, THRESHOLD   # lazy: loading the index is slow
        best, top = hybrid_top(str(query), k=3)
        if best < THRESHOLD:
            out = "No relevant Kali documentation found for that query."
        else:
            out = "\n\n".join(f"[{n}] ({chunks[i][0]})\n{chunks[i][1][:1500]}"
                              for n, i in enumerate(top, 1))
            self.log("tool", tool="search_documentation", query=str(query),
                best_score=round(best, 3), pages=[chunks[i][0] for i in top], output=out[:3000])
        return {"ok": True, "blocked": False, "output": out}

    def _combine(self, cmds):
        parts, ok = [], True
        for c in cmds:
            r = self.run_readonly(c)
            ok = ok and r["ok"]
            parts.append(f"$ {c}\n[exit {r.get('exit_code', '-')}] {r['output']}")
        return {"ok": ok, "blocked": False, "output": "\n\n".join(parts)}

    # ---------------------------------------------------------------- dispatcher
    def call_tool(self, name, args=None):
        """The single entry point the agent loop uses. Never raises; always returns a dict."""
        args = args if isinstance(args, dict) else {}
        fn = self.TOOLS.get(name)
        if fn is None:
            return {"ok": False, "output": f"Unknown tool {name!r}. Available: {', '.join(self.TOOLS)}"}

        key = name + json.dumps(args, sort_keys=True, default=str)
        if key in self.seen:
            self.log("tool", tool=name, args=args, repeat=True)
            return {"ok": False, "repeat": True,
                    "output": "You already made this exact call and nothing has changed since. "
                              "Try a different check, or state your conclusion."}
        self.seen.add(key)
        self.calls += 1

        try:
            return fn(self, **args)
        except TypeError as e:
            return {"ok": False, "output": f"Bad arguments for {name}: {e}"}
        except Exception as e:                      # SSH drop, timeout, etc.
            self.log("tool_error", tool=name, args=args, error=f"{type(e).__name__}: {e}")
            return {"ok": False, "output": f"Tool failed: {type(e).__name__}"}


KaliSession.TOOLS = {
    "run_readonly": KaliSession.run_readonly,
    "read_file": KaliSession.read_file,
    "search_logs": KaliSession.search_logs,
    "check_service": KaliSession.check_service,
    "check_package": KaliSession.check_package,
    "search_documentation": KaliSession.search_documentation,
}