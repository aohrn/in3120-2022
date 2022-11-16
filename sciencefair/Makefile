.PHONY = clean make
$FIGS  = papers/boyer-moore-1977.pdf uio.pdf

boyer-moore.pdf: boyer-moore.tex ref.bib $(FIGS)
	latexmk -pdf -bibtex boyer-moore.tex

horspool: horspool.c
	gcc -Wall -O3 horspool.c -o horspool

clean:
	latexmk -C -pdf -bibtex boyer-moore.tex
	rm boyer-moore.nav
	rm boyer-moore.run.xml
	rm boyer-moore.snm
