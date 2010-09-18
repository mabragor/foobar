STYLE=rose
PNG=$(patsubst %.seq, %.png, $(wildcard *.seq))

all: $(PNG)

clean:
		rm -f $(PNG) *~

%.png: %.seq
		python ./getuml.py $< $@ $(STYLE)
