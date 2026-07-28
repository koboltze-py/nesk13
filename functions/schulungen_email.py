"""
Schulungen – E-Mail-Funktionen
Erstellt Outlook-Entwürfe für abgelaufene/ablaufende Schulungen:
  1) E-Mail an den Mitarbeiter – inkl. Info-Block zur ZÜP (Zuverlässigkeitsüberprüfung)
  2) separate E-Mail an Herrn Peters – informiert über die Benachrichtigung
"""
from __future__ import annotations

import os
import sys
import urllib.parse
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import HANDYS_EMAIL_EMPFAENGER as _PETERS_EMAIL
from functions.handys_email import _outlook_mail_oeffnen, _absender_name

# ─── ZÜP-Unterlagen (identisch zum Laufzettel-Abschnitt "ZÜP") ───────────────
ZUEP_UNTERLAGEN = [
    "Ausweiskopie (Personalausweis oder Reisepass, beidseitig)",
    "Wohnortmeldebescheinigungen / Nachweise der Wohnorte der letzten 10 Jahre",
    "Nachweise aller Arbeitgeber der letzten 5 Jahre (Arbeitszeugnisse, Arbeitsverträge)",
    "Letzte Lohnabrechnung (als Tätigkeitsnachweis)",
    "Sonstige Nachweise (z. B. Ausbildungsnachweise, Zeugnisse)",
]

ANTRAGSARTEN = ["Neuantrag", "Verlaengerung"]


def _mitarbeiter_email(nachname: str, vorname: str) -> str:
    """Sucht die E-Mail-Adresse eines Mitarbeiters in mitarbeiter.db."""
    try:
        from database.connection import get_ma_connection
        import sqlite3
        conn = get_ma_connection()
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT email FROM mitarbeiter WHERE nachname=? AND vorname=? LIMIT 1",
            (nachname, vorname),
        ).fetchone()
        conn.close()
        if row:
            return row["email"] or ""
    except Exception:
        pass
    return ""


def _employee_email_text(vorname: str, schulungen: list[tuple[str, str]],
                          antragsart: str | None, absender: str,
                          fehlende_dokumente: list[str] | None = None) -> str:
    linie = "─" * 42
    schulungen_liste = "\n".join(f"  • {anzeige}: gültig bis {gb}" for anzeige, gb in schulungen)
    mehrzahl = len(schulungen) > 1

    dok_block = ""
    if fehlende_dokumente:
        dok_mehrzahl = len(fehlende_dokumente) > 1
        dok_liste = "\n".join(f"  • {d}" for d in fehlende_dokumente)
        dok_block = (
            f"Außerdem liegen uns von dir noch folgende Dokument"
            f"{'e' if dok_mehrzahl else ''} nicht vor:\n\n"
            f"{dok_liste}\n\n"
            f"Bitte reiche auch diese{'e' if not dok_mehrzahl else ''} zeitnah nach.\n\n"
        )

    zuep_block = ""
    if antragsart is not None:
        zuep_liste = "\n".join(f"  • {u}" for u in ZUEP_UNTERLAGEN)
        antrag_txt = "Neuantrag" if antragsart == "Neuantrag" else "Verlängerung"
        verlaengerung_hinweis = ""
        if antragsart != "Neuantrag":
            verlaengerung_hinweis = (
                "\nHinweis: Da es sich um eine Verlängerung handelt, sind nicht zwingend "
                "alle oben genannten Unterlagen notwendig. Bitte sprich dich hierzu kurz "
                "mit Herrn Peters ab, welche Unterlagen in deinem Fall tatsächlich "
                "benötigt werden.\n"
            )
        zuep_block = (
            f"Zusätzlich benötigen wir im Rahmen der Zuverlässigkeitsüberprüfung (ZÜP) "
            f"– {antrag_txt} – folgende Unterlagen von dir:\n\n"
            f"{zuep_liste}\n"
            f"{verlaengerung_hinweis}\n"
            f"Bitte reiche die Unterlagen zeitnah bei Herrn Peters oder deinem "
            f"Schichtleiter ein.\n\n"
        )

    return (
        f"Hallo {vorname},\n\n"
        f"im Rahmen der Schulungsübersicht wurde festgestellt, dass folgende "
        f"Schulung{'en' if mehrzahl else ''}/Berechtigung{'en' if mehrzahl else ''} "
        f"abgelaufen {'sind' if mehrzahl else 'ist'} bzw. in Kürze "
        f"{'ablaufen' if mehrzahl else 'abläuft'}:\n\n"
        f"{schulungen_liste}\n\n"
        f"Bitte kümmere dich zeitnah um die Erneuerung.\n\n"
        f"{dok_block}"
        f"{zuep_block}"
        f"Bei Fragen stehen wir gerne zur Verfügung.\n\n"
        f"Viele Grüße\n"
        f"{absender}\n"
        f"DRK Erste-Hilfe-Station Flughafen Köln/Bonn\n\n"
        f"{linie}\n"
        f"Deutsches Rotes Kreuz\n"
        f"Kreisverband Köln e.V.\n"
        f"Erste-Hilfe-Station Flughafen Köln/Bonn\n"
        f"Terminal 2 | 51147 Köln\n"
        f"E-Mail: erste-hilfe-station-flughafen@drk-koeln.de\n"
        f"{linie}"
    )


