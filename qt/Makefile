
BASE=build/manager
DST=$(BASE)/src/manager
LCL=locale/ru/LC_MESSAGES

all:
	echo "Usage: make distmanager"

distmanager:
	mkdir -p $(DST) $(DST)/$(LCL)
	cp ./manager/*.py ./manager/*.css $(DST)/
	cp ./manager/$(LCL)/*mo $(DST)/$(LCL)/
	cp ./manager/install/* $(BASE)/
	cd $(BASE); python setup.py sdist; cd -

