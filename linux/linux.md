
## Linux Installers

---

### Debian .deb packages

`createDebFile.sh` script have to be run from the main project:

```shell
./linux/createDebFile.sh 
```

It will build .deb file in `/build` folder in project root directory.  

To install run:
```shell
sudo apt install ./build/transaction-decorator_1.0.1.deb -y
```
To run:
```shell
transaction-decorator
```
or from all apps.  

To remove run:
```shell
sudo apt remove transaction-decorator -y
```

Required packages installed on a system:
```shell
sudo apt install python3-pip
pip install --break-system-packages PySide6
sudo apt install python3-pandas python3-numpy python3-matplotlib
```

---

### Snap building

Ensure you have snapcraft installed:
```shell
sudo snap install snapcraft --classic
```

then in `linux` directory, where a script is located:
```shell
snapcraft
```
For debug use (it will shell into built snap):
```shell
snapcraft --debug
```

If prompt for 
```text
Support for 'multipass' needs to be set up. Would you like to do it now?
```
or
```
LXD is required but not installed. Do you wish to install LXD and configure it with the defaults?
```
you may need to init it, described [here](#lxd-setup-)
Accept (y).  
Built package will be in `linux` directory.  

To install snap from compiled package:
```shell
sudo snap install --dangerous --classic ./transaction-decorator_1.0.1_amd64.snap
```

To run snap from the terminal (and see logs):
```shell
transaction-decorator
```

To run with debugger shell:
```shell
snap run --shell
```

To clean snapcraft:
```shell
snapcraft clean
```

to remove snap:
```shell
sudo snap remove transaction-decorator
```

to run additional app mentioned in `apps` part of `snapcraft.yaml` for example to run copying scripts run:
```shell
snap run transaction-decorator.run-user-data-copy
```

#### lxd setup:  
```shell
sudo usermod -a -G lxd $USER
```
```shell
newgrp lxd
```
```shell
lxd init
```
leave default, if default is existing then use existing

### Troubleshooter

```
 File "/snap/snapcraft/10595/lib/python3.10/site-packages/packaging/version.py", line 200, in __init__
    raise InvalidVersion(f"Invalid version: '{version}'")
packaging.version.InvalidVersion: Invalid version: '5.21.1 LTS'
```
you need to update snapcraft to deal with it:
```
sudo snap refresh snapcraft
```
