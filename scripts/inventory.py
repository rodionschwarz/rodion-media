#!/usr/bin/env python3
"""
Portfolio Steward — INVENTURA (fáze 0, jen čtení)

Stáhne z Trading 212 API stav účtu, portfolio a pies a zapíše:
  - data/inventory_<datum>.json   (surová data, verzovaná)
  - reports/INVENTORY.md          (lidsky čitelný report)

Zásady (viz PORTFOLIO_BRAIN.md §7):
  - klíče jen z prostředí (GitHub Secrets), nikdy se nevypisují
  - hlasité selhání: co se nepodařilo přečíst, je SLEPOTA nahoře v reportu
  - jen standardní knihovna
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

BASE = "https://live.trading212.com/api/v0"
PAUSE_S = 3  # šetrnost k rate limitům API


def auth_header() -> str:
    key = os.environ.get("T212_API_KEY", "").strip()
    secret = os.environ.get("T212_API_SECRET", "").strip()
    if not key or not secret:
        print("CHYBA: chybí T212_API_KEY nebo T212_API_SECRET v prostředí.")
        sys.exit(1)
    token = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return f"Basic {token}"


def get(path: str, auth: str):
    """Vrátí (data, None) nebo (None, 'popis chyby bez tajemství')."""
    req = urllib.request.Request(BASE + path, headers={"Authorization": auth})
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(10 * attempt)  # rate limit: počkat a zkusit znovu
                continue
            return None, f"HTTP {e.code} na {path}"
        except Exception as e:  # síť, timeout, JSON — bez detailů s tajemstvími
            return None, f"{type(e).__name__} na {path}"
    return None, f"opakovaný rate limit na {path}"


def main() -> int:
    auth = auth_header()
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    blind = []  # seznam slepot — vždy nahoře v reportu
    data = {"collected_at": now}

    steps = [
        ("account_info", "/equity/account/info"),
        ("account_cash", "/equity/account/cash"),
        ("portfolio", "/equity/portfolio"),
        ("pies", "/equity/pies"),
    ]
    for name, path in steps:
        result, err = get(path, auth)
        if err:
            blind.append(f"{name}: {err}")
        else:
            data[name] = result
        time.sleep(PAUSE_S)

    # detail každé pie (jen pokud seznam pies dorazil)
    data["pie_details"] = []
    for pie in data.get("pies") or []:
        pid = pie.get("id")
        detail, err = get(f"/equity/pies/{pid}", auth)
        if err:
            blind.append(f"pie {pid}: {err}")
        else:
            data["pie_details"].append(detail)
        time.sleep(PAUSE_S)

    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    with open(f"data/inventory_{today}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ---------- report ----------
    lines = [f"# INVENTURA PORTFOLIA — {today}", ""]
    lines += ["## K vaší pozornosti", ""]
    if blind:
        lines += ["**SLEPOTA — tyto části systém NEVIDÍ (ne 0, ale nevidí):**", ""]
        lines += [f"- {b}" for b in blind]
    else:
        lines += ["- Všechny čtecí endpointy odpověděly. Slepota: žádná."]
    lines += ["", f"*Sběr dat: {now}*", ""]

    cash = data.get("account_cash") or {}
    if cash:
        lines += ["## Účet", ""]
        for k in ("total", "invested", "free", "ppl", "result"):
            if k in cash:
                lines.append(f"- {k}: {cash[k]}")
        lines.append("")

    positions = data.get("portfolio") or []
    if positions:
        lines += [f"## Pozice ({len(positions)})", ""]
        lines += ["| Ticker | Kusů | Prům. cena | Akt. cena | Zisk/ztráta |",
                  "|---|---|---|---|---|"]
        def ppl(p):
            return p.get("ppl") if isinstance(p.get("ppl"), (int, float)) else 0
        for p in sorted(positions, key=ppl):
            lines.append(
                f"| {p.get('ticker','?')} | {p.get('quantity','?')} "
                f"| {p.get('averagePrice','?')} | {p.get('currentPrice','?')} "
                f"| {p.get('ppl','?')} |"
            )
        lines += ["", "*Ceny a P/L jsou v měně instrumentu (většinou USD);",
                  "účet je veden v CZK — kurzové riziko viz brain §8.*", ""]

    for pie in data.get("pie_details") or []:
        s = pie.get("settings") or {}
        st = (pie.get("status") or "").upper()
        lines += [f"## Pie: {s.get('name', '?')}", ""]
        if st and st != "AHEAD":
            lines.append(f"- POZOR status: {st}")
        instruments = pie.get("instruments") or []
        lines.append(f"- pozic: {len(instruments)}")
        issues = [i for i in instruments if (i.get("issues") or [])]
        if issues:
            lines.append("- POZOR instrumenty s problémem: "
                         + ", ".join(i.get("ticker", "?") for i in issues))
        lines.append("")

    with open("reports/INVENTORY.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Hotovo. Slepých míst: {len(blind)}. "
          f"Pozic: {len(positions)}. Pies: {len(data.get('pie_details') or [])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
