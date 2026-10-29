---
title: SSH Configuration
description:
icon:
weight:
author: ["arnaudr", "gamb1t",]
---

## SSH client: Wide Compatibility vs Strong Security

Since our release of [Kali Linux 2022.1](/blog/kali-linux-2022-1-release/) it is possible to easily configure the SSH client for **wider compatibility** to allow Kali to talk to as many SSH servers as possible. In wide compatibility mode, legacy key exchange algorithms _(such as diffie-hellman-*-sha1)_ and old ciphers _(such as CBC)_ are **enabled**. As a result, tools used inside of Kali are able to communicate using these outdated methods. _This is done to help increase Kali's ability to talk to older, obsolete SSH servers that are still using these older protocols. Older services using this may be at end of life, thus increasing the chances of discovering vulnerabilities or other problems_.

Note that this is _not the default_. Out of the box, the SSH client in Kali Linux is configured for **Strong Security** to enforce communication over more secure channels.

This setting can be changed easily using the `kali-tweaks` tool. Simply:

- Open a terminal and run `kali-tweaks`.
- From there, select the _Hardening_ menu.
- Now you can choose between **Strong Security** _(the default)_ and **Wide Compatibility**.

_Note: This is achieved by creating or deleting the configuration file `/etc/ssh/ssh_config.d/kali-wide-compat.conf`._

## SSH client: Restoring removed functionality via the ssh1 package

As software and security advance, OpenSSH will remove features that are no longer commonly used from the default package. The Wide Compatibility mode mentioned above can enable features that are _present in the package, but disabled by default_. However, features that are really too old end up being completely removed. At this point, one has to resort to another SSH client: `ssh1`.

This package is, in practicality, OpenSSH frozen at version 7.5 (released in March 2017). It provides binaries for `ssh`, `scp`, and `ssh-keygen`, under the respective names `ssh1`, `scp1` and `ssh-keygen1`. Why version 7.5, you might ask? Because this is the last release of OpenSSH that supports the **SSH v.1 protocol**. And as time passed, this old version became useful to keep using other removed features, notably support for **DSA keys** that was removed in version 9.8.

Since the release of [Kali Linux 2024.4](/blog/kali-linux-2024-4-release/), the package `openssh-client-ssh1` is installed by default. For others who upgraded their system and need this functionality, it's easy to just install the package:

```console
kali@kali:~$ sudo apt update
[...]
kali@kali:~$
kali@kali:~$ sudo apt install -y openssh-client-ssh1
[...]
kali@kali:~$
kali@kali:~$ dpkg --listfiles openssh-client-ssh1 | grep bin/
/usr/bin/scp1
/usr/bin/ssh-keygen1
/usr/bin/ssh1
kali@kali:~$
kali@kali:~$ ssh1 -V
OpenSSH_7.5p1 Debian-17, OpenSSL 3.3.2 3 Sep 2024
kali@kali:~$
```

## SSH client: Support for GSS-API

<!-- Add link to release: [Kali Linux 2026.3](/blog/kali-linux-2026-3-release/ -->

Starting with Kali Linux 2026.3, the SSH client doesn't include support for the GSS-API key exchange anymore.

For those who need this functionality, it's possible to get it back by installing the alternative package `openssh-client-gssapi`. In practical terms, this package should be the same as the stock openssh package, but with the GSS-API patch applied. More information can be found in the announcement at <https://lists.debian.org/debian-devel/2024/04/msg00044.html>.

So, in order to restore GSS-API support in your SSH client, just run the following:

```console
kali@kali:~$ sudo apt update
[...]
kali@kali:~$
kali@kali:~$ sudo apt install -y openssh-client-gssapi
Installing:                     
  openssh-client-gssapi
[...]
REMOVING:
  openssh-client
[...]
Continue? [Y/n]
```

Note that the package `openssh-client-gssapi` _replaces_ `openssh-client`, and the other way around, they are not co-installable.

## SSH server: automatic host keys generation

Since the release of [Kali Linux 2022.1](/blog/kali-linux-2022-1-release/), the SSH host keys are automatically generated if missing. This is achieved via the systemd service `regenerate-ssh-host-keys`.

So what are SSH host keys exactly? Those keys are required for the SSH server to be functional. They are supposed to be unique for each machine. Those keys can be found under `/etc/ssh` and are named `ssh_host_*_key`. This is how it usually looks like:

```console
kali@kali:~$ ls -l /etc/ssh/ssh_host_*
-rw------- 1 root root 1373 Feb  3 23:50 /etc/ssh/ssh_host_dsa_key
-rw-r--r-- 1 root root  599 Feb  3 23:50 /etc/ssh/ssh_host_dsa_key.pub
-rw------- 1 root root  505 Feb  3 23:50 /etc/ssh/ssh_host_ecdsa_key
-rw-r--r-- 1 root root  171 Feb  3 23:50 /etc/ssh/ssh_host_ecdsa_key.pub
-rw------- 1 root root  399 Feb  3 23:50 /etc/ssh/ssh_host_ed25519_key
-rw-r--r-- 1 root root   91 Feb  3 23:50 /etc/ssh/ssh_host_ed25519_key.pub
-rw------- 1 root root 2590 Feb  3 23:50 /etc/ssh/ssh_host_rsa_key
-rw-r--r-- 1 root root  563 Feb  3 23:50 /etc/ssh/ssh_host_rsa_key.pub
```

Since these keys must be unique for each machine, they can't be embedded in pre-built Kali images such as the Kali Linux [VM images](/get-kali/#kali-virtual-machines) or the [ARM images](/get-kali/#kali-arm). It's usually up to the user to create those keys before running the SSH server for the first time. However, for most users who are not familiar with SSH, this is a hurdle, as they are not aware of this technical detail.

To make it easier, Kali Linux now comes with a systemd service that takes care of that automatically, and generate those keys if they are missing. In theory, it's only during a first boot of a pre-built image that the service kicks in. On subsequent boots, the keys already exist and therefore nothing happens. This may not be the case for users who may remove these keys themselves.

For those who are not comfortable with this automatic behavior, it's very simple and straightforward to disable it:

```console
kali@kali:~$ sudo systemctl disable regenerate-ssh-host-keys.service
```