def _peters_email_text(ma_name: str, schulungen: list[tuple[str, str]],
                        antragsart: str | None, informiert_am: str, absender: str,
                        fehlende_dokumente: list[str] | None = None) -> str:
    linie = "─" * 42
    mehrzahl = len(schulungen) > 1
    schulungen_liste = "\n".join(f"  • {anzeige}: gültig bis {gb}" for anzeige, gb in schulungen)

    dok_block = ""
    if fehlende_dokumente:
        dok_liste = "\n".join(f"  • {d}" for d in fehlende_dokumente)
        dok_block = (
            f"Außerdem fehlen von {ma_name} noch folgende Dokument"
            f"{'e' if len(fehlende_dokumente) > 1 else ''}:\n\n"
            f"{dok_liste}\n\n"
        )

    if antragsart is not None:
        zuep_satz = (
            f"Es handelt sich hierbei um "
            f"{'einen Neuantrag' if antragsart == 'Neuantrag' else 'eine Verlängerung'} "
            f"im Rahmen der ZÜP. {ma_name} wurde gebeten, die erforderlichen "
            f"Unterlagen einzureichen.\n\n"
        )
    else:
        zuep_satz = f"{ma_name} wurde gebeten, sich zeitnah um die Erneuerung zu kümmern.\n\n"
    return (
        f"Sehr geehrter Herr Peters,\n\n"
        f"{ma_name} wurde am {informiert_am} darüber informiert, dass folgende "
        f"Schulung{'en' if mehrzahl else ''}/Berechtigung{'en' if mehrzahl else ''} "
        f"abgelaufen {'sind' if mehrzahl else 'ist'} bzw. in Kürze "
        f"{'ablaufen' if mehrzahl else 'abläuft'}:\n\n"
        f"{schulungen_liste}\n\n"
        f"{zuep_satz}"
        f"{dok_block}"
        f"Bitte um Kenntnisnahme und weitere Veranlassung.\n\n"
        f"Mit freundlichen Grüßen\n\n"
        f"{absender}\n"
        f"Schichtleiter | DRK Kreisverband Köln e.V.\n"
        f"Erste-Hilfe-Station Flughafen Köln/Bonn\n\n"
        f"{linie}\n"
        f"Deutsches Rotes Kreuz\n"
        f"Kreisverband Köln e.V.\n"
        f"Erste-Hilfe-Station Flughafen Köln/Bonn\n"
        f"Terminal 2 | 51147 Köln\n"
        f"E-Mail: erste-hilfe-station-flughafen@drk-koeln.de\n"
        f"{linie}"
    )


def _mail_oeffnen_mit_fallback(an: str, betreff: str, text: str) -> None:
    """Versucht Outlook via pywin32, sonst mailto-Fallback."""
    try:
        _outlook_mail_oeffnen(an, betreff, text)
        return
    except ImportError:
        pass
    mailto = (
        f"mailto:{urllib.parse.quote(an)}"
        f"?subject={urllib.parse.quote(betreff)}"
        f"&body={urllib.parse.quote(text)}"
    )
    subprocess.Popen(["cmd", "/c", "start", "", mailto], shell=False)


