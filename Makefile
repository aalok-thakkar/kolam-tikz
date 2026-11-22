EXAMPLES := 01-minimal-loop 02-hourglass 03-braided-ladder 04-diamond-weave 05-one-stroke-21 07-nine-row-diamond
SMOKE_TEST := foreach-smoke

# Fix PDF timestamps (the 0.1.0 release date) so rebuilds are byte-identical.
export SOURCE_DATE_EPOCH := 1795305600

.PHONY: all examples gallery preview check test verify tidy clean

all: examples gallery

examples:
	@for example in $(EXAMPLES); do \
		(cd examples && TEXINPUTS=../tex: latexmk -pdf -interaction=nonstopmode -halt-on-error $$example.tex) || exit $$?; \
	done

gallery: examples
	cd examples && TEXINPUTS=../tex: latexmk -pdf -interaction=nonstopmode -halt-on-error 06-gallery.tex

preview: gallery
	mkdir -p docs/assets
	pdftoppm -png -singlefile -r 180 examples/06-gallery.pdf docs/assets/gallery

check:
	python3 tools/kolam-audit.py examples/01-minimal-loop.tex
	python3 tools/kolam-audit.py examples/02-hourglass.tex --require-one
	python3 tools/kolam-audit.py examples/03-braided-ladder.tex --drop-fan --require-one
	python3 tools/kolam-audit.py examples/04-diamond-weave.tex
	python3 tools/kolam-audit.py examples/05-one-stroke-21.tex --require-one
	python3 tools/kolam-audit.py examples/07-nine-row-diamond.tex

test:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
	cd tests && TEXINPUTS=../tex: latexmk -pdf -interaction=nonstopmode -halt-on-error $(SMOKE_TEST).tex

verify: all check test

tidy:
	@for example in $(EXAMPLES) 06-gallery; do \
		(cd examples && latexmk -c $$example.tex); \
	done
	cd tests && latexmk -C $(SMOKE_TEST).tex

clean:
	@for example in $(EXAMPLES) 06-gallery; do \
		(cd examples && latexmk -C $$example.tex); \
	done
	cd tests && latexmk -C $(SMOKE_TEST).tex
