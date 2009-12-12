DOT=$(wildcard *.dot)
DOTPNG=$(patsubst %.dot,%.dot.png,$(DOT))
FDPPNG=$(patsubst %.dot,%.fdp.png,$(DOT))

all: $(DOTPNG) $(FDPPNG)

clean: $(DOTPNG) $(FDPPNG)
	rm -rf *.png *~

# пример использования временного файла для изменения кодировки
#%.utf: %.dot
#	iconv -t utf-8 $< > $*.utf

%.dot.png: %.dot
	dot -Tpng $< > $@

%.fdp.png: %.dot
	fdp -Tpng $< > $@
