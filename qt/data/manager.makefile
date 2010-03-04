VERSION=0.1.0
PROJECT=pyqounter-manager
PROJECT_EGG=pyqounter_manager-$(VERSION).egg-info

clean:
	rm -rf *.py[co] *~

install:
	python setup.py install --prefix=$(DESTDIR)

uninstall:
	cd $(DESTDIR)/lib/python2.5/site-packages/; \
	rm -rf $(PROJECT); \
	rm -r $(PROJECT_EGG); \
	cd -
