# List of Files

* byuminecraft.png (icon used for server app)
* minecraft.service (describes system service) 
* ServerControl.py (Gui server interface)
* 


## Setting up
Place all files in Server Scripts into the server's folder.
Update launch server to properly have the server launch command
In serverWrapper.py replace "<SERVER Path>" with the full path to the server folder (ie /home/byumc/Eden/)
Run createFifos.sh (the one you copied to the server's folder). This will create serverInput and serverOutput in the server folder.


edit the minecraft.service file to have the path to the server instead of "<Server Directory>"
Copy the file to /etc/systemd/system

run the command sudo systemctl enable minecraft.service

update the minecraftTerminal.desktop file replacing <Util Directory> with the location of this directory. 

Copy this file to `/usr/share/applications` This will add the terminal util to the application list. In the home menu, right click it and select add to home menu (to add to sidebar for convenience).

run the command `sudo visudo` this will open a config file. At the very bottom add the following lines.

```
%minecraft ALL = NOPASSWD: /usr/bin/systemctl start minecraft.service
%minecraft ALL = NOPASSWD: /usr/bin/systemctl restart minecraft.service
%minecraft ALL = NOPASSWD: /usr/bin/systemctl stop minecraft.service
```

Run the command `sudo group add minecraft`

For each user on the computer (byumc used as example) (that might use the server)
Run the command `usermod -a -G minecraft byumc`

Copy minecraft.cron to /etc/cron.d

 (replacing <Server Path>) and changing the times as desired (its in MM HH) (warn of restart should be scheduled ~5-6 min before shutdown command 

Reboot computer.

It should be all setup.

