#!/bin/bash
set -euo pipefail

# Video clip extraction script using yt-dlp + ffmpeg
# Usage: clip-extract.sh <youtube-url> <start_time> <end_time> <output_path> [--format mp4|webm] [--resolution 720|1080]

# Binary paths
YTDLP="$HOME/.youtube-venv/bin/yt-dlp"
FFMPEG="$HOME/.local/bin/ffmpeg"
FFPROBE="$HOME/.local/bin/ffprobe"

# Check required binaries
check_binaries() {
    local missing=()

    [[ ! -f "$YTDLP" ]] && missing+=("yt-dlp at $YTDLP")
    [[ ! -f "$FFMPEG" ]] && missing+=("ffmpeg at $FFMPEG")
    [[ ! -f "$FFPROBE" ]] && missing+=("ffprobe at $FFPROBE")

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Error: Missing required binaries:" >&2
        printf '  - %s\n' "${missing[@]}" >&2
        exit 1
    fi
}

# Parse arguments
parse_args() {
    if [[ $# -lt 4 ]]; then
        echo "Usage: $0 <youtube-url> <start_time> <end_time> <output_path> [--format mp4|webm] [--resolution 720|1080]" >&2
        echo "" >&2
        echo "Time formats: HH:MM:SS or seconds" >&2
        echo "Default: 720p mp4 with audio" >&2
        exit 1
    fi

    YOUTUBE_URL="$1"
    START_TIME="$2"
    END_TIME="$3"
    OUTPUT_PATH="$4"
    shift 4

    # Defaults
    FORMAT="mp4"
    RESOLUTION="720"

    # Parse optional arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --format)
                FORMAT="$2"
                shift 2
                ;;
            --resolution)
                RESOLUTION="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1" >&2
                exit 1
                ;;
        esac
    done

    # Validate format
    if [[ "$FORMAT" != "mp4" && "$FORMAT" != "webm" ]]; then
        echo "Error: Format must be mp4 or webm, got: $FORMAT" >&2
        exit 1
    fi

    # Validate resolution
    if [[ "$RESOLUTION" != "720" && "$RESOLUTION" != "1080" ]]; then
        echo "Error: Resolution must be 720 or 1080, got: $RESOLUTION" >&2
        exit 1
    fi
}

# Convert time to seconds (supports HH:MM:SS or plain seconds)
time_to_seconds() {
    local time="$1"

    # Check if already in seconds (integer or float)
    if [[ "$time" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        echo "$time"
        return
    fi

    # Convert HH:MM:SS to seconds
    if [[ "$time" =~ ^([0-9]+):([0-9]+):([0-9]+)(\.[0-9]+)?$ ]]; then
        local hours="${BASH_REMATCH[1]}"
        local minutes="${BASH_REMATCH[2]}"
        local seconds="${BASH_REMATCH[3]}"
        local fraction="${BASH_REMATCH[4]:-}"

        echo "$((10#$hours * 3600 + 10#$minutes * 60 + 10#$seconds))$fraction"
        return
    fi

    # Try MM:SS format
    if [[ "$time" =~ ^([0-9]+):([0-9]+)(\.[0-9]+)?$ ]]; then
        local minutes="${BASH_REMATCH[1]}"
        local seconds="${BASH_REMATCH[2]}"
        local fraction="${BASH_REMATCH[3]:-}"

        echo "$((10#$minutes * 60 + 10#$seconds))$fraction"
        return
    fi

    echo "Error: Invalid time format: $time (use HH:MM:SS or seconds)" >&2
    exit 1
}

# Get format selection string for yt-dlp
get_format_selection() {
    local res="$1"

    if [[ "$res" == "1080" ]]; then
        echo "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    else
        echo "bestvideo[height<=720]+bestaudio/best[height<=720]"
    fi
}

# Download clip using segment download (primary method)
download_segment() {
    local url="$1"
    local start="$2"
    local end="$3"
    local output="$4"
    local format="$5"
    local resolution="$6"

    local format_sel
    format_sel="$(get_format_selection "$resolution")"

    local temp_output="${output}.temp.${format}"

    echo "Attempting segment download: $start to $end"

    if "$YTDLP" \
        -f "$format_sel" \
        --download-sections "*${start}-${end}" \
        --merge-output-format "$format" \
        -o "$temp_output" \
        "$url" 2>&1; then

        mv "$temp_output" "$output"
        echo "Successfully downloaded segment to: $output"
        return 0
    else
        echo "Segment download failed, falling back to full download + trim" >&2
        [[ -f "$temp_output" ]] && rm -f "$temp_output"
        return 1
    fi
}

# Download full video and trim with ffmpeg (fallback method)
download_and_trim() {
    local url="$1"
    local start="$2"
    local end="$3"
    local output="$4"
    local format="$5"
    local resolution="$6"

    local format_sel
    format_sel="$(get_format_selection "$resolution")"

    local temp_full
    temp_full="$(mktemp -u --suffix=.${format})"

    echo "Downloading full video..."

    "$YTDLP" \
        -f "$format_sel" \
        --merge-output-format "$format" \
        -o "$temp_full" \
        "$url"

    echo "Trimming video from $start to $end..."

    local start_sec
    local end_sec
    start_sec="$(time_to_seconds "$start")"
    end_sec="$(time_to_seconds "$end")"
    local duration
    duration="$(echo "$end_sec - $start_sec" | bc)"

    "$FFMPEG" \
        -ss "$start_sec" \
        -i "$temp_full" \
        -t "$duration" \
        -c copy \
        -avoid_negative_ts make_zero \
        "$output" \
        -y

    rm -f "$temp_full"
    echo "Successfully created clip: $output"
}

# Main execution
main() {
    check_binaries
    parse_args "$@"

    # Create output directory if needed
    local output_dir
    output_dir="$(dirname "$OUTPUT_PATH")"
    mkdir -p "$output_dir"

    # Ensure output path has correct extension
    if [[ ! "$OUTPUT_PATH" =~ \.$FORMAT$ ]]; then
        OUTPUT_PATH="${OUTPUT_PATH%.*}.$FORMAT"
    fi

    echo "=== Video Clip Extraction ==="
    echo "URL: $YOUTUBE_URL"
    echo "Start: $START_TIME"
    echo "End: $END_TIME"
    echo "Output: $OUTPUT_PATH"
    echo "Format: $FORMAT"
    echo "Resolution: ${RESOLUTION}p"
    echo ""

    # Try segment download first, fall back to full download + trim
    if ! download_segment "$YOUTUBE_URL" "$START_TIME" "$END_TIME" "$OUTPUT_PATH" "$FORMAT" "$RESOLUTION"; then
        download_and_trim "$YOUTUBE_URL" "$START_TIME" "$END_TIME" "$OUTPUT_PATH" "$FORMAT" "$RESOLUTION"
    fi

    # Verify output file
    if [[ ! -f "$OUTPUT_PATH" ]]; then
        echo "Error: Output file was not created: $OUTPUT_PATH" >&2
        exit 1
    fi

    # Show file info
    local filesize
    filesize="$(du -h "$OUTPUT_PATH" | cut -f1)"
    echo ""
    echo "=== Extraction Complete ==="
    echo "File: $OUTPUT_PATH"
    echo "Size: $filesize"

    # Show duration if ffprobe available
    if [[ -f "$FFPROBE" ]]; then
        local duration
        duration="$("$FFPROBE" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_PATH" 2>/dev/null || echo "unknown")"
        if [[ "$duration" != "unknown" ]]; then
            printf "Duration: %.2f seconds\n" "$duration"
        fi
    fi
}

main "$@"
