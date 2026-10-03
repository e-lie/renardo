Alpha release. The installers are not signed: your OS will warn you the first time you open Renardo.

SuperCollider is not bundled, install it separately.

## Downloads

- Linux: `.AppImage` or `.deb` (an Arch `PKGBUILD` based on the deb is attached)
- macOS Apple Silicon: `.dmg` named `aarch64`/`arm64`
- macOS Intel: `.dmg` named `x64`/`x86_64`
- Windows: `-setup.exe`

## macOS (Gatekeeper)

If macOS says the app is damaged or from an unidentified developer, drag Renardo to Applications, then either right-click the app, choose Open, and confirm, or run:

    xattr -dr com.apple.quarantine /Applications/Renardo.app

## Windows (SmartScreen)

If SmartScreen shows "Windows protected your PC", click "More info", then "Run anyway".
