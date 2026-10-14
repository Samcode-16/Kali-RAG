import unittest
from agent.safety import check_command, build_command, redact, truncate, check_path

ALLOWED = [
    "systemctl status postgresql",
    "systemctl is-active ssh",
    "systemctl is-enabled postgresql",
    "systemctl list-units --failed --no-pager",
    "journalctl -u postgresql -n 50 --no-pager",
    'journalctl -u ssh --since "1 hour ago" --no-pager',
    "dpkg -s metasploit-framework",
    "apt-mark showhold",
    "apt-cache policy kali-archive-keyring",
    "df -h",
    "cat /etc/os-release",
    "ls -la /etc/apt",
    "tail -n 20 /var/log/dpkg.log",
    "grep -i error /var/log/dpkg.log",
    "ss -tlnp",
    "msfdb status",
    "ps aux",
    "free -h",
]

BLOCKED = [
    "",
    "   ",
    "echo hi",
    "rm -rf /",
    "sudo systemctl status ssh",
    "systemctl restart postgresql",
    "systemctl stop ssh",
    "systemctl status ssh && id",
    "systemctl status ssh; id",
    "systemctl status ssh`id`",
    "ps aux | grep ssh",
    "cat /etc/hostname > /tmp/x",
    "ls $(whoami)",
    "cat /etc/passwd; id",
    "cat /etc/shadow",
    "cat /etc/../etc/shadow",
    "cat /etc/sudoers",
    "cat /etc/ssh/ssh_host_rsa_key",
    "cat /home/kali/.bash_history",
    "head -n 5 /etc/hostname /etc/shadow",
    "journalctl -f",
    "journalctl -u ssh -o json-pretty",
    "apt install nmap",
    "apt-mark hold nmap",
    "dpkg -i evil.deb",
    "bash -c id",
    "curl http://example.com",
    "msfdb init",
    "grep -r password /etc",
    "cat relative/path",
    "x" * 400,
]


class TestAllowList(unittest.TestCase):
    def test_allowed(self):
        for cmd in ALLOWED:
            with self.subTest(cmd=cmd):
                v = check_command(cmd)
                self.assertTrue(v.allowed, f"should be allowed but was blocked: {v.reason}")

    def test_blocked(self):
        for cmd in BLOCKED:
            with self.subTest(cmd=cmd[:60]):
                self.assertFalse(check_command(cmd).allowed, "should have been blocked")


class TestHelpers(unittest.TestCase):
    def test_build_command_quotes_everything(self):
        self.assertEqual(build_command(["cat", "/etc/hosts"]), "timeout 15 cat /etc/hosts")
        self.assertIn("'1 hour ago'", build_command(["journalctl", "--since", "1 hour ago"]))

    def test_paths(self):
        self.assertIsNone(check_path("/etc/hosts"))
        self.assertIsNotNone(check_path("/root/.bashrc"))
        self.assertIsNotNone(check_path("/etc/shadow"))

    def test_redact(self):
        self.assertNotIn("hunter2", redact("password=hunter2"))
        self.assertNotIn("AIzaSyABCDEFGHIJKLMNOPQRSTUV", redact("key AIzaSyABCDEFGHIJKLMNOPQRSTUV"))

    def test_truncate_keeps_both_ends(self):
        out = truncate("A" * 3000 + "B" * 3000, limit=1000)
        self.assertTrue(out.startswith("A"))
        self.assertTrue(out.endswith("B"))
        self.assertIn("omitted", out)
        self.assertLess(len(out), 1100)


if __name__ == "__main__":
    unittest.main()