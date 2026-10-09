from pathlib import Path
from sentence_transformers import SentenceTransformer, util
import re
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
USE_RERANK = False   # switch to False to compare

open("failures.txt", "w").close()

LUKS     = ["raspberry-pi-with-luks-full-disk-encryption",
            "raspberry-pi-with-luks-full-disk-encryption-2"]
LIVE_USB = ["live-usb-install-with-windows", "live-usb-install-with-linux",
            "live-usb-install-with-mac"]
PERSIST  = ["usb-persistence", "usb-persistence-encryption"]
VM_TOOLS = ["install-virtualbox-guest-additions", "install-vmware-guest-tools",
            "troubleshooting-vmware"]
WIFI     = ["troubleshooting-wireless-driver-issues", "wireless-cards"]
KEX      = ["nethunter-kex-manager", "nethunter-rootless"]
ISO      = ["download-official-kali-linux-images", "download-images-securely"]

# (question, folder name that should contain the answer, or None if out of scope)
TESTS = [
    ("apt update fails with GPG error", "gpgkey-expiry"),
    ("how to install kali in virtualbox", "install-virtualbox-guest-vm"),
    ("metasploit cannot connect to database", "starting-metasploit-framework-in-kali"),
    ("my laptop is on fire", None),
    ("wifi adapter not entering monitor mode", WIFI),
    ("how to install Docker on Kali Linux", "installing-docker-on-kali"),
    ("how do I prepare Kali Linux for WSL", "wsl-preparations"),
    ("how to install Kali as a QEMU guest", "install-qemu-guest-vm"),
    ("how to install Kali in Hyper-V", "install-hyper-v-guest-vm"),
    ("how to install VMware guest tools on Kali", "install-vmware-guest-tools"),
    ("how to install Kali Linux on a Raspberry Pi 5", "raspberry-pi-5"),
    ("what is Kali NetHunter Rootless", "nethunter-rootless"),
    ("how to set up a NetHunter KeX session", "nethunter-kex-manager"),
    ("how to scan a network with the NetHunter Nmap interface", "nethunter-nmap"),
    ("how to change the Wi-Fi MAC address in NetHunter", "nethunter-mac-changer"),
    ("how to search Exploit-Database with Searchsploit", "nethunter-searchsploit"),
    ("how to configure NetHunter custom commands", "nethunter-custom-commands"),
    ("how to use the NetHunter USB Arsenal", "nethunter-usbarsenal"),
    ("how to install NVIDIA drivers on Kali Linux", "install-nvidia-drivers-on-kali-linux"),
    ("how to enable full disk encryption on Kali Raspberry Pi", LUKS),
    ("what is the best pizza topping", None),
    ("how do I bake a chocolate cake", None),
    ("how to configure a Cisco router", None),
    ("fix my Windows blue screen error", None),
    ("how do I install Photoshop", None),
]

SYMPTOM_TESTS = [
    # apt problems
    ("apt update says the repository signature is invalid", ["gpgkey-expiry", "handling-common-apt-errors"]),
    ("apt says missing key which is needed to verify signature", ["gpgkey-expiry", "handling-common-apt-errors"]),
    ("dpkg error trying to overwrite a file owned by another package", "handling-common-apt-errors"),

    # Installation
    ("The installer completed successfully but after reboot the machine only shows a blinking cursor","troubleshooting-a-kali-linux-install"),
    ("Kali boots into a black screen immediately after installation","Graphics-issues-on-bare-metal-installation"),
    ("The system starts directly into Windows even though I installed Kali on another partition","dual-boot-kali-with-windows"),
    ("GRUB never appears after installing Kali alongside Windows",["dual-boot", "dual-boot-kali-with-windows"]),

    #Cloud
    ("My Kali EC2 instance boots but I cannot log in using the credentials I expected","aws"),
    ("I launched a Kali EC2 instance on AWS but SSH access is failing","aws"),

    #USB / Live Boot
    ("I created a bootable Kali USB but the computer says no bootable device found", LIVE_USB),
    ("The USB works on one computer but another machine refuses to boot from it", LIVE_USB),
    ("My live USB starts but changes disappear after every reboot","usb-persistence"),
    ("I expected files to remain on my live USB but everything resets each time",["usb-persistence", "usb-persistence-encryption"]),

    # Virtualization
    ("The virtual machine window is tiny and cannot automatically resize", VM_TOOLS),
    ("Shared folders are configured but they do not appear inside Kali", VM_TOOLS),

    # VMware
    ("The screen resolution stays fixed even when I resize the VMware window",["install-vmware-guest-tools","install-vmware-guest-vm","troubleshooting-vmware",]),
    ("Dragging files between VMware and Kali does not work",["install-vmware-guest-tools","troubleshooting-vmware",]),
    ("I installed NetHunter Rootless but the KeX graphical desktop will not start", KEX),

    #Wireless
    ("Monitor mode enables successfully but I cannot capture any nearby traffic", WIFI),
    ("I cannot connect to the internet through my wireless adapter", WIFI),

    # Metasploit
    ("msfconsole says no database connection", "starting-metasploit-framework-in-kali"),
    ("msfdb init fails and postgresql is not running", "starting-metasploit-framework-in-kali"),

    # Wireless
    ("wifi card not detected in kali", WIFI),
    ("wlan0 does not show up after plugging in my usb adapter", WIFI),

    # VM problems
    ("copy and paste between my host and kali vm is not working", VM_TOOLS),
    ("kali vm screen is tiny and will not resize", VM_TOOLS),
    ("my VirtualBox guest additions broke after an update", "install-virtualbox-guest-additions"),                                          # check

    # Other
    ("docker command gives permission denied on kali", "installing-docker-on-kali"),                                                       # check
    ("black screen after installing nvidia driver", ["install-nvidia-drivers-on-kali-linux", "Graphics-issues-on-bare-metal-installation"]),                                               # check

    #Raspberry Pi
    ("My Raspberry Pi never finishes booting after enabling disk encryption", LUKS),
    ("The device asks for decryption information but refuses the correct password", LUKS),

    #Download / Verification
    ("How can I verify that my Kali ISO was not modified before installation", ISO + ["verify-usb-write"]),
    ("I downloaded Kali from a mirror and want to confirm the image is authentic", ISO),


    # Difficult Semantic Tests
    ("My Android phone can reach the Kali environment but not the desktop session", KEX),
    ("I can boot the operating system from removable media but none of my changes survive a restart", PERSIST),
    ("The guest operating system runs normally but host integration features are missing", VM_TOOLS),
    ("The wireless card appears in the system yet packet capture yields almost nothing", WIFI),



    # Should refuse
    ("How do I reverse a linked list in C?", None),
    ("What is the capital of Japan?", None),
    ("Write a Python program for bubble sort", None),
    ("Explain transformers in machine learning", None),
    ("How do I create a React component?", None),
    ("my ubuntu server will not boot after kernel update", None),
    ("how to set up a wordpress site with apache", None),
]

