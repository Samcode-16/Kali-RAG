---
title: Graphics issues on bare-metal installation
description: Troubleshooting steps for GPU and kernel module issues on Kali Linux installed on physical hardware.
icon:
weight: 12
author: ["Soroush Nekoozadeh"]
---

This document covers several common graphics issues that occur when running Kali Linux on bare-metal systems (physical hardware) rather than in virtual machines. Users with NVIDIA graphics cards frequently encounter black screens, login failures, or system instability after kernel updates or driver installations.

## Kernel Update and DKMS Module Issues

When Kali receives frequent kernel updates, users who run full upgrades can see DKMS-backed modules (NVIDIA, VirtualBox, some Wi‑Fi drivers) break if the kernel headers for the new version are not installed. This most commonly appears after a kernel upgrade on a system using NVIDIA graphics: on boot the graphical session fails to start and you may see only a blinking cursor or dash.

This guide provides safe, repeatable methods to keep kernel headers and DKMS modules synchronized, and explains how to properly prepare a system for installing proprietary NVIDIA drivers.

{{% notice info %}}
This guide assumes you have Kali installed on physical hardware (not a live image). It was written for rolling releases — adapt package names and kernel versioning to your environment where necessary.
{{% /notice %}}

#### 1 — Add an APT hook to auto-install headers and rebuild DKMS

Create the file `/etc/apt/apt.conf.d/99-kernel-headers-dkms`. This causes APT to check the highest kernel version in `/lib/modules`, attempt to install missing `linux-headers` for it, and run `dkms autoinstall` if DKMS is present. The hook is conservative: failures to install headers or build modules are ignored so system upgrades are not blocked.

Safe, minimal example (run as root or with sudo):

```console
kali@kali:~$ sudo tee /etc/apt/apt.conf.d/99-kernel-headers-dkms >/dev/null <<'EOF'
DPkg::Post-Invoke {"bash -c 'set -e; newk=$(ls -1 /lib/modules 2>/dev/null | sort -V | tail -1); if [ -n $newk ] && [ ! -d /usr/src/linux-headers-$newk ]; then echo [apt] Installing headers for $newk >&2; apt-get -y install linux-headers-$newk || true; fi; if command -v dkms >/dev/null; then dkms autoinstall -k $newk || true; fi'";};
EOF
kali@kali:~$
```

This helps avoid the common case where a kernel upgrade arrives and the matching headers are not yet installed.


#### 2 — One‑time/manual: install headers and rebuild DKMS for the newest kernel

If you just installed a new kernel and want to run the steps immediately (instead of waiting for the next APT run):

```console
# pick the highest installed kernel (not `uname -r`)
kali@kali:~$ newk=$(ls -1 /lib/modules | sort -V | tail -1)

# install headers for that kernel
kali@kali:~$ sudo apt-get update
[...]
kali@kali:~$ sudo apt-get install -y "linux-headers-$newk" || echo "linux-headers-$newk not available"
[...]
# rebuild DKMS modules for that kernel
kali@kali:~$ if command -v dkms >/dev/null; then
  sudo dkms autoinstall -k "$newk"
fi
```

Tip: if `apt-get install` can't find a header package, check that your APT sources include the correct repositories (rolling vs. archive) and that the kernel package actually provides matching headers.


#### 3 — Optional: tune the GRUB kernel command line

You can change the kernel command line for quieter boots or to work around firmware/ACPI issues. Edit `/etc/default/grub`, update `GRUB_CMDLINE_LINUX_DEFAULT`, then run `update-grub` and reboot to test.

Example (changes boot verbosity and adds stricter ACPI handling):

```console
kali@kali:~$ sudo sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash acpi=strict loglevel=3"/' /etc/default/grub
kali@kali:~$ sudo update-grub
[...]
kali@kali:~$
```
Warning: do not disable ACPI unless you understand your hardware. Disabling ACPI can prevent the kernel from interacting with platform firmware and may cause devices (including the GPU) to not function correctly. Reducing boot verbosity can also make debugging harder.


