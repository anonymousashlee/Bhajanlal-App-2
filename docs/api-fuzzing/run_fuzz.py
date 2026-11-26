#!/usr/bin/env python3
"""Run Nuclei-style templates against the Bhajanlal backend (api-fuzzing-nuclei apply)."""
import os, yaml, itertools, json, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(BASE, "nuclei-templates")
TARGET = os.environ.get("BHAIJAN_TARGET", "http://127.0.0.1:8790")

def load_templates():
    out=[]
    for fn in sorted(os.listdir(TPL)):
        if fn.endswith(".yaml") or fn.endswith(".yml"):
            with open(os.path.join(TPL,fn)) as f:
                d=yaml.safe_load(f)
            if isinstance(d,dict) and "http" in d:
                out.append((fn,d))
    return out

def render_path(t, combos):
    # t may contain {{BaseURL}} and {{var}}
    s=t.replace("{{BaseURL}}", TARGET)
    for k,v in combos.items():
        s=s.replace("{{"+k+"}}", str(v))
    return s

def render_body(t, combos):
    s=t
    for k,v in combos.items():
        s=s.replace("{{"+k+"}}", str(v) if not isinstance(v,(dict,list)) else json.dumps(v))
    return s

def combinations(tpl_http):
    payloads = tpl_http.get("payloads") or {}
    keys = list(payloads.keys())
    vals = [payloads[k] for k in keys]
    attack = tpl_http.get("attack", "clusterbomb")
    if not keys:
        yield {}
        return
    if attack == "pitchfork":
        n = min(len(v) for v in vals)
        for i in range(n):
            yield {keys[j]: vals[j][i] for j in range(len(keys))}
    elif attack == "battering-ram":
        n = max(len(v) for v in vals)
        for i in range(n):
            yield {keys[j]: vals[j][i % len(vals[j])] for j in range(len(keys))}
    else:  # clusterbomb
        for prod in itertools.product(*vals):
            yield {keys[j]: prod[j] for j in range(len(keys))}

def match(resp_status, resp_text, http):
    matchers = http.get("matchers") or []
    mc = http.get("matchers-condition", "or")
    results = []
    for m in matchers:
        mtype = m.get("type")
        ok = False
        if mtype == "status":
            ok = resp_status in (m.get("status") or [])
        elif mtype == "word":
            words = m.get("words") or []
            cond = m.get("condition", "or")
            hits = [w in resp_text for w in words]
            ok = any(hits) if cond == "or" else all(hits)
        results.append(ok)
    if not results:
        return False
    return any(results) if mc == "or" else all(results)

def do_request(method, url, headers, body):
    data = body.encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    for k,v in (headers or {}).items():
        req.add_header(k,v)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return 0, str(e)

def main():
    templates = load_templates()
    filt = os.environ.get("FUZZ_FILTER", "")
    if filt:
        templates = [(fn,t) for fn,t in templates if filt.lower() in (t.get("id","")+fn).lower()]
    skip = os.environ.get("FUZZ_SKIP", "")
    if skip:
        for s in skip.split(","):
            templates = [(fn,t) for fn,t in templates if s.lower() not in (t.get("id","")+fn).lower()]
    findings = []
    total = 0
    for fn, tpl in templates:
        for http in tpl.get("http", []):
            method = http.get("method", "GET")
            paths = http.get("path", [])
            headers = http.get("headers")
            body_tmpl = http.get("body")
            for path_tmpl in paths:
                for combo in combinations(http):
                    url = render_path(path_tmpl, combo)
                    body = render_body(body_tmpl, combo) if body_tmpl else None
                    status, text = do_request(method, url, headers, body)
                    total += 1
                    if match(status, text, http):
                        findings.append({
                            "template": tpl["id"],
                            "method": method,
                            "url": url,
                            "status": status,
                            "combo": combo,
                            "snippet": text[:300],
                        })
    print(f"Ran {total} requests across {len(templates)} templates.")
    print(f"Findings: {len(findings)}")
    for f in findings:
        print("---")
        print(f['template'], f['method'], f['status'])
        print(f['url'])
        print("combo:", f['combo'])
        print("snippet:", f['snippet'].replace("\n"," ")[:200])
    # write report
    report_path = os.path.join(BASE, "fuzz-report.json")
    with open(report_path,"w") as fh:
        json.dump({"target":TARGET,"total":total,"findings":findings}, fh, indent=2)
    print("Report written:", report_path)

if __name__ == "__main__":
    main()
