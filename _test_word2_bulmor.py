# -*- coding: utf-8 -*-
"""
Testausgaben fuer Branch 'word2': Bulmor-Fahrzeugstatus nur noch als
Anzahl + farbiger Punkt (rot <2, orange <3, gruen >=3) statt 5 Einzelboxen.

Erzeugt je eine Test-Word-Datei fuer bulmor_aktiv = 0..5 im Zielordner.
"""
from datetime import datetime
from pathlib import Path

from functions.staerkemeldung_dashboard_export import StaerkemeldungDashboardExport

ZIEL = Path(
    r"C:\Users\DRKairport\OneDrive - Deutsches Rotes Kreuz - Kreisverband Köln e.V\Desktop\bei\word2"
)
ZIEL.mkdir(parents=True, exist_ok=True)

DATA = {
    "dispo": [
        {"vollname": "Kieckhoefel Patrick", "anzeigename": "Kieckhoefel Pa",
         "start_zeit": "07:00", "end_zeit": "19:00", "dienst_kategorie": "DT"},
        {"vollname": "Kieckhoefel Meike", "anzeigename": "Kieckhoefel Me",
         "start_zeit": "07:00", "end_zeit": "19:00", "dienst_kategorie": "DT"},
        {"vollname": "Macchitella Rosa", "anzeigename": "Macchitella",
         "start_zeit": "19:00", "end_zeit": "07:00", "dienst_kategorie": "DN"},
        {"vollname": "Issa Karim", "anzeigename": "Issa",
         "start_zeit": "19:00", "end_zeit": "07:00", "dienst_kategorie": "DN"},
    ],
    "betreuer": [
        {"vollname": "Rentschke Anna", "anzeigename": "Rentschke",
         "start_zeit": "06:00", "end_zeit": "16:00"},
        {"vollname": "Vogt Peter", "anzeigename": "Vogt",
         "start_zeit": "09:00", "end_zeit": "19:00"},
        {"vollname": "Schaefer Lena", "anzeigename": "Schaefer",
         "start_zeit": "10:30", "end_zeit": "20:00"},
        {"vollname": "Cremer Tim", "anzeigename": "Cremer",
         "start_zeit": "18:00", "end_zeit": "22:00"},
    ],
    "kranke": [],
}

VON = datetime(2026, 7, 25)
BIS = datetime(2026, 7, 26)

for aktiv in range(0, 6):
    ziel_datei = ZIEL / f"Staerkemeldung_test_bulmor_{aktiv}.docx"
    exp = StaerkemeldungDashboardExport(
        DATA, str(ziel_datei), VON, BIS,
        pax_zahl=346, einsaetze_zahl=5,
        bulmor_aktiv=aktiv,
        sl_tag_name="Kurthen", sl_nacht_name="Gross",
        stationsleitung="Mustermann",
    )
    pfad, warnungen = exp.export()
    print(f"bulmor_aktiv={aktiv} -> {pfad}" + (f" (Warnungen: {warnungen})" if warnungen else ""))

print("Fertig.")
