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


def _employee_email_text(vorname: str, schulung_anzeige: str, gueltig_bis: str,
                          antragsart: str, absender: str) -> str:
    linie = "─" * 42
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
    return (
        f"Hallo {vorname},\n\n"
        f"im Rahmen der Schulungsübersicht wurde festgestellt, dass folgende Schulung/"
        f"Berechtigung abgelaufen ist bzw. in Kürze abläuft:\n\n"
        f"  • {schulung_anzeige}: gültig bis {gueltig_bis}\n\n"
        f"Bitte kümmere dich zeitnah um die Erneuerung.\n\n"
        f"Zusätzlich benötigen wir im Rahmen der Zuverlässigkeitsüberprüfung (ZÜP) "
        f"– {antrag_txt} – folgende Unterlagen von dir:\n\n"
        f"{zuep_liste}\n"
        f"{verlaengerung_hinweis}\n"
        f"Bitte reiche die Unterlagen zeitnah bei Herrn Peters oder deinem "
        f"Schichtleiter ein.\n\n"
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


def _peters_email_text(ma_name: str, schulung_anzeige: str, gueltig_bis: str,
                        antragsart: str, informiert_am: str, absender: str) -> str:
    linie = "─" * 42
    antrag_txt = "Neuantrag" if antragsart == "Neuantrag" else "Verlängerung"
    return (
        f"Sehr geehrter Herr Peters,\n\n"
        f"{ma_name} wurde am {informiert_am} darüber informiert, dass folgende Schulung/"
        f"Berechtigung abgelaufen ist bzw. in Kürze abläuft:\n\n"
        f"  • {schulung_anzeige}: gültig bis {gueltig_bis}\n\n"
        f"Es handelt sich hierbei um einen {antrag_txt} im Rahmen der ZÜP. "
        f"{ma_name} wurde gebeten, die erforderlichen Unterlagen einzureichen.\n\n"
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
    schulungstyp_key: str,
    eintrag: dict,
    antragsart: str,
    informiert_am: str | None = None,
    absender_name: str | None = None,
) -> tuple[bool, str]:
    """
    Erstellt zwei Outlook-Entwürfe für eine abgelaufene/ablaufende Schulung:
      1) An den Mitarbeiter (inkl. ZÜP-Unterlagen-Info)
      2) An Herrn Peters (separate Benachrichtigung)

    antragsart: "Neuantrag" oder "Verlaengerung"
    Rückgabe: (erfolg: bool, meldung: str)
    """
    from functions.schulungen_db import SCHULUNGSTYPEN_CFG

    if absender_name is None:
        absender_name = _absender_name()

    vorname  = ma.get("vorname", "")
    nachname = ma.get("nachname", "")
    name     = f"{vorname} {nachname}".strip()
    anzeige  = SCHULUNGSTYPEN_CFG.get(schulungstyp_key, {}).get("anzeige", schulungstyp_key)
    gueltig_bis = eintrag.get("gueltig_bis", "") or "—"
    informiert_am = informiert_am or datetime.now().strftime("%d.%m.%Y")

    email_ma = _mitarbeiter_email(nachname, vorname)
    if not email_ma:
        return False, (
            f"Für {name} ist keine E-Mail-Adresse in der Mitarbeiter-Datenbank "
            f"hinterlegt. E-Mail konnte nicht erstellt werden."
        )

    betreff_ma = f"Abgelaufene Schulung: {anzeige} – bitte Unterlagen einreichen"
    text_ma = _employee_email_text(vorname, anzeige, gueltig_bis, antragsart, absender_name)

    betreff_peters = f"Schulungsablauf {anzeige} – {name} informiert"
    text_peters = _peters_email_text(name, anzeige, gueltig_bis, antragsart, informiert_am, absender_name)

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
        f"Zwei E-Mail-Entwürfe erstellt:\n"
        f"  • Mitarbeiter: {email_ma}\n"
        f"  • Herr Peters: {_PETERS_EMAIL}"
    )
