"""Build the pre-lock companion, with no network access or .git writes.

Run: python3 studio/episodes/scramble-luck/companion/build.py
The independent claim verifier did not read results.json, and therefore did
not record its hash. This binding freezes the current results and verified
claims together; every displayed measurement is also checked against that
verifier's independently recomputed values. Never refresh these pins merely
to make a changed analysis build. Re-verify and review a new binding first.
"""
import base64
import hashlib
import html
import json
import math
import re
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
ROOT = EP.parents[2]
VERIFIED_RESULTS = "4cb552244944cc0194bd750c7ea088030129285491996de91a48869ba5deb334"
VERIFIED_CLAIMS = "a2eb17f7cbbd27e0916b065b43106f4053cb931744e5ca6eb67bbf9abc7f933e"
VERIFICATION_REPORT = "7cdff71041e750892443d53e0c5d45cebc0fa77203a6059afc7f428b87ef9da7"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def flatten(item, prefix=""):
    out = {prefix: item}
    if isinstance(item, dict):
        for k, v in item.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(item, list):
        for k, v in enumerate(item):
            out.update(flatten(v, f"{prefix}[{k}]"))
    return out


def esc(value):
    return html.escape(str(value), quote=True)


def commit(revision):
    # Read-only Git operations; never stage, commit or update repository state.
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", revision + "^{commit}"],
                          check=True, text=True, capture_output=True).stdout.strip()


def fonts():
    source = ROOT / "studio/render/fonts"
    css = []
    for family, weights in (("BigShouldersDisplay", [700]), ("IBMPlexMono", [400, 500, 600]),
                            ("SourceSerif4", [400])):
        face = {"BigShouldersDisplay": "Big Shoulders Display", "IBMPlexMono": "IBM Plex Mono",
                "SourceSerif4": "Source Serif 4"}[family]
        for weight in weights:
            data = base64.b64encode((source / f"{family}-normal-{weight}-latin.woff2").read_bytes()).decode()
            css.append(f"@font-face{{font-family:'{face}';font-style:normal;font-weight:{weight};"
                       f"font-display:swap;src:url(data:font/woff2;base64,{data}) format('woff2')}}")
    for filename, face, weight in (("BigShouldersDisplay-800.ttf", "Big Shoulders Display", 800),
                                   ("BigShouldersDisplay-900.ttf", "Big Shoulders Display", 900),
                                   ("SourceSerif4-500.ttf", "Source Serif 4", 500)):
        data = base64.b64encode((EP / "companion/fonts" / filename).read_bytes()).decode()
        css.append(f"@font-face{{font-family:'{face}';font-style:normal;font-weight:{weight};"
                   f"font-display:swap;src:url(data:font/ttf;base64,{data}) format('truetype')}}")
    # Preserve the locally supplied font licences inside both self-contained outputs.
    for name in ("BigShouldersDisplay", "IBMPlexMono", "SourceSerif4"):
        css.append("/* " + (source / f"OFL-{name}.txt").read_text().replace("*/", "* /") + " */")
    return "\n".join(css)


