.PHONY: release
VERSION := $(shell python3 setup.py --version)

release:
	@ git commit --allow-empty -m "Release v$(VERSION)"
	@ git tag -a v$(VERSION) -m "Version $(VERSION)"
	@ git push origin --tags
