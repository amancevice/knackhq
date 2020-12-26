SDIST := dist/$(shell python setup.py --fullname).tar.gz

.PHONY: all clean test test upload

all: $(SDIST)

clean:
	rm -rf dist

test: coverage.xml

upload: $(SDIST)
	twine upload $<

$(SDIST): coverage.xml
	python setup.py sdist

coverage.xml: $(shell find knackhq tests -name '*.py')
	flake8 $^
	pytest || (rm $@ ; exit 1)