def main():
    raw = (EP / "analysis/results.json").read_bytes()
    claim_raw = (EP / "CLAIMS.json").read_bytes()
    report_raw = (EP / "analysis/claims_check.json").read_bytes()
    for name, content, expected in (("results.json", raw, VERIFIED_RESULTS),
                                    ("CLAIMS.json", claim_raw, VERIFIED_CLAIMS),
                                    ("claims_check.json", report_raw, VERIFICATION_REPORT)):
        if sha(content) != expected:
            raise SystemExit(f"REFUSED: {name} differs from the verified companion binding; re-verify and review first.")
    results, ledger, report = json.loads(raw), json.loads(claim_raw), json.loads(report_raw)
    if not report["all_passed"] or report["claims_sha256"] != sha(claim_raw):
        raise SystemExit("REFUSED: independent claims verification is not current and passing.")
    claims = {c["id"]: c for c in ledger["claims"]}
    flat = flatten(results)
    proof = {}
    for c in report["claims"]:
        for v in c.get("values", []):
            if v.get("key") in flat and v.get("passed") and "recomputed" in v:
                proof.setdefault(v["key"], []).append((c["id"], v))
    provenance = {}

    def number(key):
        actual = flat[key]
        candidates = proof.get(key, [])
        passing = []
        for cid, v in candidates:
            value = v["recomputed"]
            if isinstance(actual, (float, int)) and isinstance(value, (float, int)):
                digits = v.get("digits")
                same = (round(actual, digits) == round(value, digits)) if digits is not None else actual == value
            else:
                same = actual == value
            if same:
                passing.append(cid)
        if not passing or not isinstance(actual, (int, float)) or not math.isfinite(actual):
            raise SystemExit(f"REFUSED: no matching independent numeric verification for {key}")
        provenance[key] = sorted(set(passing))
        return actual

    def measurement(path):
        return {"estimate": number(path + ".estimate"),
                "interval": [number(path + ".interval_95[0]"), number(path + ".interval_95[1]")],
                "path": path, "interval_method": flat[path]["interval_method"]}

    primary = measurement("primary.R_geometric_person_year")
    threshold = number("verdict.threshold")
    n = number("coverage.census_measurements.available_extrema.estimate")
    variants = []

    def variant(key, label, change, path, kind="R"):
        if path not in flat:
            return
        variants.append({"id": key, "label": label + " · cannot change verdict", "change": change,
                         "kind": kind, "rows": [measurement(path)]})

    variant("registered", "Registered estimate", "Equal weight per available person-year; geometric ratio. The amended reselecting interval is the only decision interval.", "primary.R_geometric_person_year")
    variant("arithmetic", "Arithmetic-mean R", "Changes aggregation to the mean of adjusted/observed ratios; extreme corrections receive more influence. Descriptive pointwise sensitivity, not a newly validated decision procedure.", "aggregation_and_tier_sensitivities.arithmetic_mean_R")
    variant("solver", "Per-solver R", "Averages log adjustments within each solver, then gives every solver equal weight. Descriptive pointwise sensitivity; no new confirmatory verdict.", "aggregation_and_tier_sensitivities.per_solver_weighted_R")
    tier_n = number("aggregation_and_tier_sensitivities.equal_tier_R.n.person_years")
    attrition = number("aggregation_and_tier_sensitivities.equal_tier_attrition.estimate")
    variant("tier", "Equal-tier R", f"Balances fast and slow peers on the supported subset: {tier_n:,} person-years; {attrition:,} original extrema omitted. Compare with the all-peer estimate on exactly that subset. Descriptive pointwise sensitivity; it cannot establish an advantage uniform across skill tiers.", "aggregation_and_tier_sensitivities.equal_tier_R")
    variant("matched", "All-peer R on equal-tier subset", "Keeps the all-peer estimator but restricts it to the same supported extrema as equal-tier R. This separates peer weighting from subset attrition. Descriptive pointwise sensitivity.", "aggregation_and_tier_sensitivities.all_peer_R_on_equal_tier_subset")
    for path in results.get("robustness", {}):
        if path.startswith("era_"):
            label = path.removeprefix("era_").replace("_", "–")
            variant(path, f"Era {label}", "Restricts season-best outcomes to this era. All-peer R does not use the skill references that caused the blind era-variance discrepancies. Interval is a secondary pointwise sensitivity.", f"robustness.{path}.R_geometric_person_year")
    deletions = []
    for key in results.get("robustness", {}):
        if key.startswith("leave_year_"):
            row = measurement(f"robustness.{key}.R_geometric_person_year")
            row["label"] = "Omit " + key.split("_")[2]
            deletions.append(row)
    if deletions:
        variants.append({"id": "years", "label": "Leave-one-year-out range · cannot change verdict", "kind": "range",
                         "change": "Deletes one year and its reference information at a time, retaining the original roster. Each dot has its own pointwise interval. The span of dots is a point-estimate range, not a simultaneous confidence interval.", "rows": deletions})
    variant("fixed", "Fixed-selection interval", "Keeps the originally selected extrema fixed instead of reselecting the seasonal best in each draw. Procedure A is a percentile-interval sensitivity; its point estimate is unchanged.", "primary.R_fixed_selection_A_sensitivity")
    for key, block in results.get("replacement_sensitivity", {}).items():
        if not isinstance(block, dict) or "variance_share_with_original_D" not in block:
            continue
        variant(key, "Replacement p = " + key.removeprefix("p_"), "Assumes independent random replacement and scales shared variance with the original denominator. No replacement-adjusted R exists in these results: the registered R remains unchanged. This is neither a worst-case bound nor an audited assignment correction; targeted replacements can bias either way.", f"replacement_sensitivity.{key}.variance_share_with_original_D", "replacement")
        variants[-1]["replacement"] = variants[-1]["rows"][0]
        variants[-1]["rows"] = [primary]

    scope = claims["SL-C001"]["scope"]
    # The confidence level is stated in the verified claim, not typed into HTML.
    level = int(re.search(r"(\d+)% interval", claims["SL-C001"]["text"])[1])
    notice = results["source_notice"]
    method = (EP / "METHOD.md").read_text()
    if re.sub(r"\s+", " ", notice) not in re.sub(r"\s+", " ", method):
        raise SystemExit("REFUSED: results attribution differs from METHOD's verbatim notice.")
    recheck = json.loads((EP / "analysis/recheck_report.json").read_text())
    if not all(x.get("resolution", {}).get("matches") for x in recheck["comparisons"] if x["status"] == "mismatch"):
        raise SystemExit("REFUSED: an unexplained blind recheck discrepancy remains.")
    crosses = []
    for key, label in (("six_face_centered_correlation", "Best of all faces · within-final centered"),
                       ("white_yellow_centered_correlation", "White/yellow faces · within-final centered")):
        m = measurement("optimal_cross_mechanism." + key)
        crosses.append(f'<tr><th scope="row">{esc(label)}</th><td>{m["estimate"]:.4f}</td><td>{m["interval"][0]:.4f}–{m["interval"][1]:.4f}</td></tr>')
    changes = [commit(x) for x in ("8a474d3", "3eca079", "0eb88d1", "5496074", "e8880f3", "d0c8f9e", "4c3fd03")]
    # The same linear coordinates as draw() in the template, for no-JS readers.
    domain_max = threshold + (threshold - 1) * .08
    coord = lambda value: 32 + (value - 1) / (domain_max - 1) * 636
    lo, hi = map(coord, primary["interval"])
    point, line = coord(primary["estimate"]), coord(threshold)
    initial_marks = (f'<line class="neutral" x1="32" y1="108" x2="668" y2="108"/>'
                     f'<line class="reference" x1="{line}" y1="28" x2="{line}" y2="108"/>'
                     f'<text class="plot-label" x="668" y="20" text-anchor="end">Registered {threshold:.2f} line</text>'
                     f'<line class="interval" x1="{lo}" y1="62" x2="{hi}" y2="62"/>'
                     f'<line class="cap" x1="{lo}" y1="53" x2="{lo}" y2="71"/>'
                     f'<line class="cap" x1="{hi}" y1="53" x2="{hi}" y2="71"/>'
                     f'<circle class="dot" cx="{point}" cy="62" r="8"/>')
    for tick in (1, (1 + threshold) / 2, threshold):
        initial_marks += f'<text class="axis" x="{coord(tick)}" y="143" text-anchor="{"start" if tick == 1 else "middle"}">{tick:.2f}</text>'
    data = {"variants": variants, "primary": primary, "threshold": threshold, "level": level, "provenance": provenance,
            "results_sha256": sha(raw), "claims_sha256": sha(claim_raw), "verification_sha256": sha(report_raw)}
    status = "claims locked" if all(c["status"] == "locked" for c in ledger["claims"]) else "pre-lock draft: claims proposed"
    replacements = {
        "__FONTS__": fonts(), "__DATA__": json.dumps(data, ensure_ascii=False).replace("<", "\\u003c"),
        "__LEVEL__": str(level),
        "__STATUS__": status, "__SCOPE__": esc(scope), "__VERDICT__": esc(results["verdict"]["outcome"]),
        "__ANSWER__": esc(results["verdict"]["permitted_claim"]), "__R__": f'{primary["estimate"]:.4f}',
        "__CI__": "–".join(f"{v:.4f}" for v in primary["interval"]), "__PERCENT__": f'{(primary["estimate"]-1)*100:.2f}',
        "__N__": f"{n:,}", "__THRESHOLD__": f"{threshold:.2f}", "__LINE_PERCENT__": f"{(threshold-1)*100:g}",
        "__OPTIONS__": "".join(f'<option value="{esc(v["id"])}">{esc(v["label"])}</option>' for v in variants),
        "__CROSS_ROWS__": "".join(crosses), "__NOTICE__": esc(notice), "__HASH__": sha(raw),
        "__CLAIMS_HASH__": sha(claim_raw), "__INITIAL_CHANGE__": esc(variants[0]["change"]),
        "__INITIAL_MARKS__": initial_marks,
        "__CHRONOLOGY__": esc(results["confirmation_access_chronology"]["decisions_7_10_timing"]),
    }
    for name, value in zip(("METHOD", "GATE", "INVESTIGATION", "AMENDMENT", "RECHECK", "REVIEW", "FIXES"), changes):
        replacements[f"__{name}_COMMIT__"] = value
    template = (Path(__file__).parent / "template.html").read_text()
    for key, value in replacements.items():
        template = template.replace(key, value)
    # Evidence downloads travel with the standalone file and wrapper-free page.
    # They are source artifacts, not new page measurements or live dependencies.
    def embed_document(match):
        source = (EP / "companion" / match[1]).resolve()
        if not source.is_relative_to(EP):
            raise SystemExit("REFUSED: evidence download escapes the episode.")
        encoded = base64.b64encode(source.read_bytes()).decode()
        mime = "application/json" if source.suffix == ".json" else "text/plain"
        return f'href="data:{mime};base64,{encoded}" download="{source.name}"'
    template = re.sub(r'href="(\.\./[^"]+)"', embed_document, template)
    unresolved = re.findall(r"__[A-Z_]+__", template)
    if unresolved:
        raise SystemExit(f"Unfilled template tokens: {unresolved}")
    head, body = template.split("<!--BODY-->")
    document = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' + head + '</head>\n<body>\n' + body + '</body>\n</html>\n'
    target = EP / "renders/companion"
    target.mkdir(parents=True, exist_ok=True)
    (EP / "companion/index.html").write_text(document)
    (target / "page.html").write_text(head + body)
    print(f"Built standalone + fragment; {len(variants)} precomputed selections; results {sha(raw)[:12]}; {len(provenance)} independently verified numeric bindings.")


if __name__ == "__main__":
    main()
