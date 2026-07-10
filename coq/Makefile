COQMAKEFILE ?= coq_makefile

.PHONY: all clean

all: Makefile.coq
	$(MAKE) -f Makefile.coq

Makefile.coq: _CoqProject $(wildcard theories/*.v)
	$(COQMAKEFILE) -f _CoqProject -o Makefile.coq

clean:
	@if [ -f Makefile.coq ]; then $(MAKE) -f Makefile.coq clean; fi
	rm -f Makefile.coq Makefile.coq.conf
