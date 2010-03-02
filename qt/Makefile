PROJECT=pyqounter-manager
VERSION=0.1.0

BASE=build/manager
DST=$(BASE)/src/manager
LCL=locale/ru/LC_MESSAGES

DEB_BASE=package
BASENAME=$(PROJECT)-$(VERSION)
ARCHIVE=$(BASENAME).tar.gz
ARCH4DEB=$(BASENAME).orig.tar.gz

all:
	echo "Usage: make distmanager"

distmanager:
	mkdir -p $(DST) $(DST)/$(LCL)
	cp ./manager/*.py ./manager/*.css $(DST)/
	cp ./manager/$(LCL)/*mo $(DST)/$(LCL)/
	cp ./manager/install/* $(BASE)/
	cd $(BASE); python setup.py sdist; cd -

debmanager:
	mkdir -p $(DEB_BASE)/manager
	cd $(DEB_BASE)/manager; \
	test -L $(ARCHIVE) || ln -s ../../build/manager/dist/$(ARCHIVE); \
	test -d $(BASENAME) || tar -xzf $(ARCHIVE); \
	cp $(ARCHIVE) $(ARCH4DEB); \
	cd $(BASENAME); \
	test -d debian || mkdir -p debian; \
	test -f debian/changelog || debchange --create --package $(PROJECT) -v $(VERSION); \
	test -f debian/compat || echo "7" >> ./debian/compat; \
	cp ../../../data/rules ./debian/rules; \
	sed -e "s/<PROJECT>/$(PROJECT)/" \
	    -e "s/<FULLNAME>/$(DEBFULLNAME)/" \
	    -e "s/<EMAIL>/<$(DEBEMAIL)>/" \
	    < ../../../data/control > ./debian/control; \
	sed -e "s/<DATE>/`LANG=C date`/" \
	    -e "s/<FULLNAME>/$(DEBFULLNAME)/" \
	    -e "s/<EMAIL>/<$(DEBEMAIL)>/" \
	    < ../../../data/copyright > ./debian/copyright; \


