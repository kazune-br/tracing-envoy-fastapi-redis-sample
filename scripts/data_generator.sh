#!/usr/bin/env bash

id=${1:-a}
now_unix=$(date +%s)
data=()

for (( i = 60; i > 0; i-- )); do
  datum=$(cat << EOF
{
  "id": "${id}",
  "value": "$(jot -r 1 5 1000)",
  "timestamp": $(expr ${now_unix} - ${i})
}
EOF
)
  data=("${data[@]}" "$(echo ${datum} | jq -c .)");
done

echo "${data[@]}" | jq -cs ". | {values: .}"