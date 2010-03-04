PROJECT=pyqounter-manager
VERSION=0.1.0

BASE=build/manager
DST=$(BASE)/src/manager
LCL=locale/ru/LC_MESSAGES

DEBBASE=debianize

all:
	echo "Usage: make distmanager"

distmanager:
	mkdir -p $(DST) $(DST)/$(LCL)
	cp ./manager/*.py ./manager/*.css $(DST)/
	cp ./manager/$(LCL)/*mo $(DST)/$(LCL)/
	cp ./manager/install/* $(BASE)/
	cd $(BASE); python setup.py sdist; cd -

debianize:
	mkdir -p $(DEBBASE)
	cd $(DEBBASE); tar xzf ../$(BASE)/dist/$(PROJECT)-$(VERSION).tar.gz; cd -
	cp data/manager.makefile $(DEBBASE)/$(PROJECT)-$(VERSION)/Makefile
	cd $(DEBBASE)/$(PROJECT)-$(VERSION)/; \
	test -d debian || mkdir -p debian; \
	test -f debian/changelog || debchange --create --package $(PROJECT) -v $(VERSION); \
	test -f debian/compat || echo "6" >> ./debian/compat; \
	cp ../../data/rules ./debian/rules; \
	sed -e "s/<PROJECT>/$(PROJECT)/" \
	    -e "s/<FULLNAME>/$(DEBFULLNAME)/" \
	    -e "s/<EMAIL>/<$(DEBEMAIL)>/" \
	    < ../../data/control > ./debian/control; \
	sed -e "s/<DATE>/`LANG=C date`/" \
	    -e "s/<FULLNAME>/$(DEBFULLNAME)/" \
	    -e "s/<EMAIL>/<$(DEBEMAIL)>/" \
	    < ../../data/copyright > ./debian/copyright; \
	echo "Now you're ready to build the package."
	echo "Just do:"
	echo "    cd $(DEBBASE)/$(PROJECT)-$(VERSION)"
	echo "    debuild -k<YOUR_PGP_KEY>"

