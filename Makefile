.PHONY: release
VERSION := $(shell python3 setup.py --version)

release:
	@ git commit --allow-empty -m "Release $(VERSION)"
	@ git tag -a $(VERSION) -m "Version $(VERSION)"
	@ git push origin --tags
