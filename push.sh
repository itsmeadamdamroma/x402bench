#!/bin/bash
set -e
cd /root/x402bench
rm -rf .git
git init -b main -q
git add -A
git commit -q -m "x402bench v0.1: 10-task deterministic eval, harness for OpenAI-compatible endpoints, initial 11-model leaderboard"
git remote add origin https://github.com/itsmeadamdamroma/x402bench.git
git push -q -u origin main
echo PUSH_OK