HARD_TESTS = [   # unanswerable or ambiguous; do not score
       ("Kali was working yesterday but after updates several tools stopped launching", None),
       ("A package installs correctly but crashes every time I run it", None),
       ("Connecting to the Kali desktop from my phone immediately disconnects", None),
   ]

TESTS = TESTS + SYMPTOM_TESTS

def get_title(text):
    m = re.search(r'^title:\s*(.+)$', text, re.M)
    return m.group(1).strip().strip('"') if m else ""

def pack_paragraphs(text, max_words=150):
    paras = [p for p in text.split("\n\n") if p.strip()]
    out, cur, n = [], [], 0
    for p in paras:
        w = len(p.split())
        if cur and n + w > max_words:
            out.append("\n\n".join(cur))
            cur, n = [], 0
        cur.append(p)
        n += w
    if cur:
        out.append("\n\n".join(cur))
    return out

USE_TITLE = False   # switch to False to compare

chunks = []
for f in Path("data/raw/kali-docs").rglob("*.md"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    if 'archived: "true"' in text:
        continue
    title = get_title(text)
    for part in text.split("\n## "):
        heading = part.split("\n", 1)[0][:80]
        for piece in pack_paragraphs(part):
            if len(piece) > 100:
                label = f"{f.parent.name} | {title} | {heading}" if USE_TITLE else f"{f.parent.name} | {heading}"
                chunks.append((f.parent.name, label + "\n" + piece))

print("Total chunks:", len(chunks))

model = SentenceTransformer("all-MiniLM-L6-v2")
vecs = model.encode([c[1] for c in chunks])

def tok(s):
    return re.findall(r"\w+", s.lower())

bm25 = BM25Okapi([tok(c[1]) for c in chunks])

def hybrid_top(question, k=3, pool=30):
    dense = util.cos_sim(model.encode(question), vecs)[0]
    best_dense = float(dense.max())
    dense_rank = dense.argsort(descending=True).tolist()
    bm = bm25.get_scores(tok(question))
    bm_rank = sorted(range(len(bm)), key=lambda i: -bm[i])
    fused = {}
    for rank_list in (dense_rank, bm_rank):
        for r, i in enumerate(rank_list[:50]):
            fused[i] = fused.get(i, 0) + 1 / (60 + r)

    ranked = sorted(fused, key=fused.get, reverse=True)

    if USE_RERANK:
        cand = ranked[:pool]
        scores = reranker.predict([(question, chunks[i][1]) for i in cand])
        order = sorted(range(len(cand)), key=lambda j: -scores[j])
        ranked = [cand[j] for j in order]

    top, seen = [], set()
    for i in ranked:
        if chunks[i][0] in seen:
            continue
        seen.add(chunks[i][0])
        top.append(i)
        if len(top) == k:
            break
    return best_dense, top

top1 = top3 = refuse_ok = n_in = n_out = 0
for question, expected in TESTS:
    best, top = hybrid_top(question)
    folders = [chunks[i][0] for i in top]
    if expected is None:
        n_out += 1
        ok = best < THRESHOLD
        refuse_ok += ok
        print("PASS" if ok else "FAIL", "| should refuse |", question, f"({best:.2f})")
    else:
        n_in += 1
        acceptable = [expected] if isinstance(expected, str) else expected
        correct_top1 = folders[0] in acceptable
        correct_top3 = any(f in acceptable for f in folders)
        accepted = best >= THRESHOLD

        if correct_top1 and accepted:
            status = "PASS"
            top1 += 1
            top3 += 1
        elif correct_top3 and accepted:
            status = "TOP3"
            top3 += 1
        elif correct_top1 and not accepted:
            status = "FALSE_REFUSAL"
        elif correct_top3 and not accepted:
            status = "TOP3_REFUSED"
        else:
            status = "WRONG_RETRIEVAL"

        print(f"{status:15} | {best:.3f} | {question} | top: {folders} | expected: {acceptable}")

        if status != "PASS":
            with open("failures.txt", "a", encoding="utf-8") as fh:
                fh.write(f"\nQ: {question}\nSTATUS: {status}\nEXPECTED: {acceptable}\n")
                for i in top:
                    fh.write(f"  - {chunks[i][0]}: {chunks[i][1][:300]!r}\n")

print(f"\nTop-1 correct: {top1}/{n_in}   Top-3 correct: {top3}/{n_in}   Correct refusals: {refuse_ok}/{n_out}")