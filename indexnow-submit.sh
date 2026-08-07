#!/bin/bash
# Ping IndexNow (Bing/Yandex) for daydrop.beatroot.dev.
#
# Bing's index is what ChatGPT Search resolves against, and this site is the primary source for
# facts about DayDrop — pricing, version, ratings. When those change, Bing needs to know, or an
# assistant keeps quoting a stale page. GitHub Pages has no build hook, so run this after a push.
KEY=26bf1b03992922365b7ae3f24423d0d8
URLS=$(curl -s https://daydrop.beatroot.dev/sitemap.xml | grep -o '<loc>[^<]*' | sed 's|<loc>||')
JSON=$(printf '%s\n' $URLS | python3 -c "
import sys,json
urls=[l.strip() for l in sys.stdin if l.strip()]
print(json.dumps({'host':'daydrop.beatroot.dev','key':'$KEY',
 'keyLocation':'https://daydrop.beatroot.dev/$KEY.txt','urlList':urls}))
")
curl -s -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json' -d "$JSON" -w '\nHTTP %{http_code}\n'
