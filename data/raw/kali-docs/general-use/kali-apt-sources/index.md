---
title: Kali Network Repositories (/etc/apt/sources.list)
description:
icon:
weight: 61
author: ["g0tmi1k",]
aliases:
  - "/docs/general-use/kali-linux-sources-list-repositories/"
---

The topic of repositories is always a large one, and comes up frequently. It is an item which people often get wrong and confused with. Please take the time to read the information below and any references which is linked to before acting on anything.

## Default APT Network Repositories Configuration

On a standard, clean install of Kali Linux, with network access, you should have the following content in `/etc/apt/sources.list.d/kali.sources`:

```console
kali@kali:~$ grep -v '^#' /etc/apt/sources.list.d/kali.sources
Types: deb
URIs: http://http.kali.org/kali/
Suites: kali-rolling
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/kali-archive-keyring.gpg

kali@kali:~$
```

Before the release of [Kali 2026.2](/blog/kali-linux-2026-2-release/), this file didn't exist, and instead you should have the following entry present in `/etc/apt/sources.list`:

```console
kali@kali:~$ grep -v '^#' /etc/apt/sources.list | sort -u
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware

kali@kali:~$
```

If the output doesn't exactly match up to the above output, you may not be able to install any new additional packages or receive updates.
This may happen for any number of reasons, such as:

- You have switched your [branch](/docs/general-use/kali-branches/).
- Using a different hardcoded [mirror](/docs/community/kali-linux-mirrors/).

You will probably want to read the "switching branches" section to alter this.

Notable changes over time:

- Since [Kali 2020.3](/blog/kali-linux-2020-3-release/), after Kali's setup is complete, network repositories will be enabled by default, even if there was no network access during installation.
- Since [Kali 2026.2](/blog/kali-linux-2026-2-release/), the Network Repositories are now configured in the file `/etc/apt/sources.list.d/kali.sources`.

## Modernizing the APT Network Repositories Configuration

If you don't have the file `/etc/apt/sources.list.d/kali.sources`, but you have only the legacy file `/etc/apt/sources.list`, you can convert from one to the other by running the following command:

```
kali@kali:~$ sudo apt update
Get:1 http://http.kali.org/kali kali-rolling InRelease [34.0 kB]
[...]
Fetched 21.4 MB in 2s (10.8 MB/s)                       

kali@kali:~$ sudo apt modernize-sources
The following files need modernizing:
  - /etc/apt/sources.list

Modernizing will replace .list files with the new .sources format,
add Signed-By values where they can be determined automatically,
and save the old files into .list.bak files.

This command supports the 'signed-by' and 'trusted' options. If you
have specified other options inside [] brackets, please transfer them
manually to the output files; see sources.list(5) for a mapping.

For a simulation, respond N in the following prompt.
Rewrite 1 sources? [Y/n] y
Modernizing /etc/apt/sources.list...
- Writing /etc/apt/sources.list.d/kali.sources

kali@kali:~$
```

For the rest of this documentation, we assume that your APT Network Repositories are configured via the file `/etc/apt/sources.list.d/kali.sources`.

## Switching Kali Main Branch

Kali has two [main branches](/docs/general-use/kali-branches/) to choose from (please take the time to read which one would be the best option for your setup):

- **kali-rolling** - default & frequently updated
- **kali-last-snapshot** - point release so more "stable" & the "safest" - updated quarterly

Enabling the `kali-rolling` branch is done with the command:

```console
kali@kali:~$ sudo sed -i 's/^Suites: .*/Suites: kali-rolling/' /etc/apt/sources.list.d/kali.sources
```

Enabling the `kali-last-snapshot` branch is done with the command:

```console
kali@kali:~$ sudo sed -i 's/^Suites: .*/Suites: kali-last-snapshot/' /etc/apt/sources.list.d/kali.sources
```

Note that such a change is effective only after running `sudo apt update`.

## Enabling Kali Additional Branches

Kali also proposes [additional branches](/docs/general-use/kali-branches/) for special cases. In theory, it's possible to enable those regardless of the main branch you use. In practice though, they are meant to be used in addition to `kali-rolling`. We discourage using it in addition to `kali-last-snapshot` unless you know exactly what you're doing. Those additional branches are:

- **kali-experimental** - packages which are under testing or work in progress
- **kali-bleeding-edge** - packages automatically updated from upstream git repositories

Enabling or disabling those branches is best done using the command-line tool `kali-tweaks`, under the *Network Repositories* section:

![](kali-tweaks-network-repositories.png)

If you prefer, you can also enable those branches manually from the command-line. For example, enabling `kali-experimental` in addition to `kali-rolling` is done with the command:

```console
kali@kali:~$ sudo sed -i 's/^Suites: .*/Suites: kali-rolling kali-experimental/' /etc/apt/sources.list.d/kali.sources
```

To disable `kali-experimental` and keep only `kali-rolling`, run the following command:

```console
kali@kali:~$ sudo sed -i 's/^Suites: .*/Suites: kali-rolling/' /etc/apt/sources.list.d/kali.sources
```

The branch `kali-bleeding-edge` can be enabled with a similar command, we just need to change the name of the branch:

```console
kali@kali:~$ sudo sed -i 's/^Suites: .*/Suites: kali-rolling kali-bleeding-edge/' /etc/apt/sources.list.d/kali.sources
```

To disable `kali-bleeding-edge` and keep only `kali-rolling`:

