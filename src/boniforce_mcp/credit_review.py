"""Deterministic, source-linked presentation data; never a new credit score."""
from __future__ import annotations

from datetime import date, datetime, timezone
import math
from typing import Any


METRICS = {
    "jahresueberschuss": ("Jahresergebnis", "Ertragskraft"),
    "eigenkapital": ("Eigenkapital", "Kapitalbasis"),
    "verbindlichkeiten": ("Verbindlichkeiten", "Finanzierung"),
    "umlaufvermoegen": ("Umlaufvermögen", "Liquidität"),
    "bilanzsumme": ("Bilanzsumme", "Bilanzstruktur"),
    "forderungen": ("Forderungen", "Kapitalbindung"),
    "liquide_mittel": ("Liquide Mittel", "Liquidität"),
}
DETAIL_PATHS = {
    "jahresueberschuss": ("passiva", "eigenkapital_details", "jahresueberschuss"),
    "eigenkapital": ("passiva", "eigenkapital"),
    "verbindlichkeiten": ("passiva", "verbindlichkeiten"),
    "umlaufvermoegen": ("aktiva", "umlaufvermoegen"),
    "bilanzsumme": ("aktiva", "bilanzsumme"),
    "forderungen": ("aktiva", "umlaufvermoegen_details", "forderungen"),
    "liquide_mittel": ("aktiva", "umlaufvermoegen_details", "kassenbestand_kreditinstitut"),
}
DIMENSIONS = {
    "financial_health": "Finanzielle Stabilität", "market_dynamics": "Marktdynamik",
    "regulatory_climate": "Regulierung", "innovation_index": "Innovation",
    "labor_market": "Arbeitsmarkt", "external_risk": "Externe Risiken",
}


