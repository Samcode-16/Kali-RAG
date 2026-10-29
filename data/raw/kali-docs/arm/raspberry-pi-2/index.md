---
title: Raspberry Pi 2
description:
icon:
weight:
author: ["steev",]
---

{{% notice info %}}
If your Raspberry Pi 2 has `Raspberry Pi 2 Model B V1.2` printed on the PCB above the CPU, we suggest to follow the [Raspberry Pi 2 v1.2 documentation](/docs/arm/raspberry-pi-64-bit/). However if it says `Raspberry Pi 2 Model B V1.1`, keep reading
{{% /notice %}}

By default, the Kali Linux Raspberry Pi 2 image contains the [**kali-linux-default** metapackage](/docs/general-use/metapackages/) similar to most other platforms. If you wish to install extra tools please refer to our [metapackages page](/docs/general-use/metapackages/).

## Kali on Raspberry Pi 2 - User Instructions

If you're unfamiliar with the details of [downloading and validating a Kali Linux image](/docs/introduction/download-official-kali-linux-images/), or for [using that image to create a bootable device](/docs/usb/live-usb-install-with-windows/), it's strongly recommended that you refer to the more detailed procedures described in the specific articles on those subjects.

To install a pre-built image of the standard build of Kali Linux on your Raspberry Pi 2, follow these instructions:

1. Get a fast microSD card with at least 16GB capacity. Class 10 cards are highly recommended.
2. Download _and validate_ the `Kali RaspberryPi 2, 3, 4 and 400 (img.xz)` image from the [downloads](/get-kali/) area. The process for validating an image is described in more detail on [Downloading Kali Linux](/docs/introduction/download-official-kali-linux-images/).
3. Use the **[dd](https://manpages.debian.org/testing/coreutils/dd.1.en.html)** utility to image this file to your microSD card (same process as [making a Kali USB](/docs/usb/live-usb-install-with-windows/).

In our example, we assume the storage device is located at `/dev/sdX`. Do _not_ simply copy these value, **change this to the correct drive path**.

{{% notice info %}}
This process will wipe out your microSD card. If you choose the wrong storage device, you may wipe out your computers hard disk.
{{% /notice %}}

```console
$ xzcat kali-linux-2026.2-raspberry-pi-armhf.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
```

This process can take a while, depending on your PC, your microSD's speed, and the size of the Kali Linux image.

Once the _dd_ operation is complete, boot up the Raspberry Pi 2 with the microSD plugged in.

You should be able to [log in to Kali](/docs/introduction/default-credentials/).

## Kali on Raspberry Pi 2 - Tips

To build external modules against the kernel, most instructions will state that you need to install header packages via `linux-headers-$(uname -r)` This is **not** the case on the Raspberry Pi 2 image. They are already included and do not follow that naming scheme, they are `linux-headers-rpi-v7` and `linux-headers-rpi-v7l`. If you have removed them, you can add them back by running the following commands:

```console
kali@kali:~$ sudo apt update
[...]
kali@kali:~$ sudo apt install -y linux-headers-rpi-v7 linux-headers-rpi-v7l
```

- - -

You can use mt76 chipset USB Wi-Fi devices, but they require creating a configuration file in `/etc/modprobe.d` with the following contents:

```plaintext
# Load mt76usb without using scatter-gather which doesn't work on the RPi2 or RPi3 USB chipset
options mt76-usb disable_usb_sg=1
```

- - -

Kali uses LightDM with Xfce on Xorg for the desktop by default. In our testing, we found that many of the HAT systems required setting up a config snippet for display to show up. If you are having issues getting output, it could be the opposite for you, and you may want to try removing the file `/etc/X11/Xorg.conf.d/99-vc4.conf` and allow Xorg to attempt to use the defaults:

```console
kali@kali:~$ sudo mv -v /etc/X11/Xorg.conf.d/99-vc4.conf ~
```

Another option may be that you may have to modify the config snippet. It is best to consult with whatever documentation your LCD may have.

- - -

## Kali on Raspberry Pi 2 - Image Customization

If you want to customize the Kali Raspberry Pi 2 image, including changes to the [packages](/docs/general-use/metapackages/) being installed, changing the [desktop environment](/docs/general-use/switching-desktop-environments/), increasing or decreasing the image file size or generally being adventurous, check out the [Kali-ARM Build-Scripts](https://gitlab.com/kalilinux/build-scripts/kali-arm) repository on GitLab, and follow the _README.md_ file's instructions. The script to use is `raspberry-pi.sh`.
