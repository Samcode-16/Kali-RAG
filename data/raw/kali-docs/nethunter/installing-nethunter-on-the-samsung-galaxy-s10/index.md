---
title: Installing NetHunter on the Samsung Galaxy S10
description:
icon:
weight:
author: ["v0lk3n","yesimxev",]
---


> This installation guide and files used is for Samsung Galaxy S10 Exynos9820 version.

## Features

| Feature  | Supported |
| :--------------- | -----:|
| BT_RFCOMM | ✅ |
| INTERNAL_BT | ✅ |
| RTL_BT | ✅ |
| HID-4 | ✅ |
| Injection | ✅ |
| ATH9K_HTC | ✅ |
| RTL88XX | ✅ |
| RTL8812AU | ✅ |
| RTL8821AU | ✅ |
| RTL8814AU | ✅ |
| RTL8188EUS (Module) | ✅ |
| RTL88x2BU | ✅ |
| NFS | ✅ |
| CAN (optional modules included) | ✅ |
| Nexmon Monitor | ✅ |
| Nexmon Injection | ✅ |
| WiFi 5Ghz | ✅ |

> All the configuration that can be found in porting guide has been applied.

## Supported Version

| ROM  | Status |
| :--------------- | -----:|
| [LineageOS 21 (A14)](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/tree/nethunter-lineage-21) | Old |
| [LineageOS 22.1 (A15)](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/tree/nethunter-lineage-22.1) | Old |
| [LineageOS 22.2 (A15)](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/tree/nethunter-lineage-22.2) | Old |
| [LineageOS 23.0 (A16)](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/tree/nethunter-lineage-23.0) | Old |
| [LineageOS 23.2 (A16)](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/tree/nethunter-lineage-23.2) | New |

> This guide will use LineageOS 22.2 but have same install process than other versions

# Installation

Let's start installation. You will walk through the following steps :
- Flash Stock Rom
- OEM Unlocking
- Flash LineageOS and Recovery
- Root the device
- Install Magisk Modules
- Flash Kali Nethunter
- Flash bootloader removing warning at boot

## Flash Stock Rom

If you need to roll back to stock, or wish to have a clean start for installation (recommended). If you have the latest update installed and don't want a clean flash, skip to the next step.

