.PHONY: format publish_beta publish_electron_release download_artifacts update_pkgbuild logs install_archlinux install_macos uninstall_macos

VERSION_FILE := VERSION
CURRENT_VERSION := $(shell cat $(VERSION_FILE))
GITHUB_REPO := e-lie/renardo

format:
	uv run ruff format src/
	cd webclient && npm run format

publish_beta:
	@echo "Current version: $(CURRENT_VERSION)"
	@python3 -c "import re; v='$(CURRENT_VERSION)'; m=re.match(r'^(.+?)(dev|a|alpha|b|beta|rc)(\d+)\$$',v); print(m.group(1)+m.group(2)+str(int(m.group(3))+1) if m else v+'.1')" > .new_version
	@NEW_VERSION=$$(cat .new_version) && \
		echo "New version: $$NEW_VERSION" && \
		echo "$$NEW_VERSION" > $(VERSION_FILE) && \
		awk '/"version":/{sub(/"version": "[^"]*"/, "\"version\": \"'$$NEW_VERSION'\"")}1' webclient/package.json > webclient/package.json.tmp && mv webclient/package.json.tmp webclient/package.json && \
		awk '/^pkgver=/{sub(/pkgver=.*/, "pkgver='$$NEW_VERSION'")}1' packaging/archlinux/PKGBUILD > packaging/archlinux/PKGBUILD.tmp && mv packaging/archlinux/PKGBUILD.tmp packaging/archlinux/PKGBUILD && \
		git add $(VERSION_FILE) webclient/package.json packaging/archlinux/PKGBUILD && \
		git commit -m "Bump version to $$NEW_VERSION" && \
		git tag "v$$NEW_VERSION" && \
		git push && \
		git push origin "v$$NEW_VERSION" && \
		gh release create "v$$NEW_VERSION" --prerelease --title "Renardo $$NEW_VERSION" --notes "Pre-release $$NEW_VERSION" && \
		rm -f .new_version
	@echo "Published v$$(cat $(VERSION_FILE))"

download_artifacts:
	@echo "Clearing ignored_files/artifacts..."
	@rm -rf ignored_files/artifacts && mkdir -p ignored_files/artifacts
	@echo "Downloading latest release artifacts..."
	gh release download --repo e-lie/renardo --dir ignored_files/artifacts --pattern '*'
	@echo "Done."

logs:
	lnav $(shell uv run python -c "from platformdirs import user_log_dir; print(user_log_dir('renardo'))")

install_archlinux:
	cd packaging/archlinux && makepkg -si && find . ! -name 'PKGBUILD' -mindepth 1 -delete

update_pkgbuild:
	awk '/^pkgver=/{sub(/pkgver=.*/, "pkgver=$(CURRENT_VERSION)")}1' packaging/archlinux/PKGBUILD > packaging/archlinux/PKGBUILD.tmp && mv packaging/archlinux/PKGBUILD.tmp packaging/archlinux/PKGBUILD

publish_electron:
	@echo "Triggering electron release for v$(CURRENT_VERSION)"
	gh workflow run publish-electron-release.yml --ref $(shell git rev-parse --abbrev-ref HEAD) --field tag=v$(CURRENT_VERSION)

GITHUB_RELEASE_API := https://api.github.com/repos/$(GITHUB_REPO)/releases/tags/v$(CURRENT_VERSION)

install_macos:
	@echo "Fetching release info for v$(CURRENT_VERSION)..."
	@mkdir -p /tmp/renardo-install
	@DMG_URL=$$(curl -s "$(GITHUB_RELEASE_API)" \
		| grep -o '"browser_download_url": *"[^"]*\.dmg"' \
		| grep -o 'https://[^"]*'); \
	if [ -z "$$DMG_URL" ]; then echo "Error: no DMG found for v$(CURRENT_VERSION)"; exit 1; fi; \
	echo "Downloading $$DMG_URL..."; \
	curl -L -o /tmp/renardo-install/renardo.dmg "$$DMG_URL"; \
	echo "Mounting DMG..."; \
	hdiutil attach /tmp/renardo-install/renardo.dmg -mountpoint /tmp/renardo-dmg -nobrowse -quiet; \
	echo "Copying Renardo.app to /Applications..."; \
	cp -R /tmp/renardo-dmg/Renardo.app /Applications/; \
	hdiutil detach /tmp/renardo-dmg -quiet; \
	echo "Removing quarantine attribute..."; \
	xattr -cr /Applications/Renardo.app; \
	rm -rf /tmp/renardo-install; \
	echo "Renardo installed successfully."

uninstall_macos:
	@echo "Uninstalling Renardo..."
	@rm -rf /Applications/Renardo.app
	@echo "Renardo removed from /Applications."
