#!/usr/bin/env python3
"""x402 Agent Commerce Bench — harness.

Runs benchmark tasks against any OpenAI-compatible chat endpoint (Cloudflare
Workers AI by default) and scores with deterministic checks.

Usage:
  python3 harness.py --model @cf/meta/llama-3.3-70b-instruct-fp8-fast
  python3 harness.py --model all          # every model in MODELS list
  python3 harness.py --endpoint URL --api-key KEY --model NAME
"""
import argparse, json, os, re, sys, time, urllib.request

ACCT = os.environ["CF_ACCOUNT_ID"]
TOK = os.environ["CF_API_TOKEN"]
BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/v1"

MODELS = [
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "@cf/openai/gpt-oss-120b",
    "@cf/deepseek-ai/deepseek-v4-pro-0813",
    "@cf/moonshotai/kimi-k2.6",
    "@cf/qwen/qwen3.8-27b",
    "@cf/meta/llama-4-scout-17b-16e-instruct",
    "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "@cf/zai-org/glm-4.7-flash",
    "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
    "@cf/meta/llama-3.1-8b-instruct-fp8",
    "@cf/ibm-granite/granite-4.0-h-micro",
    "@cf/meta/llama-3.2-3b-instruct",
]

def chat(model, user, max_tokens=200, retries=3):
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise assistant. Answer with ONLY what is asked — a single value, no explanation, no code fences."},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
                msg = d["choices"][0]["message"]
                content = msg.get("content") or msg.get("reasoning") or ""
                return content.strip() if content.strip() else f"__EMPTY__ {d['choices'][0].get('finish_reason')}"
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    return f"__ERROR__ {last}"

def grade(answer, check):
    if answer.startswith("__ERROR__"):
        return 0, answer
    # normalize: strip spaces, fences, backticks, trailing period, lowercase for letters
    a = answer.strip().strip("`").strip()
    m = re.search(r"exact:(.+)", check)
    want = m.group(1).strip()
    # case-sensitive compare for addresses (EIP-55), case-insensitive for single letters
    if len(want) == 1:
        ok = a.upper().startswith(want.upper())
    else:
        a_norm = a.replace(" ", "").replace(",", "").rstrip(".")
        if a_norm.lower() == want.lower():
            ok = True
        elif want.startswith("0x"):
            # addresses must match exactly (case-insensitive on hex is acceptable for grading)
            ok = a_norm.lower() == want.lower()
        elif want.isdigit() and a_norm.replace(".","").isdigit():
            # numeric compare: 1.5 != 1500000
            try:
                ok = abs(float(a_norm) - float(want)) < 1e-9
            except ValueError:
                ok = False
        else:
            ok = a_norm.lower() == want.lower()
    return (1 if ok else 0), a

TOKEN_BUDGET = {
    "@cf/openai/gpt-oss-120b": 700,
    "@cf/openai/gpt-oss-20b": 700,
}

def run_model(model, spec):
    results = []
    score = 0
    total = 0
    for task in spec["tasks"]:
        t0 = time.time()
        ans = chat(model, task["prompt"], max_tokens=TOKEN_BUDGET.get(model, 200))
        pts, norm = grade(ans, task["check"])
        score += pts
        total += task["points"]
        results.append({"id": task["id"], "answer": norm[:120], "pass": bool(pts), "secs": round(time.time()-t0, 1)})
        print(f"  {task['id']:<18} {'PASS' if pts else 'FAIL'}  {norm[:60]}")
    return {"model": model, "score": score, "total": total, "pct": round(100*score/total, 1), "results": results}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="all")
    ap.add_argument("--spec", default=os.path.join(os.path.dirname(__file__), "bench.json"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "results.json"))
    args = ap.parse_args()

    spec = json.load(open(args.spec))
    models = MODELS if args.model == "all" else [args.model]

    all_results = []
    for m in models:
        print(f"== {m}")
        try:
            res = run_model(m, spec)
        except Exception as e:
            print(f"  FAILED: {e}")
            continue
        all_results.append(res)
        print(f"  => {res['score']}/{res['total']} ({res['pct']}%)")

    json.dump({"bench": spec["benchmark"], "version": spec["version"], "run": time.strftime("%Y-%m-%d"), "results": all_results},
              open(args.out, "w"), indent=2)
    print(f"\nsaved {args.out}")

if __name__ == "__main__":
    main()