Download your firmware here: [sammobile.com/samsung/galaxy-s10/firmware/SM-G973F/](https://www.sammobile.com/samsung/galaxy-s10/firmware/SM-G973F/)

Unzip the content and you will end with something like this :

```plaintext
AP_G973FXXSGHWC1_CL25257816_QB62768582_REV01_user_low_ship_meta_OS12.tar.md5
BL_G973FXXSGHWC1_CL25257816_QB62768582_REV01_user_low_ship.tar.md5
CP_G973FXXSGHWB3_CP23788344_CL25257816_QB62585640_REV01_user_low_ship.tar.md5
CSC_OXM_G973FOXMGHWA3_CL25257816_QB61057831_REV01_user_low_ship.tar.md5 <= (Wipe data / Factory reset RECOMMENDED)
HOME_CSC_OXM_G973FOXMGHWA3_CL25257816_QB61057831_REV01_user_low_ship.tar.md5 <= (Keep your data)
```

Boot the phone to Download mode, if you fail to do it because it try to boot even without OS, just wait the boot to automatically go to download mode.

Flash the stock ROM, example on Linux using odin4: [github.com/Adrilaw/OdinV4(https://github.com/Adrilaw/OdinV4)

## OEM Unlocking

To unlock OEM you first need to enable Developer mode.

Open "Settings > About phone > Software Information", then spam click on "Build Number" until enabling Developer Mode.

Developer Mode should appear in "Settings".

Inside Developer Mode, search for OEM unlocking option and enable it. Go into fastboot, long press on "Vol+" then "Vol+" to accept OEM unlocking and wipe the phone.

> If you don't see OEM Unlocking option, you can try some workaround like modify Date/Time of the device. Feel free to search on google about this.

## USB Debugging

Boot your device, do initial setup. Enable Developer Mode again and connect to Wi-Fi.

Open "Settings > About phone > Software Information", then spam click on "Build Number" until enabling Developer Mode.

In developer mode, confirm that it says "Bootloader is unlocked" under OEM unlocking. Enable USB Debugging.

## ROM Flashing

Download LineageOS build, vbmeta, Recovery and MindTheGapps.

LineageOS 22.2: [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/lineage-22.2-20250627-nightly-beyond1lte-signed.zip)

Recovery: [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/recovery.img)

vbmeta: [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/vbmeta.img)

MindTheGapps: [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/MindTheGapps-15.0.0-arm64-20250214_082511.zip)

### Flash Recovery

Boot your device in Download mode using the "Vol- and Bixby key" while connecting to PC with USB cable. Flash recovery using Heimdall, you can follow the [LineageOS install guide](https://wiki.lineageos.org/devices/beyond1lte/install/#preparing-for-installation) for that part.

```plaintext
heimdall flash --RECOVERY recovery.img --VBMETA vbmeta.img --no-reboot
```

### Flash LineageOS ROM

Once the recovery flashed, reboot your device by holding "Vol- and Power key" for 7 seconds, and then directly boot to recovery by holding "Vol+, Bixby and Power key" so recovery won't be wiped.

Once booted into Recovery, navigate to "Factory reset" and Format everything.

Go back, and navigate to "Apply update > Apply from ADB" and flash LineageOS build using adb sideload.

```plaintext
adb -d sideload lineage-22.2-20250627-nightly-beyond1lte-signed.zip
```

Now flash MindTheGapps, "Apply update > Apply from ADB".

```plaintext
adb -d sideload MindTheGapps-15.0.0-arm64-20250214_082511.zip
```

You will have a warning on your phone saying "Signature verification failed Install anyway?" press "Yes", and wait for MindTheGapps flashing to complete.

Once finished, press "Reboot System Now" and do initial setup again. Connect to WiFi (needed for rooting step).

Enable Developer Mode again.

Open "Settings > About phone > Software Information", then spam click on "Build Number" until enabling Developer Mode.

Inside Developer Mode, enable USB Debugging.

> For a better and easier experience i suggest to enable advanced reboot "System > Button > Power Menu > Advanced Reboot". This is a great way to boot in Download/Recovery when needed.

## Rooting

Download Magisk 28.1.

> At time of writing this guide, the latest Magisk is 29 but it come with a lot of issue for Kali Nethunter. That's why you should use 28.1 instead.

Magisk 28.1: [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/Magisk-v28.1.zip)

Reboot to recovery and navigate to "Apply update > Apply from ADB" and flash Magisk.

```plaintext
adb -d sideload Magisk-v28.1.zip
```

You will have a warning on your phone saying "Signature verification failed Install anyway?" press "Yes", and wait for Magisk flashing to complete.

Once flashing complete, reboot to system and open Magisk app.

It will prompt to finish the installation, say yes and chose "Direct Installation" as method.

When finished, reboot.

## NetHunter

My favorite way is to build installer myself. But you may also [download it](https://www.kali.org/get-kali/#kali-mobile) if you wish to.

If you don't want to build your own installer, skip to the next step.

First let's build from source.

```console
# Clone and setup kali-nethunter-installer
$ git clone https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-installer.git
$ cd kali-nethunter-installer
$ ./bootstrap.sh
[?] Would you like to grab the full history of kernels? (y/N):
[?] Would you like to use SSH authentication (faster, but requires a GitLab account with SSH keys)? (y/N): N
[i] Running command: git clone --depth 1 https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-kernels.git kernels
Cloning into 'kernels'...

# Build full installer
## LOS 21
$ ./build.py -k beyond1lte-los -14 -fs full
## LOS 22.2
$ ./build.py -k beyond1lte-los -15 -fs full
## LOS 23.2
$ ./build.py -k beyond1lte-los -16 -fs full
```

Push installer to your device.

```plaintext
adb push nethunter-20250629_171321-beyond1lte-los-fifteen-kalifs_full.zip /sdcard/
```

Open Magisk, navigate to "Modules > Install from Storage", select Kali NetHunter installer and install it.

Wait for Kali NetHunter installation to finish, and reboot when prompted.

## Magisk Modules (optional)

Download Magisk Overlayfs module.

Magisk Overlayfs: [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/magisk-overlayfs-release.zip)

Download PlayIntegrityFix module.

PlayIntegrityFix: [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/PlayIntegrityFix_v3.3-inject-manual.zip)

Push the package to your android device.

```plaintext
adb push magisk-overlayfs-release.zip /sdcard/
adb push PlayIntegrityFix_v3.3-inject-manual.zip /sdcard/
```

Open magisk, navigate to "Modules > Install from storage" and select Magisk Overlayfs module. Press "Ok" to install and reboot once install complete.

Open magisk again, then in settings enable "Zygisk".

Navigate to "Modules > Install from storage" and select PlayIntegrityFix module. Press "Ok" to install and reboot once install complete.

## Nexmon

### Nexmon Setup

Nexmon S10 : [Download](https://github.com/V0lk3n/nethunter_kernel_samsung_exynos9820/releases/download/nethunter-22.2/nexmon-s10.zip)

Push the module to your device.

```plaintext
adb push nexmon-s10.zip /sdcard/
```

Open Magisk, navigate to "Modules > Install from Storage" and select Nexmon S10 module.

Wait for installation to complete and reboot your phone.

### Nexmon Usage

Start Monitor mode in Android terminal

```bash
$ svc wifi disable
$ sleep 2
$ ifconfig wlan0 up
$ nexutil -s0x613 -i -v2
```

Stop Monitor mode

```bash
$ nexutil -m0
$ svc wifi enable
```

Run airodump in Kali terminal (export is needed in every new terminal window)

```bash
$ export LD_PRELOAD=/lib/kalilibnexmon.so
$ airodump-ng wlan0
```

kalilibnexmon.so : [Download](https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-kernels/-/raw/main/ten/angler-los/system/lib64/kalilibnexmon.so)

Copy to chroot as `/lib/kalilibnexmon.so`

### Hijacker Setup

Open Hijacker app and configure the following Settings.

| Settings  | Value |
| :--------------- | -----:|
| Prefix | LD_PRELOAD=/data/user/0/com.hijacker/files/lib/libnexmon.so |
| Enable Monitor Mode | if [ \`dumpsys wifi \| grep "Wi-Fi is" \| cut -d" " -f3\` == "enabled" ]; then svc wifi disable; sleep 2; ifconfig wlan0 up; fi; nexutil -s0x613 -i -v2 |
| Disable Monitor Mode | nexutil -m0; svc wifi enable |
| Start Monitor Mode on Airodump Start | ✅ |
| Band | Both |

If your Wi-Fi was connected to 5Ghz, it may show only that channel at start. Just press stop + start icon to scan again, so you see all 2.4Ghz channels.

Although 5Ghz is supported, you need to manually change channels in Android terminal using `nexutil -k36/80` for channel 36, `nexutil -k40/80` for channel 40 and so on. This feature will be added to Hijacker app.

# Bonus : Flash splashscreen

Boot warning can be annoying, you probably wish to flash a custom one to get rid of theses warnings.

[XDA Thread](https://xdaforums.com/t/g97xf-soldier9312s-splash-screen-changer-1-0-13-05-2019.3929748/)

[Download](https://androidfilehost.com/?w=files&flid=293633)

Chose and Download the desired Splash Screen.

Boot to Recovery and navigate to "Apply update > Apply from ADB" and flash splash screen using adb sideload.

```plaintext
adb -d sideload G97X_Splash_Screen_Changer_by_SoLdieR9312_splash.zip
```

Wait flashing to complete, and it will automatically reboot your phone.

## Credits

Kernels and documentation maintained by @V0lk3n

Nexmon module made by @yesimxev

Special thanks to :
- **Arti** for help and support on Galaxy S10
- @Akabulous for providing up to date RTL drivers and help
- @Nexmon
- @MarkusTieger for nexmon
