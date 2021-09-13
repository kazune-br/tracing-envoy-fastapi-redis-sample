#!/usr/bin/env bash

id=${1:-a}
now_unix=$(date +%s)
data=$(cat << EOF
{
  "id": "${id}",
  "value": "$(jot -r 1 5 1000)",
  "timestamp": ${now_unix}
}
EOF
)
echo ${data} | jq -c .