def sende_schulung_ablauf_email(
    ma: dict,
    schulungen: list[dict],
    antragsart: str | None,
    informiert_am: str | None = None,
    absender_name: str | None = None,
    ma_email_override: str | None = None,
    fehlende_dokumente: list[str] | None = None,
) -> tuple[bool, str]:
    """
    Erstellt zwei Outlook-Entwürfe für eine oder mehrere abgelaufene/ablaufende
    Schulungen eines Mitarbeiters:
      1) An den Mitarbeiter (inkl. ZÜP-Unterlagen-Info, falls antragsart gesetzt)
      2) An Herrn Peters (separate Benachrichtigung)

    schulungen: Liste von Dicts mit mind. "schulungstyp" + "gueltig_bis"
                (optional "_anzeige" für den Anzeigenamen).
    antragsart: "Neuantrag" oder "Verlaengerung" – nur relevant, wenn eine
                ZÜP-Schulung ausgewählt wurde. None, wenn keine ZÜP betroffen
                ist (dann entfällt der ZÜP-Unterlagen-Block in der E-Mail).
    ma_email_override: falls gesetzt, wird diese Adresse statt der in der
                Mitarbeiter-Datenbank hinterlegten E-Mail verwendet (z. B.
                wenn dort keine Adresse gepflegt ist).
    fehlende_dokumente: Liste von Dokumentnamen, die dem Mitarbeiter noch
                fehlen – wird in beiden E-Mails erwähnt, falls vorhanden.
    Rückgabe: (erfolg: bool, meldung: str)
    """
    from functions.schulungen_db import SCHULUNGSTYPEN_CFG

    if absender_name is None:
        absender_name = _absender_name()

    vorname  = ma.get("vorname", "")
    nachname = ma.get("nachname", "")
    name     = f"{vorname} {nachname}".strip()

    schulungen_liste: list[tuple[str, str]] = []
    for s in schulungen:
        anzeige = s.get("_anzeige") or SCHULUNGSTYPEN_CFG.get(
            s.get("schulungstyp", ""), {}
        ).get("anzeige", s.get("schulungstyp", ""))
        gb = s.get("gueltig_bis") or "—"
        schulungen_liste.append((anzeige, gb))

    if not schulungen_liste:
        return False, "Es wurde keine Schulung zur Benachrichtigung ausgewählt."

    informiert_am = informiert_am or datetime.now().strftime("%d.%m.%Y")

    email_ma = ma_email_override or _mitarbeiter_email(nachname, vorname)
    if not email_ma:
        return False, (
            f"Für {name} ist keine E-Mail-Adresse in der Mitarbeiter-Datenbank "
            f"hinterlegt. E-Mail konnte nicht erstellt werden."
        )

    mehrzahl = len(schulungen_liste) > 1
    betreff_kurz = (
        f"{len(schulungen_liste)} abgelaufene Schulungen" if mehrzahl
        else f"Abgelaufene Schulung: {schulungen_liste[0][0]}"
    )
    betreff_ma = f"{betreff_kurz} – bitte Unterlagen einreichen"
    text_ma = _employee_email_text(
        vorname, schulungen_liste, antragsart, absender_name, fehlende_dokumente
    )

    betreff_peters = (
        f"Schulungsablauf ({len(schulungen_liste)} Schulungen) – {name} informiert"
        if mehrzahl else
        f"Schulungsablauf {schulungen_liste[0][0]} – {name} informiert"
    )
    text_peters = _peters_email_text(
        name, schulungen_liste, antragsart, informiert_am, absender_name, fehlende_dokumente
    )

    fehler = []
    try:
        _mail_oeffnen_mit_fallback(email_ma, betreff_ma, text_ma)
    except Exception as e:
        fehler.append(f"Mitarbeiter-Mail konnte nicht erstellt werden: {e}")

    try:
        _mail_oeffnen_mit_fallback(_PETERS_EMAIL, betreff_peters, text_peters)
    except Exception as e:
        fehler.append(f"Peters-Mail konnte nicht erstellt werden: {e}")

    if fehler:
        return False, "\n".join(fehler)
    return True, (
        f"Zwei E-Mail-Entwürfe erstellt ({len(schulungen_liste)} Schulung"
        f"{'en' if mehrzahl else ''}):\n"
        f"  • Mitarbeiter: {email_ma}\n"
        f"  • Herr Peters: {_PETERS_EMAIL}"
    )
