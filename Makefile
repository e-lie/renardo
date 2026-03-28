.PHONY: format publish_beta publish_electron_release download_artifacts

VERSION_FILE := VERSION
CURRENT_VERSION := $(shell cat $(VERSION_FILE))

format:
	uv run ruff format src/
	cd webclient_fresh && npm run format

publish_beta:
	@echo "Current version: $(CURRENT_VERSION)"
	@python3 -c "import re; v='$(CURRENT_VERSION)'; m=re.match(r'^(.+?)(dev|a|alpha|b|beta|rc)(\d+)\$$',v); print(m.group(1)+m.group(2)+str(int(m.group(3))+1) if m else v+'.1')" > .new_version
	@NEW_VERSION=$$(cat .new_version) && \
		echo "New version: $$NEW_VERSION" && \
		echo "$$NEW_VERSION" > $(VERSION_FILE) && \
		sed -i 's/"version": "[^"]*"/"version": "'$$NEW_VERSION'"/' webclient_fresh/package.json && \
		git add $(VERSION_FILE) webclient_fresh/package.json && \
		git commit -m "Bump version to $$NEW_VERSION" && \
		git tag "v$$NEW_VERSION" && \
		git push && \
		git push origin "v$$NEW_VERSION" && \
		rm -f .new_version
	@echo "Published v$$(cat $(VERSION_FILE))"

download_artifacts:
	@echo "Clearing ignored_files/artifacts..."
	@rm -rf ignored_files/artifacts && mkdir -p ignored_files/artifacts
	@echo "Downloading latest release artifacts..."
	gh release download --repo e-lie/renardo --dir ignored_files/artifacts
	@echo "Done."

publish_electron_release:
	@echo "Triggering electron release for v$(CURRENT_VERSION)"
	gh workflow run publish-electron-release.yml --field tag=v$(CURRENT_VERSION)