```console
kali@kali:~$ sudo sed -i 's/^Suites: .*/Suites: kali-rolling/' /etc/apt/sources.list.d/kali.sources
```

## Format of kali.sources and sources.list Files

Both formats are thoroughly documented in the `sources.list` manual page:

```
kali@kali:~$ man sources.list

kali@kali:~$
```

The file `/etc/apt/sources.list.d/kali.sources` is said to be in the **deb822-style** format, while the old `/etc/apt/sources.list` is dubbed the **one-line-style** format.

Let's have a closer look at the default `kali.sources` file:

```plaintext
Types: deb
URIs: http://http.kali.org/kali/
Suites: kali-rolling
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/kali-archive-keyring.gpg
```

- **Types** is going to be `deb` (Regular Binary), but you can also add `deb-src` (Source) if you need to download the sources of the packages
- **URIs** should be `http://http.kali.org/kali` as this is our load balancer, which will direct you to the best [mirror](/docs/community/kali-linux-mirrors/).
- **Suites** is what [version of Kali](/docs/general-use/kali-branches/) you wish to use (we use the term _Branch_ instead of _Suite_ in this page)
- **Components** are what packages you wish to use, based on the [Debian Free Software Guidelines (DFSG)](https://www.debian.org/social_contract#guidelines). Kali defaults to everything.
- **Signed-By** indicates what keyring is used to validate the signature of the metadata that is downloaded from the network repository

The old `sources.list` file had pretty much the same content, but packed on a single-line, which didn't allow for multiple values, except for the last field:

```plaintext
deb   http://http.kali.org/kali   kali-rolling   main contrib non-free non-free-firmware
<Type>   <URI>                    <Suite>        <Components>
```

## Default Offline Install Values

During the Kali setup process, if you don't have access to a network connection to reach a repository, you will perform an offline installation of Kali Linux. You will be limited to the packages & the version which is on the medium you installed Kali from. This will then configure Kali to continue to use this medium to install packages from, even after Kali has been installed.

This means you will not get any updates to packages, or any new additional tools, which can be frustrating. You can see if you the offline media enabled if your values match up with what's below (or if you want to enable this option):

```console
kali@kali:~$ cat /etc/apt/sources.list
#deb cdrom:[Kali GNU/Linux 2026.2 _Kali-last-snapshot_ - Official amd64 BD Binary-1 with firmware 20260518-11:06]/ kali-rolling contrib main non-free non-free-firmware

# This system was installed using removable media.
# The matching "deb cdrom" entries were disabled at the end
# of the installation process by preseed.
# For information about how to configure apt package sources,
# see the sources.list(5) manual.
kali@kali:~$
kali@kali:~$ sudo apt-cdrom add
Using CD-ROM mount point /media/cdrom/
Identifying... [214de01a423e6435d1e89953fd88dbd0-2]
Scanning disc for index files...
Found 4 package indexes, 0 source indexes, 0 translation indexes and 0 signatures
This disc is called: 
'Kali GNU/Linux 2026.2 _Kali-last-snapshot_ - Official amd64 BD Binary-1 with firmware 20260518-11:06'
Reading Package Indexes... Done
Writing new source list
Source list entries for this disc are:
deb cdrom:[Kali GNU/Linux 2026.2 _Kali-last-snapshot_ - Official amd64 BD Binary-1 with firmware 20260518-11:06]/ kali-rolling contrib main non-free non-free-firmware
Repeat this process for the rest of the CDs in your set.
kali@kali:~$
```

If your output matches what's above, please see the switching branch section, if you wish to receive updates.

However, if you do have network connection, which has access to network repositories, it will be enabled for you. You don't need to do anything.

## Non-Kali Repositories

If you want to install additional tools and software (such as [signal](https://signal.org/)) outside of what Kali has to offer, you may need to include an extra repository for this to happen. Please do not alter `/etc/apt/sources.list.d/kali.sources`, as this is used for the Kali Linux Operating System. Any extra tools and software needs to be placed into their own file in the directory `/etc/apt/sources.list.d/` (such as `/etc/apt/sources.list.d/repo-name.sources`, replacing `repo-name` with a suitable name). It is highly recommended that each repository should be in its own file.

By adding Kali's repository to a non-Kali OS (such as trying to add Kali to Ubuntu), this will highly increase the chance of your system not working. It may not happen straight away, but without any warning, it may break. We will not be able to offer support (and based on what we have seen over the years, most other OS will not help too).

Likewise, adding other operating system's repositories into Kali (such as trying to put Ubuntu on Kali), will break your installation. **This is the single most common reason why Kali Linux systems break**.

If any guides are telling you to do anything else than the above, this is unofficial advice, and completely not supported by Kali Linux. More often than not, users in this case end up doing a reinstall after learning this lesson.

## Mirrors

We have a list of [official Kali Linux mirrors](/docs/community/kali-linux-mirrors/), as well as a [guide on how to setup your own](/docs/community/setting-up-a-kali-linux-mirror/). This may be kept as a local repository which is only accessible on a LAN, or a remote private one, or if you have the ability to, you may wish to [share back to the community](/docs/community/contribute/) and make it public allowing for anyone else in your geographical area to benefit from it.

## Source Repositories

Should you require the source to a package (so you can compile the package yourself if you so wish, or look into debugging a problem with a package), you can add the `deb-src` type to your configuration:

```console
kali@kali:~$ sudo sed -i 's/^Types: .*/Types: deb deb-src/' /etc/apt/sources.list.d/kali.sources
```