#### 4 — Disable `nouveau` before installing NVIDIA drivers

Proprietary NVIDIA packages expect `nouveau` to be disabled. To blacklist it now and persistently:

```console
# unload nouveau for the running session (may fail if in use)
kali@kali:~$ sudo modprobe -r nouveau || true
[...]
# blacklist nouveau persistently
kali@kali:~$ echo "blacklist nouveau" | sudo tee /etc/modprobe.d/blacklist-nouveau.conf

# rebuild initramfs so the change takes effect on next boot
kali@kali:~$ sudo update-initramfs -u
[...]
# reboot to make sure nouveau is not loaded on boot
kali@kali:~$ sudo reboot
```

Warning: If your system requires the open-source driver to boot the graphical environment, ensure you have a recovery plan (TTY access, live USB or recovery media) before blacklisting.

Recovery: to undo the blacklist if the system will not boot into the graphical environment, drop to a TTY (Ctrl+Alt+F3) or use a live USB and run:

```bash
kali@kali:~$ sudo rm /etc/modprobe.d/blacklist-nouveau.conf
kali@kali:~$ sudo update-initramfs -u
[...]
sudo reboot
```


#### 5 — Quick steps if you already upgraded and you see a blinking cursor

If you've already updated and the system boots to a blinking cursor, use these steps from a TTY (Ctrl+Alt+F3..F6):

1. Log in with your username and password.
2. Run the following to update packages and attempt to install headers for the running kernel:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y "linux-headers-$(uname -r)" || echo "headers not available for $(uname -r)"
```

3. If you have DKMS installed, rebuild modules for the running kernel:

```bash
sudo dkms autoinstall -k "$(uname -r)" || true
```

4. Reboot:

```bash
sudo reboot
```

## GNOME on Wayland Issues

Starting with GNOME version 49, the built-in support for X11 sessions has been deprecated and disabled by default. This change can cause login issues on systems that were previously relying on X11 sessions. You may encounter a black screen or no login interface, and see the following error in system logs:

```bash
Unit gnome-session-x11@gnome-login.target not found.
```

The recommended solution is to ensure Wayland is properly enabled and configured. First, verify that Wayland is not disabled in your GDM configuration:


```bash
kali@kali:~$ sudo grep -r "Wayland" /etc/gdm3/
/etc/gdm3/daemon.conf:#WaylandEnable=true
kali@kali:~$
```

NVIDIA drivers, especially drivers below version 550.163.01, have several issues loading GNOME on Wayland. Over the time, users reported and proposed various workarounds, but they are likely to be specific to a particular graphics card, driver version, kernel version, etc... We can't really provide a quick "fix it all", but here's a list of options that users found helpful:

* `nvidia_drm.modeset=1` allows the driver to manage displays early during boot or while the system is leaving suspend mode.

* `nvidia_drm.fbdev=1` can be used to force the NVIDIA driver to manage the framebuffer (screen output). Users found it useful with NVIDIA driver older than 540.x.x.

* `nvidia.NVreg_PreserveVideoMemoryAllocations=1` prevents GPU memory from being cleared when the system enters suspend mode. Without this option, NVIDIA drivers erase all video memory allocations on suspend by default. When the system resumes, Wayland and GPU-accelerated applications expect their graphical data to still be present in GPU memory, but because it was erased, some elements fail to load. This parameter preserves video memory allocations across suspend/resume cycles, fixing the issue.

In order to enable these options, edit the file `/etc/default/grub`, and add it to the variable `GRUB_CMDLINE_LINUX_DEFAULT`. For example:

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash acpi=strict loglevel=3 nvidia_drm.modeset=1 nvidia.NVreg_PreserveVideoMemoryAllocations=1"
```

After making changes to `/etc/default/grub`, remember to run:

```console
kali@kali:~$ sudo update-grub
[...]
kali@kali:~$ sudo reboot
```
