---
title: Discovering Problems With Download Speed
description:
icon:
weight:
author: ["gamb1t",]
---

### How our downloads work

Kali Linux operates off of a network of [community](/docs/community/kali-linux-mirrors/) and official mirrors. What this means is that when you click to [download](/get-kali/) Kali Linux there are some steps that are done before you actually begin the download. First you hit [cdimage.kali.org](http://cdimage.kali.org/README?mirrorlist) which is our redirector. This determines where the request is coming from and will send you to one of the best mirrors for your situation. For example, if you are in the US you may get send to Berkeley University's mirror. After you are sent to the best mirror your download request is submitted to it, and your download actually begins.

### Determining which mirror we are at

Now that we know how this happens we can determine which mirror we are actually getting sent to ourselves. We can do this in a couple of different ways. The first is to simply click [download](/get-kali/) and then in the downloads tab right click the download and copy the URL. This works for the majority of web browsers. The second option is to use `curl`:

```console
kali@kali:~$ curl -i https://cdimage.kali.org/kali-2026.2/kali-linux-2026.2-installer-amd64.iso
HTTP/1.1 302 Found
Server: nginx
Date: Wed, 18 Jun 2025 10:52:17 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 0
Connection: keep-alive
Cache-Control: private, no-cache
Link: <https://kali.download/base-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso>; rel=duplicate; pri=1; geo=ae
Link: <https://ask4.mm.fcix.net/kali-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso>; rel=duplicate; pri=2; geo=gb
Link: <https://ftp.hands.com/kali-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso>; rel=duplicate; pri=3; geo=gb
Location: https://mirror.vinehost.net/kali-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso

kali@kali:~$
```

Here we can see that we were redirected to `mirror.vinehost.net`.

### Submitting bugs

If the download speed is noticeably slow or the mirror is not working, we would love to know. This can be the result of a few different problems and none of them are able to be fixed without us knowing which mirror and what speeds. So lets get that information wrapped up nicely.

We can use `wget` to download the iso file and learn just how fast the download is taking. If we are on Windows, we can either get the download speed from the web browser or install [wget for Windows](https://medium.com/nerd-for-tech/using-wget-command-in-windows-10-environment-d766b8f526e9)

```console
kali@kali:~$ get https://kali.download/base-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso
--2025-06-18 10:53:17--  https://kali.download/base-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso
Resolving kali.download (kali.download)... 2606:4700::6811:fdef, 2606:4700::6811:feef, 104.17.254.239, ...
Connecting to kali.download (kali.download)|2606:4700::6811:fdef|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 4478939136 (4.2G) [application/octet-stream]
Saving to: ‘kali-linux-2026.2-installer-amd64.iso’

kali-linux-2026.2-installer-amd64.iso   6%[====>                                                                     ] 196.46M  31.6MB/s    eta 81s

kali@kali:~$
```

As we can see we are downloading at about 31.6MB/s and we are using the mirror link we got from the previous section.

- - -

Lets look at another example, this time with a connection from France:

```console
kali@kali:~$ curl -i https://cdimage.kali.org/kali-2026.2/kali-linux-2026.2-installer-amd64.iso
HTTP/1.1 302 Found
Server: nginx
Date: Wed, 18 Jun 2025 10:55:33 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 0
Connection: keep-alive
Cache-Control: private, no-cache
Link: <https://kali.download/base-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso>; rel=duplicate; pri=1; geo=ae
Location: https://archive-4.kali.org/kali-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso

kali@kali:~$ wget https://archive-4.kali.org/kali-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso
--2025-06-18 10:56:00--  https://archive-4.kali.org/kali-images/kali-2026.2/kali-linux-2026.2-installer-amd64.iso
Resolving archive-4.kali.org (archive-4.kali.org)... 2001:41d0:2:f566::, 176.31.228.102
Connecting to archive-4.kali.org (archive-4.kali.org)|2001:41d0:2:f566::|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 4478939136 (4.2G) [application/octet-stream]
Saving to: ‘kali-linux-2026.2-installer-amd64.iso’

kali-linux-2026.2-installer-amd64.iso   0%[                                                                          ] 615.75K   610KB/s

kali@kali:~$
```

Now that we know the download speed and the mirror link we can submit a [bug report](/docs/community/submitting-issues-kali-bug-tracker/) with all our information.

### Using a different mirror

We can consult back to the [community](/docs/community/kali-linux-mirrors/) mirrors and manually select a different mirror to see if our download speed improves. To do this we simply will copy the mirror link we want to use from the list and then change "README" to be `kali-2026.2/kali-linux-2026.2-installer-amd64.iso` or whichever download link we are using. We can see this in the previous section, right after `kali-images/`.
