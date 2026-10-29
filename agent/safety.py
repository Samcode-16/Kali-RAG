"""
Safety layer for the Kali troubleshooting agent.

Design rules
------------
1. ALLOW-LIST, not deny-list: a command runs only if it matches a known read-only pattern.
2. Shell metacharacters are rejected outright. paramiko's exec_command hands the string to the
   remote user's shell, so blocking them (and quoting every argument) is essential.
3. File access is limited to a few directories, and sensitive names are always blocked.
4. Output is truncated and redacted before it is shown to the LLM or written to logs.

State-changing commands (apt install, systemctl restart, edits) are NOT handled here.
They will go through a separate propose_fix -> human approval path.
"""
import posixpath
import re
import shlex
from dataclasses import dataclass, field

MAX_CMD_LEN = 300

# Any of these anywhere in the raw command string => rejected.
FORBIDDEN_CHARS = [";", "&", "|", ">", "<", "`", "$", "\n", "\r", "\\",
                   "*", "?", "(", ")", "{", "}", "~", "!", "#"]

UNIT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9@._:\-]*$")
PKG_RE = re.compile(r"^[a-z0-9][a-z0-9+.\-:]*$")
INT_RE = re.compile(r"^\d{1,4}$")
SINCE_RE = re.compile(r"^[\w:\- ]{1,30}$")
PRIORITY_RE = re.compile(r"^(emerg|alert|crit|err|warning|notice|info|debug|[0-7])$")
SS_FLAGS_RE = re.compile(r"^-[tulnpa]{1,6}$")

# ---------------------------------------------------------------- path policy
ALLOWED_PREFIXES = (
    "/etc/",
    "/var/log/",
    "/usr/share/metasploit-framework/config/",
)
ALLOWED_EXACT = {"/etc", "/var/log", "/proc/meminfo", "/proc/cpuinfo", "/proc/version"}
BLOCKED_NAME_RE = re.compile(
    r"(shadow|gshadow|sudoers|ssh_host_|id_rsa|id_ed25519|id_ecdsa|\.ssh|\.env|"
    r"private|secret|\.pem|\.key|\.kdbx|bash_history)", re.I)


def check_path(path: str):
    """Return None if the path may be read, otherwise a reason string."""
    if not path.startswith("/"):
        return "path must be absolute"
    if ".." in path.split("/"):
        return "path traversal is not allowed"
    p = posixpath.normpath(path)
    if BLOCKED_NAME_RE.search(p):
        return f"path {p} looks sensitive and is blocked"
    if p in ALLOWED_EXACT or any(p.startswith(x) for x in ALLOWED_PREFIXES):
        return None
    return f"path {p} is outside the allowed directories"


# ------------------------------------------------------------ argument helpers
def _flags_and_names(args, ok_flags, name_re, int_flags=(), value_flags=None):
    """Validate args made of known flags, flags with values, and (optionally) names."""
    value_flags = value_flags or {}
    i = 0
    while i < len(args):
        t = args[i]
        if t in ok_flags:
            i += 1
        elif t in int_flags:
            if i + 1 >= len(args) or not INT_RE.match(args[i + 1]):
                return f"{t} needs a number"
            i += 2
        elif t in value_flags:
            if i + 1 >= len(args) or not value_flags[t].match(args[i + 1]):
                return f"{t} needs a valid value"
            i += 2
        elif t.startswith("-"):
            return f"flag {t} is not allowed"
        elif name_re is None or not name_re.match(t):
            return f"argument {t!r} is not allowed"
        else:
            i += 1
    return None


def _pathcmd(args, ok_flags=(), int_flags=()):
    paths, i = [], 0
    while i < len(args):
        t = args[i]
        if t in ok_flags:
            i += 1
        elif t in int_flags:
            if i + 1 >= len(args) or not INT_RE.match(args[i + 1]):
                return f"{t} needs a number"
            i += 2
        elif t.startswith("-"):
            return f"flag {t} is not allowed"
        else:
            paths.append(t)
            i += 1
    if not paths:
        return "a path is required"
    for p in paths:
        err = check_path(p)
        if err:
            return err
    return None


# ------------------------------------------------------------- per-command rules
def _systemctl(a):
    if not a:
        return "missing subcommand"
    sub, rest = a[0], a[1:]
    if sub in {"status", "is-active", "is-enabled", "is-failed", "show", "cat"}:
        return _flags_and_names(rest, {"--no-pager", "-l", "--full"}, UNIT_RE, int_flags={"-n"})
    if sub in {"list-units", "list-unit-files"}:
        return _flags_and_names(rest, {"--no-pager", "--failed", "--type=service",
                                       "--state=running", "--state=failed"}, None)
    return f"systemctl {sub} is not allowed"


def _journalctl(a):
    return _flags_and_names(
        a, {"--no-pager", "-b", "-x"}, None, int_flags={"-n"},
        value_flags={"-u": UNIT_RE, "-p": PRIORITY_RE, "--since": SINCE_RE})


