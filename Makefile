.PHONY: release
VERSION := $(shell python3 setup.py --version)

release:
	echo $(shell git commit -m "Release v$(VERSION)")
	echo $(shell git tag -a v$(VERSION) -m "Version $(VERSION)")
	echo $(shell git push origin --tags)