def obj(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def rows(value: Any) -> list[dict]:
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


def number(value: Any) -> float | int | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def at(value: Any, path: tuple[str, ...]) -> Any:
    for key in path:
        value = obj(value).get(key)
    return value


def fmt(value: float | int) -> str:
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def unit_label(currency: Any, unit: Any) -> str:
    return " · ".join(str(v) for v in (currency, unit) if v not in (None, "")) or "Einheit nicht geliefert"


def _year(row: dict) -> int | None:
    year = row.get("jahr", row.get("year"))
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    return year if type(year) is int and 1900 <= year <= 2200 else None


def financial_series(bundle: dict) -> tuple[list[dict], list[dict], list[str]]:
    data, analysis = obj(bundle.get("financial_data")), obj(bundle.get("financial_analysis"))
    by_year: dict[int, dict] = {}
    ratios, issues = [], []
    # Primary financial data wins; analysis only fills missing financial fields.
    for layer, response, key in (("financial_data", data, "financials"), ("financial_data", data, "financial_reports"), ("financial_analysis", analysis, "financials")):
        seen: set[int] = set()
        for index, row in enumerate(rows(response.get(key))):
            year = _year(row)
            if year is None:
                issues.append(f"{layer}.{key}[{index}]: Geschäftsjahr fehlt oder ist ungültig.")
                continue
            target = by_year.setdefault(year, {"values": {}, "conflicts": set()})
            source = f"{layer}.{key}[{index}]"
            duplicate = year in seen
            if duplicate:
                issues.append(f"{source}: Mehrere Datensätze für {year}; widersprüchliche Werte werden nicht verglichen.")
            seen.add(year)
            detailed = key == "financial_reports"
            # Summary currency may only be inherited from a matching filing if unambiguous.
            filings = [r for r in rows(data.get("financial_reports")) if _year(r) == year]
            filing_units = {(str(r.get("currency") or ""), str(r.get("unit") or "")) for r in filings}
            inherited = next(iter(filing_units)) if len(filing_units) == 1 else ("", "")
            currency = row.get("currency") or response.get("currency") or inherited[0] or None
            unit = row.get("unit") or response.get("unit") or inherited[1] or None
            for metric in METRICS:
                value = number(at(row, DETAIL_PATHS[metric]) if detailed else row.get(metric))
                metric_path = ".".join(DETAIL_PATHS[metric]) if detailed else metric
                # A reported deficit is negative profit, never a positive surplus.
                if value is None and detailed and metric == "jahresueberschuss":
                    value = number(at(row, ("guv", "jahresueberschuss")))
                    metric_path = "guv.jahresueberschuss"
                    if value is None:
                        deficit = number(at(row, ("passiva", "eigenkapital_details", "jahresfehlbetrag")))
                        metric_path = "passiva.eigenkapital_details.jahresfehlbetrag"
                        if deficit is None:
                            deficit = number(at(row, ("guv", "jahresfehlbetrag")))
                            metric_path = "guv.jahresfehlbetrag"
                        value = -abs(deficit) if deficit is not None else None
                if value is None:
                    continue
                point = {"period": str(year), "value": value, "currency": currency, "unit": unit,
                         "source": f"{source}.{metric_path}"}
                previous = target["values"].get(metric)
                incompatible = previous and (
                    previous["value"] != value
                    or (previous["currency"] and currency and previous["currency"] != currency)
                    or (previous["unit"] and unit and previous["unit"] != unit)
                )
                if incompatible:
                    target["conflicts"].add(metric)
                    issues.append(f"{year} · {METRICS[metric][0]}: Abweichende Quellwerte; aus Diagramm und Trendanalyse ausgeschlossen.")
                elif not previous:
                    target["values"][metric] = point
                else:
                    previous["currency"] = previous["currency"] or currency
                    previous["unit"] = previous["unit"] or unit
            for ratio in rows(row.get("ratios")):
                if ratio.get("name"):
                    ratios.append({"year": year, "name": str(ratio["name"]), "value": number(ratio.get("value")),
                                   "score": number(ratio.get("score")), "unit": ratio.get("unit"), "source": source + ".ratios"})
    series = []
    for metric, (label, area) in METRICS.items():
        groups: dict[tuple, list] = {}
        for year, row in sorted(by_year.items()):
            point = row["values"].get(metric)
            if point and metric not in row["conflicts"]:
                groups.setdefault((point["currency"], point["unit"]), []).append(point)
        for (currency, unit), points in groups.items():
            series.append({"key": metric, "label": label, "area": area, "unit": unit_label(currency, unit),
                           "comparable": bool(currency or unit), "points": points})
    # Ratios derived only from components from the same year and same unit.
    equity_points = []
    for year, row in sorted(by_year.items()):
        equity, assets = (row["values"].get(k) for k in ("eigenkapital", "bilanzsumme"))
        if equity and assets and assets["value"] > 0 and not ({"eigenkapital", "bilanzsumme"} & row["conflicts"]):
            if (equity["currency"], equity["unit"]) == (assets["currency"], assets["unit"]) and (equity["currency"] or equity["unit"]):
                equity_points.append({"period": str(year), "value": 100 * equity["value"] / assets["value"],
                                      "source": f"{equity['source']} / {assets['source']} × 100", "derived": True})
    if equity_points:
        series.append({"key": "equity_ratio", "label": "Eigenkapitalquote", "area": "Kapitalbasis",
                       "unit": "%", "comparable": True, "points": equity_points})
    return series, sorted(ratios, key=lambda r: (r["year"], r["name"])), list(dict.fromkeys(issues))


def history_series(payload: Any, field: str, label: str, unit: str, source: str) -> tuple[dict, list[str]]:
    points, issues = {}, []
    duplicates = set()
    for index, row in enumerate(rows(obj(payload).get("points"))):
        period, value = row.get("reference_period"), number(row.get(field))
        try:
            date.fromisoformat(str(period))
        except ValueError:
            issues.append(f"{source}.points[{index}]: Gültiger Bezugszeitraum fehlt.")
            continue
        if period in points:
            duplicates.add(period)
        points[period] = {"period": period, "value": value, "source": f"{source}.points[{index}].{field}"}
    for period in duplicates:
        points[period]["value"] = None
        issues.append(f"{source}: Mehrere Werte für {period}; Trend an dieser Stelle nicht ausgewertet.")
    return {"key": field, "label": label, "unit": unit, "comparable": True,
            "points": [p for _, p in sorted(points.items())]}, issues


def build_credit_review(bundle: dict, *, today: date | None = None) -> dict:
    """Keep full source data in the bundle; add conservative, explainable findings."""
    today = today or datetime.now(timezone.utc).date()
    report, company, sector = (obj(bundle.get(k)) for k in ("report", "company_details", "sector"))
    current, match = obj(sector.get("current")), obj(bundle.get("sector_match"))
    series, ratios, issues = financial_series(bundle)
    score_history, score_issues = history_series(sector.get("history"), "composite_score", "Branchenentwicklung", "Punkte / 100", "sector.history")
    insolvencies, insolvency_issues = history_series(sector.get("insolvency_history"), "total_cases", "Insolvenzfälle", "Fälle", "sector.insolvency_history")
    issues += score_issues + insolvency_issues
    findings = []

    def add(area, title, evidence, interpretation, monitor, sources, kind="observation"):
        findings.append({"area": area, "title": title, "evidence": evidence, "interpretation": interpretation,
                         "monitor": monitor, "sources": sources, "kind": kind})

    decision = report.get("credit_assessment_result")
    add("Kreditentscheidung", "Boniforce-Empfehlung", f"{decision or 'Nicht geliefert'} · Boniscore: {report.get('score') if report.get('score') is not None else 'nicht geliefert'}",
        "Die Originalempfehlung bleibt unverändert. Brancheninformationen liefern zusätzlichen Kontext, keinen neuen Kreditscore.",
        "Vor einer Freigabe offene Befunde und Aktualität prüfen.", ["report.credit_assessment_result", "report.score", "report.credit_limit"], "source")
    interpretations = {
        "jahresueberschuss": ("Die Ertragskraft hat sich im beobachteten Zeitraum verbessert.", "Der Ergebnisrückgang verringert den finanziellen Spielraum.", "Nächsten Abschluss und laufende Ergebnisentwicklung prüfen."),
        "eigenkapital": ("Die absolute Kapitalbasis ist gestiegen.", "Die absolute Kapitalbasis ist gesunken.", "Eigenkapitalentwicklung und mögliche Ausschüttungen im nächsten Abschluss prüfen."),
        "verbindlichkeiten": ("Die ausgewiesenen Verbindlichkeiten sind gestiegen; Laufzeiten und Bedienbarkeit gesondert prüfen.", "Die ausgewiesenen Verbindlichkeiten sind gesunken; Ursachen aus dem Abschluss prüfen.", "Fälligkeiten und Zinsbelastung anhand aktueller Unterlagen prüfen."),
        "umlaufvermoegen": ("Das kurzfristig gebundene Vermögen ist gestiegen; daraus folgt keine gesicherte Zahlungsfähigkeit.", "Das Umlaufvermögen ist gesunken; die Zusammensetzung ist für die Bewertung entscheidend.", "Forderungen, Vorräte und verfügbare Zahlungsmittel getrennt prüfen."),
        "bilanzsumme": ("Die Bilanz ist gewachsen; Wachstum allein belegt keine höhere Bonität.", "Die Bilanzsumme ist gesunken; Ursache und Strukturveränderungen prüfen.", "Bilanzstruktur beim nächsten Abschluss vergleichen."),
        "forderungen": ("Mehr Kapital ist in Forderungen gebunden; die Einbringlichkeit ist nicht belegt.", "Der Forderungsbestand ist gesunken; daraus lässt sich kein Umsatztrend ableiten.", "Aktuelle Fälligkeitsliste und überfällige Kundenforderungen prüfen."),
        "liquide_mittel": ("Der ausgewiesene Zahlungsmittelbestand ist gestiegen.", "Der ausgewiesene Zahlungsmittelbestand ist gesunken.", "Aktuelle Liquiditätsplanung und kurzfristige Zahlungsverpflichtungen gegenüberstellen."),
        "equity_ratio": ("Der Eigenkapitalanteil an der Bilanzsumme ist gestiegen.", "Der Eigenkapitalanteil an der Bilanzsumme ist gesunken.", "Quote im nächsten Abschluss erneut berechnen; keine branchenübergreifende Mindestquote unterstellen."),
    }
    for s in series:
        pts = s["points"]
        if not pts:
            continue
        first, last = pts[-2] if len(pts) >= 2 else pts[0], pts[-1]
        values = f"{last['period']}: {fmt(last['value'])} {s['unit']}"
        if len(pts) >= 2 and s["comparable"]:
            delta = last["value"] - first["value"]
            delta_unit = "Prozentpunkte" if s["unit"] == "%" else s["unit"]
            values = f"{first['period']}: {fmt(first['value'])} → {last['period']}: {fmt(last['value'])} {s['unit']} · Δ {fmt(delta)} {delta_unit}"
            interpretation = interpretations[s["key"]][0 if delta > 0 else 1] if delta else "Keine Veränderung zwischen den ausgewiesenen Vergleichsjahren."
        else:
            interpretation = "Kein belastbarer Zeitvergleich: weniger als zwei vergleichbare Jahreswerte oder unbestätigte Einheit."
        kind = "observation"
        if s["key"] in {"jahresueberschuss", "eigenkapital"} and last["value"] < 0:
            kind = "attention"
            interpretation += " Der letzte ausgewiesene Wert ist negativ und bedarf einer gesonderten Prüfung."
        add(s["area"], s["label"], values, interpretation, interpretations[s["key"]][2], [p["source"] for p in (first, last)], kind)
    valid_score = [p for p in score_history["points"] if p["value"] is not None]
    valid_cases = [p for p in insolvencies["points"] if p["value"] is not None]
    for s, pts, area, interpretation in ((score_history, valid_score, "Branche", "Die Veränderung beschreibt die Branche, nicht die individuelle Ausfallwahrscheinlichkeit."),
                                        (insolvencies, valid_cases, "Branche", "Fallzahlen sind keine Insolvenzquote. Unternehmensbestand und Saisonalität sind hier nicht berücksichtigt.")):
        if len(pts) >= 2:
            a, b = pts[0], pts[-1]
            add(area, s["label"], f"{a['period']}: {fmt(a['value'])} → {b['period']}: {fmt(b['value'])} {s['unit']} · Δ {fmt(b['value']-a['value'])}",
                interpretation, "Bei der nächsten monatlichen Branchenaktualisierung erneut vergleichen.", [a["source"], b["source"]])
    dims = [{"key": k, "label": DIMENSIONS.get(k, k), "value": number(v)} for k, v in obj(current.get("dimensions")).items() if number(v) is not None]
    if dims:
        weakest = min(dims, key=lambda d: d["value"])
        add("Branche", "Schwächste gelieferte Branchendimension", f"{weakest['label']}: {fmt(weakest['value'])} / 100",
            "Dies ist die relativ niedrigste Dimension innerhalb dieses Branchenprofils. Eine konkrete Betroffenheit des Unternehmens ist damit nicht bewiesen.",
            "Exposition des Unternehmens gegenüber diesem Faktor prüfen.", [f"sector.current.dimensions.{weakest['key']}"])
    if ratios:
        add("Kennzahlen", "Gelieferte Kennzahlenanalyse", f"{len(ratios)} Kennzahlenwerte aus {len({r['year'] for r in ratios})} Geschäftsjahren.",
            "Werte und Quellscores werden unverändert gezeigt. Ohne gelieferte Definition oder Einheit wird keine eigene Schwelle oder Interpretation des Scores unterstellt.",
            "Definition, Berechnungsbasis und Einheit auffälliger Kennzahlen anhand des Originalabschlusses prüfen.", ["financial_analysis.financials[].ratios"], "source")
    assessments = rows(report.get("assessments"))
    if assessments:
        add("Prüfkriterien", "Boniforce-Einzelbewertungen", f"{len(assessments)} gelieferte Einzelbewertungen: " + ", ".join(str(a.get("type", "ohne Bezeichnung")) for a in assessments),
            "Die Kriterien und ihre Detailbegründungen sind im Prüfbericht einzeln einsehbar. Numerische Codes werden ohne dokumentierte Bedeutung nicht als Risiko eingestuft.",
            "Negative oder unklare Begründungen im vollständigen Quellbericht einzeln klären.", ["report.assessments"], "source")
    risk = current.get("risk_level")
    relationship = "Gemischte oder unzureichende Evidenz"
    if match.get("status") in {"verified", "inferred"} and decision in {"APPROVE", "REVIEW", "DECLINE"}:
        if risk in {"Weak", "Critical"}:
            relationship = "Positive Unternehmenseinschätzung bei Branchengegenwind" if decision == "APPROVE" else "Unternehmens- und Branchenrisiken treffen zusammen"
        elif risk in {"Excellent", "Good"}:
            relationship = "Positive Unternehmens- und Brancheneinschätzung" if decision == "APPROVE" else "Prüfbedarf beim Unternehmen trotz positiver Branche"
    years = sorted({int(p["period"]) for s in series for p in s["points"]})
    if years and today.year - years[-1] > 2:
        issues.append(f"Letztes geliefertes Geschäftsjahr: {years[-1]}. Aktuelle wirtschaftliche Entwicklungen sind nicht durch diese Abschlüsse abgedeckt.")
    for label, raw_date in (("Boniforce-Bericht", report.get("created_at")), ("Branchenprofil", current.get("fetched_at"))):
        try:
            age = (today - date.fromisoformat(str(raw_date)[:10])).days
            if age < 0:
                issues.append(f"{label}: Das gelieferte Datum liegt in der Zukunft; Aktualität prüfen.")
                relationship = "Gemischte oder unzureichende Evidenz"
            elif age > 60:
                issues.append(f"{label}: Datenstand ist {age} Tage alt (Prüfhinweis ab 60 Tagen); vor einer Entscheidung aktualisieren.")
                relationship = "Gemischte oder veraltete Evidenz"
        except ValueError:
            if (label == "Boniforce-Bericht" and report) or (label == "Branchenprofil" and current):
                issues.append(f"{label}: Kein auswertbares Quelldatum geliefert.")
    if not series:
        issues.append("Keine auswertbaren Jahreszahlen geliefert; Finanzentwicklung und Kapitalstruktur sind nicht beurteilbar.")
    if any(not s["comparable"] for s in series):
        issues.append("Für einige Finanzwerte fehlt die bestätigte Währung/Einheit. Keine Umrechnung oder Trendbewertung dieser Reihen.")
    for key in ("report", "financial_data", "financial_analysis", "company_details"):
        if key in obj(bundle.get("errors")):
            issues.append(f"Datenquelle {key} ist nicht verfügbar.")
    if match.get("status") not in {"verified", "inferred"}:
        issues.append("Keine belastbare Branchenzuordnung vorhanden; kein Unternehmens-Branchenvergleich möglich.")
    elif match.get("status") == "inferred":
        issues.append("Branchenzuordnung ist abgeleitet und muss bestätigt werden.")
    for key in ("current", "history", "insolvency_history", "news"):
        if not sector.get(key):
            issues.append(f"Branchenquelle {key} nicht enthalten; daraus keine Entwarnung ableiten.")
    if sector.get("news") and not rows(obj(sector["news"]).get("citations")):
        issues.append("Die gelieferte Branchennachrichtenanalyse enthält keine Quellenlinks; Aussagen sind hier nicht unabhängig belegt.")
    coverage = [{"key": k, "label": label, "available": bool(bundle.get(k)), "date": obj(bundle.get(k)).get("created_at")} for k, label in
                (("report", "Boniforce-Bericht"), ("company_details", "Unternehmensdaten"), ("financial_data", "Jahresabschlüsse"), ("financial_analysis", "Kennzahlenanalyse"))]
    coverage += [{"key": f"sector.{k}", "label": label, "available": bool(sector.get(k)), "date": obj(sector.get(k)).get("fetched_at", obj(sector.get(k)).get("published_at"))} for k, label in
                 (("current", "Branchenprofil"), ("history", "Branchenverlauf"), ("insolvency_history", "Insolvenzverlauf"), ("news", "Branchennachrichten"))]
    return {"schema_version": 1, "generated_on": today.isoformat(),
            "company_name": company.get("name") or obj(report.get("company")).get("name") or "Unternehmensanalyse",
            "financial_series": series, "ratios": ratios,
            "sector_series": [score_history, insolvencies], "dimensions": dims,
            "relationship": {"label": relationship, "basis": "Boniforce-Assessment und SectorBench-Risikoklasse; keine Verrechnung der Scores.",
                             "sources": ["report.credit_assessment_result", "sector.current.risk_level", "sector_match"]},
            "findings": findings, "limitations": list(dict.fromkeys(issues)), "coverage": coverage,
            "scope": "Automatische, datenbasierte Plausibilitätsanalyse. Keine Abschlussprüfung oder Bestätigung der Vollständigkeit externer Quellen."}
