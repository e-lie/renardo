#!/usr/bin/env bash
# watch_logs.sh - Open tmux session with splits for each Renardo log file

set -e

# Session name
SESSION_NAME="renardo-logs"

# Array to store excluded log files
EXCLUDE_FILES=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--exclude)
            if [ -z "$2" ]; then
                echo "Error: --exclude requires a filename argument"
                exit 1
            fi
            EXCLUDE_FILES+=("$2")
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [-e|--exclude FILENAME] ..."
            echo ""
            echo "Options:"
            echo "  -e, --exclude FILENAME    Exclude a log file from the watch session"
            echo "                            Can be used multiple times"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                              # Watch all renardo logs"
            echo "  $0 -e renardo-main.log                         # Exclude main log"
            echo "  $0 -e renardo-main.log -e renardo-to_webclient.log  # Exclude multiple"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Find all renardo log files in /tmp
ALL_LOG_FILES=(/tmp/renardo*.log)

# Filter out excluded files
LOG_FILES=()
for log in "${ALL_LOG_FILES[@]}"; do
    basename_log=$(basename "$log")
    excluded=false
    for exclude in "${EXCLUDE_FILES[@]}"; do
        if [ "$basename_log" == "$exclude" ] || [ "$log" == "$exclude" ]; then
            excluded=true
            break
        fi
    done
    if [ "$excluded" == false ]; then
        LOG_FILES+=("$log")
    fi
done

# Show excluded files if any
if [ ${#EXCLUDE_FILES[@]} -gt 0 ]; then
    echo "Excluding ${#EXCLUDE_FILES[@]} file(s):"
    for exclude in "${EXCLUDE_FILES[@]}"; do
        echo "  - $exclude"
    done
    echo ""
fi

# Check if any log files exist
if [ ${#LOG_FILES[@]} -eq 0 ]; then
    if [ ${#ALL_LOG_FILES[@]} -eq 0 ] || [ ! -f "${ALL_LOG_FILES[0]}" ]; then
        echo "No Renardo log files found in /tmp"
        echo "Expected files like: /tmp/renardo-main.log, /tmp/renardo-to_webclient.log, etc."
    else
        echo "No log files to watch (all files were excluded)"
    fi
    exit 1
fi

echo "Watching ${#LOG_FILES[@]} log file(s):"
for log in "${LOG_FILES[@]}"; do
    echo "  - $log"
done
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed"
    echo "Install it with: sudo pacman -S tmux  (on Arch)"
    exit 1
fi

# Kill existing session if it exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Killing existing session '$SESSION_NAME'..."
    tmux kill-session -t "$SESSION_NAME"
fi

# Create new tmux session
echo "Creating tmux session '$SESSION_NAME'..."

# Start the session with the first log file
tmux new-session -d -s "$SESSION_NAME" "tail -f ${LOG_FILES[0]}"
tmux select-pane -t 0 -T "$(basename ${LOG_FILES[0]})"

# Add remaining log files with splits
for i in "${!LOG_FILES[@]}"; do
    if [ $i -eq 0 ]; then
        continue  # Skip first file (already created)
    fi

    log="${LOG_FILES[$i]}"

    # Alternate between vertical and horizontal splits
    if [ $((i % 2)) -eq 1 ]; then
        # Vertical split
        tmux split-window -h -t "$SESSION_NAME" "tail -f $log"
    else
        # Horizontal split
        tmux split-window -v -t "$SESSION_NAME" "tail -f $log"
    fi

    # Set pane title
    tmux select-pane -t $i -T "$(basename $log)"
done

# Enable pane titles
tmux set-option -t "$SESSION_NAME" pane-border-status top
tmux set-option -t "$SESSION_NAME" pane-border-format "#{pane_title}"

# Tile all panes evenly
tmux select-layout -t "$SESSION_NAME" tiled

# Attach to the session
echo "Attaching to session '$SESSION_NAME'..."
echo ""
echo "Tips:"
echo "  - Press Ctrl+B then arrow keys to navigate between panes"
echo "  - Press Ctrl+B then 'd' to detach from session"
echo "  - Press Ctrl+B then 'x' to close a pane"
echo "  - Press Ctrl+B then 'z' to zoom/unzoom a pane"
echo "  - Run 'tmux attach -t $SESSION_NAME' to reattach later"
echo ""
sleep 2

tmux attach-session -t "$SESSION_NAME"
