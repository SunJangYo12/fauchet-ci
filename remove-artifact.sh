
check_files=(
"42012312476"
"42004421784"
"42002919016"
"42001530992"
"42000594660"
)

for id in "${check_files[@]}"; do
	echo "[+] remove: $id"
	gh api -X DELETE repos/SunJangYo12/fauchet-ci/actions/runs/$id

done

