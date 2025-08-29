#!/bin/bash

# Build the REAPER extension
cargo build --release

# Get the output filename based on OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    EXT_FILE="target/release/librenardo_reaper_ext.so"
    REAPER_EXT="reaper_renardo.so"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    EXT_FILE="target/release/librenardo_reaper_ext.dylib"
    REAPER_EXT="reaper_renardo.dylib"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    EXT_FILE="target/release/renardo_reaper_ext.dll"
    REAPER_EXT="reaper_renardo.dll"
else
    echo "Unknown OS: $OSTYPE"
    exit 1
fi

if [ -f "$EXT_FILE" ]; then
    echo "Build successful!"
    echo "Extension file: $EXT_FILE"
    echo ""
    echo "To install in REAPER:"
    echo "1. Copy $EXT_FILE to your REAPER UserPlugins directory"
    echo "2. Rename it to $REAPER_EXT"
    echo "3. Restart REAPER"
    echo ""
    echo "REAPER UserPlugins locations:"
    echo "  - Linux: ~/.config/REAPER/UserPlugins/"
    echo "  - macOS: ~/Library/Application Support/REAPER/UserPlugins/"
    echo "  - Windows: %APPDATA%\\REAPER\\UserPlugins\\"
else
    echo "Build failed!"
    exit 1
fi