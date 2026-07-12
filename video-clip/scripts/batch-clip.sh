#!/bin/bash
set -euo pipefail

# Batch video clip extraction script
# Usage: batch-clip.sh <youtube-url> <clips.json> <output_dir>

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIP_EXTRACT="$SCRIPT_DIR/clip-extract.sh"

# Check dependencies
check_dependencies() {
    if [[ ! -f "$CLIP_EXTRACT" ]]; then
        echo "Error: clip-extract.sh not found at: $CLIP_EXTRACT" >&2
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required for JSON parsing but not found" >&2
        echo "Install with: sudo apt-get install jq" >&2
        exit 1
    fi
}

# Parse arguments
parse_args() {
    if [[ $# -ne 3 ]]; then
        echo "Usage: $0 <youtube-url> <clips.json> <output_dir>" >&2
        echo "" >&2
        echo "clips.json format:" >&2
        echo '[' >&2
        echo '  {"id": "clip1", "start": "00:05:30", "end": "00:05:45", "label": "description"},' >&2
        echo '  {"id": "clip2", "start": "330", "end": "345", "label": "description"}' >&2
        echo ']' >&2
        exit 1
    fi

    YOUTUBE_URL="$1"
    CLIPS_JSON="$2"
    OUTPUT_DIR="$3"

    # Validate clips.json exists
    if [[ ! -f "$CLIPS_JSON" ]]; then
        echo "Error: clips.json not found: $CLIPS_JSON" >&2
        exit 1
    fi

    # Validate JSON format
    if ! jq empty "$CLIPS_JSON" 2>/dev/null; then
        echo "Error: Invalid JSON in $CLIPS_JSON" >&2
        exit 1
    fi

    # Validate it's an array
    if [[ "$(jq -r 'type' "$CLIPS_JSON")" != "array" ]]; then
        echo "Error: clips.json must contain a JSON array" >&2
        exit 1
    fi
}

# Process clips
process_clips() {
    local url="$1"
    local clips_json="$2"
    local output_dir="$3"

    # Create output directory
    mkdir -p "$output_dir"

    # Count clips
    local total_clips
    total_clips="$(jq 'length' "$clips_json")"

    if [[ "$total_clips" -eq 0 ]]; then
        echo "Warning: No clips found in $clips_json" >&2
        return
    fi

    echo "=== Batch Clip Extraction ==="
    echo "URL: $url"
    echo "Total clips: $total_clips"
    echo "Output directory: $output_dir"
    echo ""

    # Initialize manifest
    local manifest_file="$output_dir/manifest.json"
    local manifest_data='{"youtube_url":"'"$url"'","processed_at":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'","clips":[]}'

    # Process each clip
    local index=0
    local success_count=0
    local fail_count=0

    while [[ $index -lt $total_clips ]]; do
        local clip
        clip="$(jq -r ".[$index]" "$clips_json")"

        local clip_id
        local start_time
        local end_time
        local label

        clip_id="$(echo "$clip" | jq -r '.id // "clip'"$index"'"')"
        start_time="$(echo "$clip" | jq -r '.start')"
        end_time="$(echo "$clip" | jq -r '.end')"
        label="$(echo "$clip" | jq -r '.label // ""')"

        # Validate required fields
        if [[ "$start_time" == "null" || "$end_time" == "null" ]]; then
            echo "Error: Clip at index $index missing start or end time" >&2
            ((fail_count++))
            ((index++))
            continue
        fi

        echo "[$((index + 1))/$total_clips] Processing clip: $clip_id"
        echo "  Start: $start_time"
        echo "  End: $end_time"
        [[ -n "$label" ]] && echo "  Label: $label"

        local output_file="$output_dir/${clip_id}.mp4"
        local clip_result

        # Extract clip
        if "$CLIP_EXTRACT" "$url" "$start_time" "$end_time" "$output_file" 2>&1 | tee /tmp/clip-extract-$$.log; then
            echo "  Success: $output_file"
            clip_result='{"id":"'"$clip_id"'","start":"'"$start_time"'","end":"'"$end_time"'","label":"'"$label"'","output":"'"$output_file"'","status":"success"}'
            ((success_count++))
        else
            echo "  Failed: $clip_id" >&2
            clip_result='{"id":"'"$clip_id"'","start":"'"$start_time"'","end":"'"$end_time"'","label":"'"$label"'","status":"failed","error":"See logs"}'
            ((fail_count++))
        fi

        # Add to manifest
        manifest_data="$(echo "$manifest_data" | jq ".clips += [$clip_result]")"

        echo ""
        ((index++))
    done

    # Add summary to manifest
    manifest_data="$(echo "$manifest_data" | jq ". += {\"summary\":{\"total\":$total_clips,\"success\":$success_count,\"failed\":$fail_count}}")"

    # Write manifest
    echo "$manifest_data" | jq '.' > "$manifest_file"

    echo "=== Batch Processing Complete ==="
    echo "Total clips: $total_clips"
    echo "Successful: $success_count"
    echo "Failed: $fail_count"
    echo ""
    echo "Manifest: $manifest_file"
    echo "Clips directory: $output_dir"

    # List created files
    if [[ $success_count -gt 0 ]]; then
        echo ""
        echo "Created files:"
        find "$output_dir" -name "*.mp4" -type f -exec basename {} \; | sort
    fi

    # Return non-zero if any clips failed
    if [[ $fail_count -gt 0 ]]; then
        return 1
    fi
}

# Main execution
main() {
    check_dependencies
    parse_args "$@"

    process_clips "$YOUTUBE_URL" "$CLIPS_JSON" "$OUTPUT_DIR"
}

main "$@"
