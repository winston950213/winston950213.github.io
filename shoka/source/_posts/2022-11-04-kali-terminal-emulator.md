---
title: Kali Linux Failed to launch preferred application for category 'TerminalEmulator'
  and all files missing
date: '2022-11-04T22:23:46+08:00'
permalink: 2022/11/04/Kali-Linux-Failed-to-launch-preferred-application-for-category-TerminalEmulator-and-all-files-missing/
categories:
- 操作备忘
tags:
- bug
- kali
comment: false
fancybox: true
---

I had a similar problem today. Installed Kali 2020.4 64-bit and ran sudo apt update && sudo apt upgrade as you described. Rebooted the system and was unable to open terminal or browse files (I only tried via the "Home" folder on the desktop).

<!-- more -->

I was still able to open QTerminal directly from the application menu to run commands. I was able to fix this by running the following. Hopefully this works for you.

```shell
sudo apt update
sudo apt upgrade
```

This returned a list of packages that "were automatically installed and are no longer required:" Remove these packages with the below command.

`sudo apt autoremove`
Reboot. Then run `sudo apt update && sudo apt upgrade` again. The following packages were required. Reboot again and terminal/file browsing should be working as expected.

I suspect one specific package "xfce4-helpers" is causing the issue. I'm new to Linux so not sure of the cause (hopefully someone can elaborate).

After completing the above steps, run `sudo apt-get install xfce4-helpers` .

After doing the above

- right click the terminal and remove it from panel
- then right click somewhere on the panel bar and go to "panel"
- next go to "Add New" then scroll down to verve terminal and click on it.
- Add it to the bar panel (it will show up next to notifications).
- Right click again and go to move and move it to where it was.
  (alternatively you can just go to app drop down menu and add Qterm to your desktop).
  原文指路 --> <https://superuser.com/questions/1614042/kali-linux-failed-to-launch-preferred-application-for-category-terminalemulator>
