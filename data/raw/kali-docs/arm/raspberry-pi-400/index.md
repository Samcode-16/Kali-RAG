---
title: Raspberry Pi 400
description:
icon:
weight:
author: ["steev",]
---

The [Raspberry Pi 400](https://www.raspberrypi.org/products/raspberry-pi-400/) has a quad core 1.8GHz processor, with 4GB of RAM, in a keyboard formfactor. Kali Linux runs on a microSD card.

By default, the Kali Linux Raspberry Pi 400 image contains the [**kali-linux-default** metapackage](/docs/general-use/metapackages/) similar to most other platforms. If you wish to install extra tools please refer to our [metapackages page](/docs/general-use/metapackages/).

## Kali on Raspberry Pi400 - User Instructions

If you're unfamiliar with the details of [downloading and validating a Kali Linux image](/docs/introduction/download-official-kali-linux-images/), or for [using that image to create a bootable device](/docs/usb/live-usb-install-with-windows/), it's strongly recommended that you refer to the more detailed procedures described in the specific articles on those subjects.

To install a pre-built image of the standard build of Kali Linux on your Raspberry Pi400, follow these instructions:

1. Get a fast microSD card with at least 16GB capacity. Class 10 cards are highly recommended.
2. Download _and validate_ our preferred `Kali Raspberry Pi 400` image from the [downloads](/get-kali/) area. The process for validating an image is described in more detail on [Downloading Kali Linux](/docs/introduction/download-official-kali-linux-images/).
3. Use the **[dd](https://manpages.debian.org/testing/coreutils/dd.1.en.html)** utility to image this file to your microSD card (same process as [making a Kali USB](/docs/usb/live-usb-install-with-windows/).

In our example, we assume the storage device is located at `/dev/sdX`. Do _not_ simply copy these value, **change this to the correct drive path**.

{{% notice info %}}
This process will wipe out your microSD card. If you choose the wrong storage device, you may wipe out your computers hard disk.
{{% /notice %}}

```console
$ xzcat kali-linux-2026.2-raspberry-pi-armhf.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
```

**or**

```console
$ xzcat kali-linux-2026.2-raspberry-pi-arm64.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
```

This process can take a while, depending on your PC, your microSD card's speed, and the size of the Kali Linux image.

Once the _dd_ operation is complete, boot up the Raspberry Pi 400 with the microSD card plugged in.

You should be able to [log in to Kali](/docs/introduction/default-credentials/).

## Kali on Raspberry Pi400 - Tips and Tricks

The bluetooth service on the Raspberry Pi 400 needs a **uart helper service** before it works. To enable and start the bluetooth service run the following commands:

```console
kali@kali:~$ sudo systemctl enable --now hciuart.service
kali@kali:~$ sudo systemctl enable --now bluetooth.service
```

- - -

The wireless chip on the Raspberry Pi 400 is **NOT** supported by [nexmon](https://github.com/seemoo-lab/nexmon), so if you are planning on doing wireless attacks or research, you will need to use an external wireless device.

- - -

Kali uses LightDM with Xfce on Xorg for the desktop by default. In our testing, we found that many of the HAT systems required setting up a config snippet for display to show up. If you are having issues getting output, it could be the opposite for you, and you may want to try removing the file `/etc/X11/Xorg.conf.d/99-vc4.conf` and allow Xorg to attempt to use the defaults:

```console
kali@kali:~$ sudo mv -v /etc/X11/Xorg.conf.d/99-vc4.conf ~
```

Another option may be that you may have to modify the config snippet. It is best to consult with whatever documentation your LCD may have.

- - -

# Kali on Raspberry Pi400 Headless - Tips and Tricks

You can add a `wpa_supplicant.conf` file to the first partition of the microSD card to connect to a wireless network.

You can create this file on another Linux system by running `wpa_passphrase YOURNETWORK > wpa_supplicant.conf`. It will prompt you for the wireless network's password. You can add the password to the command as you run it, but keep in mind that if you do, your Wi-Fi network password will be in your user's shell history.

## Kali on Raspberry Pi400 - Image Customization

If you want to customize the Kali Raspberry Pi400 image, including changes to the [packages](/docs/general-use/metapackages/) being installed, changing the [desktop environment](/docs/general-use/switching-desktop-environments/), increasing or decreasing the image file size or generally being adventurous, check out the [Kali-ARM Build-Scripts](https://gitlab.com/kalilinux/build-scripts/kali-arm) repository on GitLab, and follow the _README.md_ file's instructions. The script to use is `raspberry-pi.sh` (32-bit) or `raspberry-pi-64-bit.sh` (64-bit).
