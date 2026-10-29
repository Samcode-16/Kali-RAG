---
title: Updating Kali
description:
icon:
weight:
author: ["gamb1t"]
---

## When should you update Kali?

If you have a default installation of Kali, you should be checking for updates every few days or weeks. If you need a new version of a tool, or hear about a security update, that may speed up the timetable. However, a good practice is that you ensure all tools work before an engagement and during that engagement you should not update. As Kali is a rolling release, once in a while issues will sneak into rolling and may break a tool that is needed.

If you are using [last-snapshot](/docs/general-use/kali-branches/), you will not receive updates until we release the next version of Kali. You can be notified by watching our [blog posts](/blog/) via [newsletter](/newsletter/) or [RSS](/rss.xml), as well as following [Kali on social networks](/docs/community/list-of-official-kali-sites/#social-media-networks). Kali has a release four times a year, and follows a loose quarterly schedule.
<!-- For this reason, it is a good idea to follow [Kali on social networks](/docs/community/list-of-official-kali-sites/#social-media-networks), or check the [Kali website](/releases/) every few months. -->

## How to update Kali?

To update Kali, first ensure that `/etc/apt/sources.list.d/kali.sources` is [properly populated](/docs/general-use/kali-apt-sources/):

```console
kali@kali:~$ cat /etc/apt/sources.list.d/kali.sources
# See https://www.kali.org/docs/general-use/kali-apt-sources/
Types: deb
URIs: http://http.kali.org/kali/
Suites: kali-rolling
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/kali-archive-keyring.gpg

kali@kali:~$
```

After that we can run the following commands which will upgrade us to the latest Kali version:

```console
kali@kali:~$ sudo apt update
[...]
kali@kali:~$
kali@kali:~$ sudo apt full-upgrade -y
[...]
kali@kali:~$
```
