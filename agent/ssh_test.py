import os
import paramiko
from dotenv import load_dotenv

load_dotenv()
HOST = os.environ["KALI_HOST"]
USER = os.environ["KALI_USER"]
KEY = os.path.expanduser("~/.ssh/id_ed25519")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # fine for a local VM
client.connect(HOST, username=USER, key_filename=KEY, timeout=10)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out, err = stdout.read().decode(), stderr.read().decode()
    return stdout.channel.recv_exit_status(), out, err

print(run("hostname"))
print(run("systemctl is-active postgresql"))
print(run("journalctl -u ssh -n 3 --no-pager"))
print(run("sudo -n true"))   # should FAIL: the agent user must not have sudo
client.close()