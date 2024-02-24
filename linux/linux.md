
## Linux Installers

---

### Debian .deb packages

`createDebFile.sh` script have to be run from main project:

```shell
./linux/createDebFile.sh 
```

it will build .deb file in `/build` folder in project root directory

in `/linux/debian/` directory there is project structure as will be build with script.  
This is only for preview, it is possible to create debian package this way  
but it required to manually copy all project files to correct directories - script automates this.  
Anyway it can be build with :
```shell
dpkg-deb --build ./linux/debian/transaction_decorator
```
launched from project root directory.

---