def _dpkg(a):
    if len(a) == 1 and a[0] in {"-l", "--audit"}:
        return None
    if len(a) == 2 and a[0] in {"-s", "-l", "-L", "--status", "--listfiles"} and PKG_RE.match(a[1]):
        return None
    return "dpkg allows only: -s PACKAGE or -L PACKAGE (one package at a time), -l [PACKAGE], --audit"


def _apt_mark(a):
    return None if a == ["showhold"] else "only 'apt-mark showhold' is allowed"


def _apt_cache(a):
    if len(a) == 2 and a[0] in {"policy", "show", "madison", "depends"} and PKG_RE.match(a[1]):
        return None
    return "that apt-cache usage is not allowed"


def _no_args(a):
    return None if not a else "this command takes no arguments here"


def _flags_only(ok):
    return lambda a: _flags_and_names(a, ok, None)


def _ps(a):
    return None if a in (["aux"], ["-ef"]) else "only 'ps aux' or 'ps -ef' is allowed"


def _ss(a):
    if len(a) == 1 and SS_FLAGS_RE.match(a[0]):
        return None
    return "that ss usage is not allowed"


def _ip(a):
    return None if tuple(a) in {("a",), ("addr",), ("link",), ("route",), ("r",)} else "that ip usage is not allowed"


def _lsb(a):
    return None if a == ["-a"] else "only 'lsb_release -a' is allowed"


def _msfdb(a):
    return None if a == ["status"] else "only 'msfdb status' is allowed"


def _grep(a):
    ok, i, rest = {"-i", "-n", "-c"}, 0, []
    while i < len(a):
        if a[i] in ok:
            i += 1
        elif a[i].startswith("-"):
            return f"flag {a[i]} is not allowed"
        else:
            rest.append(a[i])
            i += 1
    if len(rest) != 2:
        return "usage: grep [-i -n -c] PATTERN FILE"
    if len(rest[0]) > 80:
        return "pattern too long"
    return check_path(rest[1])


RULES = {
    "systemctl": _systemctl,
    "journalctl": _journalctl,
    "dpkg": _dpkg,
    "apt-mark": _apt_mark,
    "apt-cache": _apt_cache,
    "df": _flags_only({"-h", "-i", "-T"}),
    "free": _flags_only({"-h", "-m"}),
    "uname": _flags_only({"-a", "-r", "-m"}),
    "uptime": _no_args,
    "hostname": _no_args,
    "whoami": _no_args,
    "id": _no_args,
    "pg_lsclusters": _no_args,
    "ps": _ps,
    "ss": _ss,
    "ip": _ip,
    "lsb_release": _lsb,
    "msfdb": _msfdb,
    "grep": _grep,
    "cat": lambda a: _pathcmd(a),
    "stat": lambda a: _pathcmd(a),
    "ls": lambda a: _pathcmd(a, ok_flags={"-l", "-a", "-la", "-lh", "-lah", "-h"}),
    "head": lambda a: _pathcmd(a, int_flags={"-n"}),
    "tail": lambda a: _pathcmd(a, int_flags={"-n"}),
}


# ------------------------------------------------------------------ public API
@dataclass
class Verdict:
    allowed: bool
    reason: str = ""
    argv: list = field(default_factory=list)


def check_command(cmd: str) -> Verdict:
    """Decide whether a read-only command may run."""
    if not cmd or not cmd.strip():
        return Verdict(False, "empty command")
    if len(cmd) > MAX_CMD_LEN:
        return Verdict(False, "command too long")
    for ch in FORBIDDEN_CHARS:
        if ch in cmd:
            return Verdict(False, f"character {ch!r} is not allowed")
    try:
        argv = shlex.split(cmd)
    except ValueError as e:
        return Verdict(False, f"cannot parse command: {e}")
    if not argv:
        return Verdict(False, "empty command")
    name, args = argv[0], argv[1:]
    if name not in RULES:
        return Verdict(False, f"command {name!r} is not on the allow-list")
    err = RULES[name](args)
    if err:
        return Verdict(False, err)
    return Verdict(True, "ok", argv)


def build_command(argv, timeout_s: int = 15) -> str:
    """Build the string sent over SSH: every argument quoted, with a hard timeout."""
    return f"timeout {timeout_s} " + " ".join(shlex.quote(x) for x in argv)


# ------------------------------------------------------------ output handling
_REDACTIONS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
     "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{20,}"), "[REDACTED_API_KEY]"),
    (re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\b(\s*[=:]\s*)\S+"),
     r"\1\2[REDACTED]"),
]


def redact(text: str) -> str:
    for pattern, repl in _REDACTIONS:
        text = pattern.sub(repl, text)
    return text


def truncate(text: str, limit: int = 4000) -> str:
    """Keep the start and end of long output so the model still sees the final lines."""
    if len(text) <= limit:
        return text
    half = limit // 2
    return text[:half] + f"\n...[{len(text) - limit} characters omitted]...\n" + text[-half:]


def clean_output(text: str, limit: int = 4000) -> str:
    return truncate(redact(text), limit)