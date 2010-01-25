clean:
	rm -f $(wildcard *.pyc) *~;

translate:
	mkdir -p ./locale/ru/LC_MESSAGES; \
	mkdir -p ./locale/pots; \
	for i in `ls *.py`; do \
	    NAME=`basename $$i .py`; \
	    xgettext -d manager -p ./locale/pots -L Python --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --keyword=ugettext_noop --keyword=ugettext_lazy --keyword=ungettext_lazy:1,2 --from-code UTF-8 -o "$$NAME.pot" "$$i"; \
	done; \
	cd ./locale/pots; \
	POTS=`ls *.pot`; \
	msgcat -o ../project.pot $$POTS; \
	cd -; \
	rm -rf ./locale/pots; \
	if [ -f ./locale/ru/LC_MESSAGES/project.po ]; then \
	    msgmerge -o ./locale/ru/LC_MESSAGES/project.po ./locale/ru/LC_MESSAGES/project.po ./locale/project.pot; \
	else \
	    if [ -f ./locale/project.pot ]; then \
	        cp ./locale/project.pot ./locale/ru/LC_MESSAGES/project.po; \
            fi; \
	fi;

pomo:
	if [ -f locale/ru/LC_MESSAGES/project.po ]; then \
	    msgfmt -o locale/ru/LC_MESSAGES/project.mo locale/ru/LC_MESSAGES/project.po; \
	fi;
