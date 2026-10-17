import json
import tempfile
import unittest
from pathlib import Path

from agent.tools import KaliSession


class FakeSession(KaliSession):
    """Same logic as KaliSession, but commands are recorded instead of sent over SSH."""

    def __init__(self, tmp, replies=None):
        super().__init__(host="fake", log_dir=tmp)
        self.executed = []
        self.replies = replies or {}

    def _exec(self, command, timeout=20):
        self.executed.append(command)
        return self.replies.get(command, (0, "fake output\n", ""))


class TestTools(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.s = FakeSession(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_blocked_commands_never_reach_the_vm(self):
        for cmd in ["rm -rf /", "systemctl restart postgresql", "cat /etc/shadow",
                    "cat /etc/passwd; id", "sudo id"]:
            r = self.s.call_tool("run_readonly", {"cmd": cmd})
            self.assertFalse(r["ok"])
            self.assertTrue(r["blocked"])
        self.assertEqual(self.s.executed, [])

    def test_allowed_command_is_built_safely(self):
        r = self.s.call_tool("run_readonly", {"cmd": "systemctl status ssh"})
        self.assertTrue(r["ok"])
        self.assertEqual(self.s.executed, ["timeout 15 systemctl status ssh"])

    def test_exit_code_is_returned(self):
        s = FakeSession(self._tmp.name, {"timeout 15 systemctl is-active postgresql": (3, "inactive\n", "")})
        r = s.call_tool("run_readonly", {"cmd": "systemctl is-active postgresql"})
        self.assertEqual(r["exit_code"], 3)
        self.assertIn("inactive", r["output"])

    def test_read_file_blocks_sensitive_paths(self):
        self.assertTrue(self.s.call_tool("read_file", {"path": "/etc/hostname"})["ok"])
        r = self.s.call_tool("read_file", {"path": "/etc/shadow"})
        self.assertTrue(r["blocked"])

    def test_check_service_runs_three_commands(self):
        self.s.call_tool("check_service", {"name": "postgresql"})
        self.assertEqual(len(self.s.executed), 3)

    def test_check_service_rejects_injection_in_name(self):
        r = self.s.call_tool("check_service", {"name": "ssh; id"})
        self.assertFalse(r["ok"])
        self.assertEqual(self.s.executed, [])

    def test_search_logs_clamps_line_count(self):
        self.s.call_tool("search_logs", {"unit": "ssh", "lines": 99999})
        self.assertIn("-n 200", self.s.executed[0])

    def test_repeat_detection_and_reset(self):
        args = {"cmd": "df -h"}
        self.assertTrue(self.s.call_tool("run_readonly", args)["ok"])
        again = self.s.call_tool("run_readonly", args)
        self.assertTrue(again.get("repeat"))
        self.assertEqual(len(self.s.executed), 1)
        self.s.reset_repeats()                      # e.g. after a fix was applied
        self.assertTrue(self.s.call_tool("run_readonly", args)["ok"])
        self.assertEqual(len(self.s.executed), 2)

    def test_unknown_tool_and_bad_arguments(self):
        self.assertFalse(self.s.call_tool("format_disk", {})["ok"])
        r = self.s.call_tool("run_readonly", {"wrong_name": 1})
        self.assertFalse(r["ok"])
        self.assertIn("Bad arguments", r["output"])

    def test_secrets_are_redacted_from_output(self):
        s = FakeSession(self._tmp.name, {"timeout 15 cat /etc/hostname": (0, "password=hunter2\n", "")})
        r = s.call_tool("read_file", {"path": "/etc/hostname"})
        self.assertNotIn("hunter2", r["output"])

    def test_every_call_is_logged_including_blocked(self):
        self.s.call_tool("run_readonly", {"cmd": "df -h"})
        self.s.call_tool("run_readonly", {"cmd": "rm -rf /"})
        lines = Path(self.s.log_path).read_text(encoding="utf-8").strip().splitlines()
        entries = [json.loads(x) for x in lines]
        self.assertEqual(len(entries), 2)
        self.assertTrue(entries[1]["blocked"])

    def test_ssh_failure_does_not_crash_the_agent(self):
        class Broken(FakeSession):
            def _exec(self, command, timeout=20):
                raise ConnectionError("connection lost")
        r = Broken(self._tmp.name).call_tool("run_readonly", {"cmd": "df -h"})
        self.assertFalse(r["ok"])
        self.assertIn("Tool failed", r["output"])


if __name__ == "__main__":
    unittest.main()