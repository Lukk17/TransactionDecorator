
## Linux Installers

---

### Debian .deb packages

`createDebFile.sh` script have to be run from main project:

```shell
./linux/createDebFile.sh 
```

It will build .deb file in `/build` folder in project root directory

In `/linux/debian/` directory there is project structure as will be built with a script.  
This is only for preview, it is possible to create debian package this way, 
but it is required to manually copy all project files to correct directories - script automates this.  
Anyway, it can be built with :
```shell
dpkg-deb --build ./linux/debian/transaction_decorator
```
Launched from project root directory.

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
Before re-compiling snap delete old compiled snap package from directory.  
For debug use(it will shell into built snap):
```shell
snapcraft --debug
```

If prompt for 
```text
Support for 'multipass' needs to be set up. Would you like to do it now?
```
Accept (y).  
Built package will be in `linux` directory.  

To install snap from compiled package:
```shell
sudo snap install --dangerous ./transaction-decorator_1.0.0_amd64.snap
```

To run snap from terminal (and see logs):
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

For base22:  
```shell
sudo usermod -a -G lxd $USER
```
```shell
newgrp lxd
```
```shell
lxd init
```
