STYLE=rose
PNG=$(patsubst %.seq, %.png, $(wildcard *.seq))
DOT=$(wildcard *.dot)
DOTSVG=$(patsubst %.dot,%.dot.svg,$(DOT))
FDPSVG=$(patsubst %.dot,%.fdp.svg,$(DOT))

all: $(PNG) $(DOTSVG) $(FDPSVG)

clean:
		rm -f $(PNG) $(DOTSVG) $(FDPSVG) *~

%.png: %.seq
		python ./getuml.py $< $@ $(STYLE)

%.fdp.svg: %.dot
		fdp -Tsvg $< > $@

%.dot.svg: %.dot
		dot -Tsvg $< > $@
