#!/bin/bash
set -e
cd /root/x402bench
git rm -q --cached run.log smoke.json push.sh r_deepseek-r1-distill-qwen-32b.json r_deepseek-v4-pro-0813.json r_deepseekv4pro0813.json r_glm-4_7-flash.json r_gpt-oss-120b.json r_gptoss120.json r_gptoss120b.json r_granite-4_0-h-micro.json r_kimi-k2_6.json r_kimik26.json r_llama-3_1-8b-instruct-fp8.json r_llama-3_2-3b-instruct.json r_llama-3_3-70b-instruct-fp8-fast.json r_llama-4-scout-17b-16e-instruct.json r_mistral-small-3_1-24b-instruct.json r_qwen3_8-27b.json 2>/dev/null || true
rm -f run.log smoke.json push.sh r_*.json
printf 'r_*.json\nrun.log\nsmoke.json\npush.sh\n__pycache__/\n' > .gitignore
git add -A
git commit -q -m "clean repo: keep spec, harness, README, aggregated results.json"
git push -q origin main
echo CLEAN_OK
