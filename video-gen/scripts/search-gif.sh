#!/usr/bin/env bash
# Search for GIFs using Tenor API (free, no key required for limited use)
# Usage: ./search-gif.sh "search term" [limit]
#
# Returns JSON array of GIF URLs suitable for video-gen configs.
# The URLs can be used directly in gifUrl fields of scene data.

QUERY="${1:?Usage: search-gif.sh 'search term' [limit]}"
LIMIT="${2:-5}"

# Tenor v2 API (anonymous access with limited rate)
# For production use, get a free API key at https://developers.google.com/tenor
API_KEY="${TENOR_API_KEY:-AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ}"

echo "🔍 Searching Tenor for: \"$QUERY\" (limit: $LIMIT)"
echo ""

RESPONSE=$(curl -s "https://tenor.googleapis.com/v2/search?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")&key=$API_KEY&limit=$LIMIT&media_filter=gif")

if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); results=d.get('results',[]); [print(f'  {i+1}. {r[\"content_description\"][:60]}\n     URL: {r[\"media_formats\"][\"gif\"][\"url\"]}\n     Size: {r[\"media_formats\"][\"gif\"][\"size\"]//1024}KB') for i,r in enumerate(results)]" 2>/dev/null; then
    echo ""
    echo "📋 JSON URLs for config:"
    echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
urls = [r['media_formats']['gif']['url'] for r in d.get('results', [])]
print(json.dumps(urls, indent=2))
"
else
    echo "❌ Error: Could not fetch GIFs. Response:"
    echo "$RESPONSE" | head -5
    echo ""
    echo "💡 Tip: Set TENOR_API_KEY env var for better rate limits"
    echo "   Get free key at: https://developers.google.com/tenor"
fi
