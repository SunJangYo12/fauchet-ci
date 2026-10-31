DATA=$@

cat << EOF > btcFaucet.json
{
  "initData": "$DATA",
  "base_url": "https://btc.zrbtdoma.com"
}
EOF

