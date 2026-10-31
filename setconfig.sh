COOKIE=$@

cat << EOF > config.json
{
    "session_hash": "$COOKIE",
    "hash": "$COOKIE",
    "user_agent": "Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36"
}
EOF

