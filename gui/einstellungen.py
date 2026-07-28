"""
Einstellungen-Widget
Anwendungseinstellungen verwalten (Ordner-Pfade etc.)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QMessageBox, QFileDialog, QGroupBox, QListWidget,
    QComboBox, QInputDialog, QAbstractItemView, QListWidgetItem, QSpinBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from config import FIORI_BLUE, FIORI_TEXT


class EinstellungenWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Titel ──────────────────────────────────────────────────────
        title = QLabel("⚙️ Einstellungen")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {FIORI_TEXT};")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #ddd;")
        layout.addWidget(sep)

        # ── Gruppe: Dienstplan-Ordner ───────────────────────────────────
        grp = QGroupBox("📂 Dienstplan-Ordner")
        grp.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_layout = QVBoxLayout(grp)
        grp_layout.setSpacing(8)

        beschreibung = QLabel(
            "Ordner, der im Dienstplan-Tab als Dateibaum angezeigt wird.\n"
            "Alle .xlsx / .xls Dateien in diesem Ordner können direkt geladen werden."
        )
        beschreibung.setWordWrap(True)
        beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_layout.addWidget(beschreibung)

        ordner_row = QHBoxLayout()
        self._ordner_edit = QLineEdit()
        self._ordner_edit.setPlaceholderText("Pfad zum Dienstplan-Ordner …")
        self._ordner_edit.setMinimumHeight(32)
        ordner_row.addWidget(self._ordner_edit, 1)

        browse_btn = QPushButton("📂 Durchsuchen")
        browse_btn.setMinimumHeight(32)
        browse_btn.setToolTip("Ordner für Dienstplan-Excel-Dateien auswählen")
        browse_btn.clicked.connect(self._browse_ordner)
        ordner_row.addWidget(browse_btn)

        grp_layout.addLayout(ordner_row)

        # Status-Anzeige für Pfad-Validierung
        self._pfad_status = QLabel("")
        self._pfad_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_layout.addWidget(self._pfad_status)

        self._ordner_edit.textChanged.connect(self._validate_path)

        layout.addWidget(grp)
        # ── Gruppe: Sonderaufgaben-Ordner ─────────────────────────────────
        grp_sa = QGroupBox("📝 Sonderaufgaben-Ordner")
        grp_sa.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_sa.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_sa_layout = QVBoxLayout(grp_sa)
        grp_sa_layout.setSpacing(8)

        sa_beschreibung = QLabel(
            "Ordner, der im Sonderaufgaben-Tab als Dateibaum angezeigt wird.\n"
            "Standardmäßig: 04_Tagesdienstpläne"
        )
        sa_beschreibung.setWordWrap(True)
        sa_beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_sa_layout.addWidget(sa_beschreibung)

        sa_row = QHBoxLayout()
        self._sa_ordner_edit = QLineEdit()
        self._sa_ordner_edit.setPlaceholderText("Pfad zum Sonderaufgaben-Ordner …")
        self._sa_ordner_edit.setMinimumHeight(32)
        sa_row.addWidget(self._sa_ordner_edit, 1)

        sa_browse_btn = QPushButton("📂 Durchsuchen")
        sa_browse_btn.setMinimumHeight(32)
        sa_browse_btn.setToolTip("Ordner für Sonderaufgaben-Dateien auswählen")
        sa_browse_btn.clicked.connect(self._browse_sa_ordner)
        sa_row.addWidget(sa_browse_btn)

        grp_sa_layout.addLayout(sa_row)

        self._sa_pfad_status = QLabel("")
        self._sa_pfad_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_sa_layout.addWidget(self._sa_pfad_status)

        self._sa_ordner_edit.textChanged.connect(self._validate_sa_path)

        layout.addWidget(grp_sa)

        # ── Gruppe: AOCC Lagebericht-Datei ─────────────────────────────
        grp_aocc = QGroupBox("📣 AOCC Lagebericht-Datei")
        grp_aocc.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_aocc.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_aocc_layout = QVBoxLayout(grp_aocc)
        grp_aocc_layout.setSpacing(8)

        aocc_beschreibung = QLabel(
            "Pfad zur AOCC Lagebericht Excel-Datei (.xlsm).\n"
            "Wird im Tab '!Aufgaben Nacht > AOCC Lagebericht' geöffnet."
        )
        aocc_beschreibung.setWordWrap(True)
        aocc_beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_aocc_layout.addWidget(aocc_beschreibung)

        aocc_row = QHBoxLayout()
        self._aocc_edit = QLineEdit()
        self._aocc_edit.setPlaceholderText("Pfad zur AOCC Lagebericht.xlsm …")
        self._aocc_edit.setMinimumHeight(32)
        aocc_row.addWidget(self._aocc_edit, 1)

        aocc_browse_btn = QPushButton("📂 Durchsuchen")
        aocc_browse_btn.setMinimumHeight(32)
        aocc_browse_btn.setToolTip("AOCC Lagebericht Excel-Datei (.xlsm) auswählen")
        aocc_browse_btn.clicked.connect(self._browse_aocc)
        aocc_row.addWidget(aocc_browse_btn)

        grp_aocc_layout.addLayout(aocc_row)

        self._aocc_status = QLabel("")
        self._aocc_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_aocc_layout.addWidget(self._aocc_status)

        self._aocc_edit.textChanged.connect(self._validate_aocc_path)

        layout.addWidget(grp_aocc)

        # ── Gruppe: Code 19 Datei ──────────────────────────────────────
        grp_c19 = QGroupBox("🚨 Code 19 Datei")
        grp_c19.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_c19.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_c19_layout = QVBoxLayout(grp_c19)
        grp_c19_layout.setSpacing(8)

        c19_beschreibung = QLabel(
            "Pfad zur Code-19-Excel-Datei (.xlsx).\n"
            "Wird im Tab '🚨 Code 19' geöffnet."
        )
        c19_beschreibung.setWordWrap(True)
        c19_beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_c19_layout.addWidget(c19_beschreibung)

        c19_row = QHBoxLayout()
        self._c19_edit = QLineEdit()
        self._c19_edit.setPlaceholderText("Pfad zur Code 19.xlsx …")
        self._c19_edit.setMinimumHeight(32)
        c19_row.addWidget(self._c19_edit, 1)

        c19_browse_btn = QPushButton("📂 Durchsuchen")
        c19_browse_btn.setMinimumHeight(32)
        c19_browse_btn.setToolTip("Code-19-Excel-Datei (.xlsx) auswählen")
        c19_browse_btn.clicked.connect(self._browse_c19)
        c19_row.addWidget(c19_browse_btn)

        grp_c19_layout.addLayout(c19_row)

        self._c19_status = QLabel("")
        self._c19_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_c19_layout.addWidget(self._c19_status)

        self._c19_edit.textChanged.connect(self._validate_c19_path)

        layout.addWidget(grp_c19)

        # ── Gruppe: E-Mobby Fahrer ───────────────────────────────
        grp_emobby = QGroupBox("🛥 E-Mobby Fahrer")
        grp_emobby.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_emobby.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_emobby_layout = QVBoxLayout(grp_emobby)
        grp_emobby_layout.setSpacing(8)

        emobby_desc = QLabel(
            "Namen der Mitarbeiter, die E-Mobby fahren dürfen.\n"
            "Beim Laden des Dienstplans werden diese automatisch erkannt und in der "
            "Übergabe-Ansicht unter Fahrzeuge als E-Mobby-Fahrer markiert. "
            "Nur Nachnamen eintragen – Groß-/Kleinschreibung wird ignoriert."
        )
        emobby_desc.setWordWrap(True)
        emobby_desc.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_emobby_layout.addWidget(emobby_desc)

        self._emobby_list = QListWidget()
        self._emobby_list.setFixedHeight(130)
        self._emobby_list.setStyleSheet(
            "border: 1px solid #c0c0c0; border-radius: 3px; "
            "font-size: 12px; background: white;"
        )
        grp_emobby_layout.addWidget(self._emobby_list)

        emobby_add_row = QHBoxLayout()
        self._emobby_input = QLineEdit()
        self._emobby_input.setPlaceholderText("Nachname eingeben …")
        self._emobby_input.setMinimumHeight(32)
        self._emobby_input.returnPressed.connect(self._add_emobby_entry)
        emobby_add_row.addWidget(self._emobby_input, 1)

        emobby_add_btn = QPushButton("+ Hinzufügen")
        emobby_add_btn.setMinimumHeight(32)
        emobby_add_btn.setToolTip("Eingegebenen Nachnamen zur E-Mobby-Fahrerliste hinzufügen")
        emobby_add_btn.setStyleSheet(
            f"background-color: #107e3e; color: white; border: none; "
            f"border-radius: 3px; padding: 4px 12px; font-weight: bold;"
        )
        emobby_add_btn.clicked.connect(self._add_emobby_entry)
        emobby_add_row.addWidget(emobby_add_btn)

        emobby_remove_btn = QPushButton("🗑 Entfernen")
        emobby_remove_btn.setMinimumHeight(32)
        emobby_remove_btn.setToolTip("Ausgewählten Eintrag aus der E-Mobby-Liste entfernen")
        emobby_remove_btn.setStyleSheet(
            "background-color: #e0e0e0; color: #555; border: none; "
            "border-radius: 3px; padding: 4px 12px;"
        )
        emobby_remove_btn.clicked.connect(self._remove_emobby_entry)
        emobby_add_row.addWidget(emobby_remove_btn)
        grp_emobby_layout.addLayout(emobby_add_row)

        self._emobby_count_lbl = QLabel("")
        self._emobby_count_lbl.setStyleSheet("color: #555; font-size: 10px;")
        grp_emobby_layout.addWidget(self._emobby_count_lbl)

        layout.addWidget(grp_emobby)

        # ── Protokoll-Verwaltung ───────────────────────────────────────
        grp_proto = QGroupBox("📋 Protokoll-Verwaltung")
        grp_proto.setStyleSheet(
            "QGroupBox { font-weight: bold; font-size: 12px; "
            "border: 2px solid #ddd; border-radius: 6px; margin-top: 10px; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }"
        )
        grp_proto_layout = QVBoxLayout(grp_proto)
        grp_proto_layout.setSpacing(8)

        # Filter-Zeile
        proto_filter_row = QHBoxLayout()
        self._proto_filter = QComboBox()
        self._proto_filter.addItems(["Alle Protokolle", "Tagdienst", "Nachtdienst"])
        self._proto_filter.setFixedWidth(180)
        proto_load_btn = QPushButton("🔄 Laden")
        proto_load_btn.setFixedWidth(90)
        proto_load_btn.setToolTip("Protokollliste nach gewähltem Filter neu laden")
        proto_load_btn.clicked.connect(self._load_protokoll_liste)
        proto_filter_row.addWidget(QLabel("Filter:"))
        proto_filter_row.addWidget(self._proto_filter)
        proto_filter_row.addWidget(proto_load_btn)
        proto_filter_row.addStretch()
        grp_proto_layout.addLayout(proto_filter_row)

        # List-Widget (Mehrfachauswahl)
        self._proto_list = QListWidget()
        self._proto_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._proto_list.setMinimumHeight(180)
        self._proto_list.setStyleSheet(
            "QListWidget { border: 1px solid #ccc; border-radius: 4px; font-size: 11px; }"
            "QListWidget::item:selected { background: #2980b9; color: white; }"
        )
        grp_proto_layout.addWidget(self._proto_list)

        # Aktions-Buttons
        proto_btn_row = QHBoxLayout()
        proto_del_btn = QPushButton("🗑 Löschen")
        proto_del_btn.setFixedHeight(34)
        proto_del_btn.setToolTip("Ausgewählte Protokolle dauerhaft löschen (Passwortschutz)")
        proto_del_btn.setStyleSheet(
            "QPushButton{background:#c0392b;color:white;border-radius:4px;font-weight:bold;}"
            "QPushButton:hover{background:#e74c3c;}"
        )
        proto_del_btn.clicked.connect(self._loeschen_protokolle_bulk)
        proto_arch_btn = QPushButton("📦 Archivieren")
        proto_arch_btn.setFixedHeight(34)
        proto_arch_btn.setToolTip("Ausgewählte Protokolle ins Archiv verschieben (Passwortschutz)")
        proto_arch_btn.setStyleSheet(
            "QPushButton:hover{background:#95a5a6;}"
        )
        proto_arch_btn.clicked.connect(self._archivieren_protokolle_bulk)
        proto_btn_row.addWidget(proto_del_btn)
        proto_btn_row.addWidget(proto_arch_btn)
        proto_btn_row.addStretch()
        grp_proto_layout.addLayout(proto_btn_row)

        hint_lbl = QLabel("ℹ️  Mehrfachauswahl mit Strg/Shift. Aktionen sind passwortgeschützt.")
        hint_lbl.setStyleSheet("color:#888;font-size:9px;")
        grp_proto_layout.addWidget(hint_lbl)

        layout.addWidget(grp_proto)

        # ── Archiv-Datenbank ─────────────────────────────────────
        grp_archiv = QGroupBox("📁 Archiv-Datenbank")
        grp_archiv.setStyleSheet(
            "QGroupBox { font-weight: bold; font-size: 12px; "
            "border: 2px solid #b8c8d8; border-radius: 6px; margin-top: 10px; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }"
        )
        grp_archiv_layout = QVBoxLayout(grp_archiv)
        grp_archiv_layout.setSpacing(8)

        # Pfad-Zeile
        arch_path_row = QHBoxLayout()
        self._archiv_path_edit = QLineEdit()
        from config import ARCHIV_DB_PATH as _ARCH_PATH
        self._archiv_path_edit.setText(_ARCH_PATH)
        self._archiv_path_edit.setStyleSheet(
            "border:1px solid #ccc;border-radius:3px;padding:3px 6px;font-size:10px;"
        )
        arch_browse_btn = QPushButton("📂 Durchsuchen")
        arch_browse_btn.setFixedWidth(110)
        arch_browse_btn.setFixedHeight(28)
        arch_browse_btn.setToolTip("Archiv-Datenbankdatei auswählen oder neu anlegen")
        arch_browse_btn.setStyleSheet(
            "QPushButton{background:#eef4fa;border:1px solid #b0c8e8;"
            "border-radius:4px;padding:2px 8px;color:#0a6ed1;font-size:11px;}"
            "QPushButton:hover{background:#d0e4f5;}"
        )
        arch_path_row.addWidget(QLabel("Archiv-Datei:"))
        arch_path_row.addWidget(self._archiv_path_edit, 1)
        arch_path_row.addWidget(arch_browse_btn)
        grp_archiv_layout.addLayout(arch_path_row)

        def _browse_archiv():
            p, _ = QFileDialog.getSaveFileName(
                self, "Archiv-Datenbankdatei wählen", self._archiv_path_edit.text(),
                "SQLite Datenbank (*.db);;Alle Dateien (*)"
            )
            if p:
                self._archiv_path_edit.setText(p)
        arch_browse_btn.clicked.connect(_browse_archiv)

        # Filter-Zeile
        archiv_filter_row = QHBoxLayout()
        self._archiv_filter = QComboBox()
        self._archiv_filter.addItems(["Alle Protokolle", "Tagdienst", "Nachtdienst"])
        self._archiv_filter.setFixedWidth(180)
        arch_load_btn = QPushButton("🔄 Archiv laden")
        arch_load_btn.setFixedWidth(110)
        arch_load_btn.setToolTip("Archivierte Protokolle nach gewähltem Filter anzeigen")
        arch_load_btn.clicked.connect(self._load_archiv_liste)
        archiv_filter_row.addWidget(QLabel("Filter:"))
        archiv_filter_row.addWidget(self._archiv_filter)
        archiv_filter_row.addWidget(arch_load_btn)
        archiv_filter_row.addStretch()
        grp_archiv_layout.addLayout(archiv_filter_row)

        # Archiv-List-Widget
        self._archiv_list = QListWidget()
        self._archiv_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._archiv_list.setMinimumHeight(160)
        self._archiv_list.setStyleSheet(
            "QListWidget { border: 1px solid #b8c8d8; border-radius: 4px; font-size: 11px; }"
            "QListWidget::item:selected { background: #1a6ea0; color: white; }"
        )
        grp_archiv_layout.addWidget(self._archiv_list)

        # Aktions-Buttons
        archiv_btn_row = QHBoxLayout()
        arch_detail_btn = QPushButton("🔍 Details")
        arch_detail_btn.setFixedHeight(34)
        arch_detail_btn.setToolTip("Inhalt des ausgewählten archivierten Protokolls anzeigen")
        arch_detail_btn.setStyleSheet(
            "QPushButton:hover{background:#3498db;}"
        )
        arch_detail_btn.clicked.connect(self._archiv_details_popup)
        arch_restore_btn = QPushButton("↩ Wiederherstellen")
        arch_restore_btn.setFixedHeight(34)
        arch_restore_btn.setToolTip("Ausgewählte Protokolle aus dem Archiv in die Hauptdatenbank zurückverschieben")
        arch_restore_btn.setStyleSheet(
            "QPushButton{background:#27ae60;color:white;border-radius:4px;font-weight:bold;}"
            "QPushButton:hover{background:#2ecc71;}"
        )
        arch_restore_btn.clicked.connect(self._wiederherstellen_aus_archiv)
        archiv_btn_row.addWidget(arch_detail_btn)
        archiv_btn_row.addWidget(arch_restore_btn)
        archiv_btn_row.addStretch()
        grp_archiv_layout.addLayout(archiv_btn_row)

        arch_hint = QLabel("ℹ️  Protokolle, die über ‘Archivieren’ entfernt wurden, landen hier.  Wiederherstellen = zurück in die Hauptdatenbank.")
        arch_hint.setStyleSheet("color:#888;font-size:9px;")
        arch_hint.setWordWrap(True)
        grp_archiv_layout.addWidget(arch_hint)

        layout.addWidget(grp_archiv)

        # ── Gruppe: Schulungen Excel-Stammdaten ────────────────────────
        grp_schulung = QGroupBox("📊 Schulungen – Excel-Stammdaten")
        grp_schulung.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_schulung.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_schulung_layout = QVBoxLayout(grp_schulung)
        grp_schulung_layout.setSpacing(8)

        schulung_hint = QLabel(
            "Pfad zur Excel-Datei mit Mitarbeiter-Stammdaten (Blatt \"laufend\").\n"
            "Beim ersten Programmstart wird die Datei automatisch in die Datenbank geladen."
        )
        schulung_hint.setWordWrap(True)
        schulung_hint.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_schulung_layout.addWidget(schulung_hint)

        schulung_row = QHBoxLayout()
        self._schulung_excel_edit = QLineEdit()
        self._schulung_excel_edit.setPlaceholderText("Pfad zur Stammdaten-Excel …")
        self._schulung_excel_edit.setMinimumHeight(32)
        schulung_row.addWidget(self._schulung_excel_edit, 1)

        schulung_browse_btn = QPushButton("📂 Durchsuchen")
        schulung_browse_btn.setMinimumHeight(32)
        schulung_browse_btn.clicked.connect(self._browse_schulungen_excel)
        schulung_row.addWidget(schulung_browse_btn)

        schulung_import_btn = QPushButton("📥 Jetzt importieren")
        schulung_import_btn.setMinimumHeight(32)
        schulung_import_btn.setStyleSheet(
            f"background-color: {FIORI_BLUE}; color: white; border-radius: 4px;"
        )
        schulung_import_btn.clicked.connect(self._schulungen_excel_importieren)
        schulung_row.addWidget(schulung_import_btn)

        grp_schulung_layout.addLayout(schulung_row)

        self._schulung_import_status = QLabel("")
        self._schulung_import_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_schulung_layout.addWidget(self._schulung_import_status)

        layout.addWidget(grp_schulung)

        # ── Gruppe: Bulmor-Fahrzeuge (Word-Export Dienstplan) ───────────
        grp_bulmor = QGroupBox("🚐 Bulmor-Fahrzeuge (Word-Export Dienstplan)")
        grp_bulmor.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_bulmor.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_bulmor_layout = QVBoxLayout(grp_bulmor)
        grp_bulmor_layout.setSpacing(8)

        bulmor_hint = QLabel(
            "Legt fest, wie viele Bulmor-Fahrzeuge insgesamt zur Verfügung stehen und "
            "ab welcher Anzahl aktiver Fahrzeuge die Ampel im Word-Export (Stärkemeldung) "
            "rot bzw. gelb angezeigt wird."
        )
        bulmor_hint.setWordWrap(True)
        bulmor_hint.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_bulmor_layout.addWidget(bulmor_hint)

        bulmor_form = QHBoxLayout()
        bulmor_form.addWidget(QLabel("Bulmor gesamt:"))
        self._bulmor_gesamt_spin = QSpinBox()
        self._bulmor_gesamt_spin.setRange(1, 50)
        self._bulmor_gesamt_spin.setValue(5)
        self._bulmor_gesamt_spin.setToolTip("Gesamtanzahl der Bulmor-Fahrzeuge")
        bulmor_form.addWidget(self._bulmor_gesamt_spin)

        bulmor_form.addSpacing(16)
        bulmor_form.addWidget(QLabel("Rot, wenn weniger als:"))
        self._bulmor_rot_spin = QSpinBox()
        self._bulmor_rot_spin.setRange(0, 50)
        self._bulmor_rot_spin.setValue(2)
        self._bulmor_rot_spin.setToolTip("Anzahl aktiver Bulmor, unter der die Ampel rot (kritisch) ist")
        bulmor_form.addWidget(self._bulmor_rot_spin)

        bulmor_form.addSpacing(16)
        bulmor_form.addWidget(QLabel("Gelb, wenn weniger als:"))
        self._bulmor_gelb_spin = QSpinBox()
        self._bulmor_gelb_spin.setRange(0, 50)
        self._bulmor_gelb_spin.setValue(3)
        self._bulmor_gelb_spin.setToolTip("Anzahl aktiver Bulmor, unter der die Ampel gelb (eingeschränkt) ist")
        bulmor_form.addWidget(self._bulmor_gelb_spin)
        bulmor_form.addStretch()

        grp_bulmor_layout.addLayout(bulmor_form)
        layout.addWidget(grp_bulmor)

        # ── Speichern-Button ───────────────────────────────────────────
        save_btn = QPushButton("💾 Einstellungen speichern")
        save_btn.setMinimumHeight(42)
        save_btn.setMaximumWidth(320)
        save_btn.setStyleSheet(
            f"background-color: {FIORI_BLUE}; color: white; font-size: 13px; "
            f"border-radius: 4px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

        layout.addStretch()

    # ------------------------------------------------------------------

    def _load_settings(self):
        try:
            from functions.settings_functions import get_setting, get_bulmor_gesamt, get_bulmor_schwellen
            self._ordner_edit.setText(get_setting('dienstplan_ordner'))
            self._sa_ordner_edit.setText(get_setting('sonderaufgaben_ordner'))
            self._aocc_edit.setText(get_setting('aocc_datei'))
            self._c19_edit.setText(get_setting('code19_datei'))
            self._schulung_excel_edit.setText(get_setting('schulungen_excel_pfad'))
            self._bulmor_gesamt_spin.setValue(get_bulmor_gesamt())
            rot, gelb = get_bulmor_schwellen()
            self._bulmor_rot_spin.setValue(rot)
            self._bulmor_gelb_spin.setValue(gelb)
        except Exception:
            pass
        # E-Mobby Liste laden
        self._load_emobby_list()

    def _validate_path(self, text: str):
        if not text.strip():
            self._pfad_status.setText("")
            return
        if os.path.isdir(text.strip()):
            self._pfad_status.setText("✅ Ordner gefunden")
            self._pfad_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._pfad_status.setText("⚠️ Ordner nicht gefunden")
            self._pfad_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_ordner(self):
        current = self._ordner_edit.text().strip()
        start = current if os.path.isdir(current) else os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(
            self, "Dienstplan-Ordner auswählen", start
        )
        if path:
            self._ordner_edit.setText(path)

    def _validate_sa_path(self, text: str):
        if not text.strip():
            self._sa_pfad_status.setText("")
            return
        if os.path.isdir(text.strip()):
            self._sa_pfad_status.setText("✅ Ordner gefunden")
            self._sa_pfad_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._sa_pfad_status.setText("⚠️ Ordner nicht gefunden")
            self._sa_pfad_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_sa_ordner(self):
        current = self._sa_ordner_edit.text().strip()
        start = current if os.path.isdir(current) else os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(
            self, "Sonderaufgaben-Ordner auswählen", start
        )
        if path:
            self._sa_ordner_edit.setText(path)

    def _validate_aocc_path(self, text: str):
        if not text.strip():
            self._aocc_status.setText("")
            return
        if os.path.isfile(text.strip()):
            self._aocc_status.setText("✅ Datei gefunden")
            self._aocc_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._aocc_status.setText("⚠️ Datei nicht gefunden")
            self._aocc_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_aocc(self):
        current = self._aocc_edit.text().strip()
        start_dir = os.path.dirname(current) if os.path.isfile(current) else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, "AOCC Lagebericht-Datei auswählen", start_dir,
            "Excel-Dateien (*.xlsx *.xlsm *.xls)"
        )
        if path:
            self._aocc_edit.setText(path)

    def _validate_c19_path(self, text: str):
        if not text.strip():
            self._c19_status.setText("")
            return
        if os.path.isfile(text.strip()):
            self._c19_status.setText("✅ Datei gefunden")
            self._c19_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._c19_status.setText("⚠️ Datei nicht gefunden")
            self._c19_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_c19(self):
        current = self._c19_edit.text().strip()
        start_dir = os.path.dirname(current) if os.path.isfile(current) else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, "Code-19-Datei auswählen", start_dir,
            "Excel-Dateien (*.xlsx *.xls)"
        )
        if path:
            self._c19_edit.setText(path)

    # ── E-Mobby Fahrer Verwaltung ────────────────────────────────

    def _load_emobby_list(self):
        try:
            from functions.emobby_functions import get_emobby_fahrer
            names = get_emobby_fahrer()
        except Exception:
            names = []
        self._emobby_list.clear()
        for n in names:
            self._emobby_list.addItem(n)
        self._emobby_count_lbl.setText(f"{len(names)} Fahrer in der Liste")

    def _add_emobby_entry(self):
        name = self._emobby_input.text().strip()
        if not name:
            return
        try:
            from functions.emobby_functions import add_emobby_fahrer
            added = add_emobby_fahrer(name)
            if added:
                self._emobby_input.clear()
                self._load_emobby_list()
            else:
                QMessageBox.information(self, "Bereits vorhanden",
                    f"'{name}' ist bereits in der Liste.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Hinzufügen:\n{e}")

    def _remove_emobby_entry(self):
        selected = self._emobby_list.currentItem()
        if not selected:
            QMessageBox.information(self, "Nichts ausgewählt",
                "Bitte zuerst einen Namen in der Liste auswählen.")
            return
        name = selected.text()
        antwort = QMessageBox.question(
            self, "Entfernen",
            f"'{name}' aus der E-Mobby-Liste entfernen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort != QMessageBox.StandardButton.Yes:
            return
        try:
            import json
            from functions.settings_functions import get_setting, set_setting
            db_raw = get_setting('emobby_fahrer', '')
            try:
                db_names = json.loads(db_raw) if db_raw else []
            except Exception:
                db_names = []
            if name in db_names:
                db_names.remove(name)
                set_setting('emobby_fahrer', json.dumps(db_names, ensure_ascii=False))
            self._load_emobby_list()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Entfernen:\n{e}")

    # ------------------------------------------------------------------
    # Protokoll-Verwaltung
    # ------------------------------------------------------------------

    def _load_protokoll_liste(self):
        """Lädt alle Protokolle (inkl. archivierte) in die Verwaltungs-Liste."""
        from functions.uebergabe_functions import lade_alle_protokolle_verwaltung
        self._proto_list.clear()
        filter_text = self._proto_filter.currentText()
        typ_map = {"Tagdienst": "Tag", "Nachtdienst": "Nacht"}
        typ_filter = typ_map.get(filter_text)      # None → alle
        try:
            protokolle = lade_alle_protokolle_verwaltung(typ_filter)
            for p in protokolle:
                pid    = p.get("id", "?")
                datum  = p.get("datum", "?")
                stype  = p.get("schicht_typ", "?")
                erst   = p.get("ersteller", "")
                status = p.get("status", "")
                arch   = p.get("archiviert", 0)
                icon   = "☀" if stype == "Tag" else "🌙"
                arch_tag = "  [archiviert]" if arch else ""
                text = f"#{pid}  {datum}  {icon} {stype}  {erst}  [{status}]{arch_tag}"
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, pid)
                self._proto_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Protokolle konnten nicht geladen werden:\n{e}")

    def _loeschen_protokolle_bulk(self):
        """Löscht ausgewählte Protokolle nach Passwortprüfung."""
        selected = self._proto_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "Hinweis", "Bitte mindestens ein Protokoll auswählen.")
            return
        pw, ok = QInputDialog.getText(
            self, "Passwort erforderlich",
            f"Passwort eingeben zum endgültigen Löschen\nvon {len(selected)} Protokoll(en):",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return
        if pw != "mettwurst":
            QMessageBox.warning(self, "Falsches Passwort", "Das eingegebene Passwort ist falsch.")
            return
        ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected]
        try:
            from functions.uebergabe_functions import loesche_protokolle_bulk
            count = loesche_protokolle_bulk(ids)
            QMessageBox.information(self, "Erledigt", f"✅ {count} Protokoll(e) wurden gelöscht.")
            self._load_protokoll_liste()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen:\n{e}")

    def _archivieren_protokolle_bulk(self):
        """Exportiert ausgewählte Protokolle in archiv.db und löscht sie aus der Haupt-DB."""
        selected = self._proto_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "Hinweis", "Bitte mindestens ein Protokoll auswählen.")
            return
        pw, ok = QInputDialog.getText(
            self, "Passwort erforderlich",
            f"Passwort eingeben zum Archivieren\nvon {len(selected)} Protokoll(en):",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return
        if pw != "mettwurst":
            QMessageBox.warning(self, "Falsches Passwort", "Das eingegebene Passwort ist falsch.")
            return
        ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected]
        archiv_path = getattr(self, "_archiv_path_edit", None)
        archiv_path = archiv_path.text().strip() if archiv_path else None
        try:
            from functions.archiv_functions import exportiere_in_archiv
            count = exportiere_in_archiv(ids, archiv_path or None)
            QMessageBox.information(
                self, "Erledigt",
                f"📦 {count} Protokoll(e) wurden in die Archiv-Datenbank exportiert"
                f"\nund aus der Hauptdatenbank entfernt."
            )
            self._load_protokoll_liste()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Archivieren:\n{e}")

    # ------------------------------------------------------------------
    # Archiv-Datenbank
    # ------------------------------------------------------------------

    def _load_archiv_liste(self):
        """Lädt Protokolle aus der Archiv-Datenbank in die Archiv-Liste."""
        from functions.archiv_functions import lade_archiv_protokolle
        self._archiv_list.clear()
        archiv_path = self._archiv_path_edit.text().strip() or None
        filter_text = self._archiv_filter.currentText()
        typ_map = {"Tagdienst": "tagdienst", "Nachtdienst": "nachtdienst"}
        typ_filter = typ_map.get(filter_text)
        try:
            protokolle = lade_archiv_protokolle(archiv_path, typ_filter)
            if not protokolle:
                self._archiv_list.addItem("(Keine archivierten Protokolle vorhanden)")
                return
            for p in protokolle:
                pid      = p.get("id", "?")
                orig_id  = p.get("orig_id", "")
                datum    = p.get("datum", "?")
                stype    = p.get("schicht_typ", "?")
                erst     = p.get("ersteller", "")
                status   = p.get("status", "")
                arch_am  = (p.get("archiviert_am") or "")[:10]
                icon     = "☀" if "tag" in stype else "🌙"
                label    = "Tagdienst" if "tag" in stype else "Nachtdienst"
                text = f"[Archiv#{pid}]  {datum}  {icon} {label}  {erst}  [{status}]  archiviert: {arch_am}"
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, pid)
                self._archiv_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Archiv konnte nicht geladen werden:\n{e}")

    def _archiv_details_popup(self):
        """Zeigt ein Detail-Popup für das ausgewählte Archiv-Protokoll."""
        selected = self._archiv_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "Hinweis", "Bitte ein Protokoll auswählen.")
            return
        item = selected[0]
        archiv_id = item.data(Qt.ItemDataRole.UserRole)
        if archiv_id is None:
            return
        from functions.archiv_functions import lade_archiv_protokoll_detail
        archiv_path = self._archiv_path_edit.text().strip() or None
        try:
            data = lade_archiv_protokoll_detail(archiv_id, archiv_path)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Details konnten nicht geladen werden:\n{e}")
            return

        p  = data.get("protokoll", {})
        fz = data.get("fahrzeuge", [])
        hs = data.get("handys", [])

        stype = p.get("schicht_typ", "?")
        icon  = "☀ Tagdienst" if "tag" in stype else "🌙 Nachtdienst"
        lines: list[str] = [
            f"Archiv-Protokoll #{p.get('id','?')}  (Original-ID: #{p.get('orig_id','?')})",
            "=" * 50,
            f"Art:         {icon}",
            f"Datum:       {p.get('datum','?')}",
            f"Schicht:     {p.get('beginn_zeit','?')} – {p.get('ende_zeit','?')}",
            f"Ersteller:   {p.get('ersteller','')}",
            f"Abzeichner:  {p.get('abzeichner','')}",
            f"Patienten:   {p.get('patienten_anzahl',0)}",
            f"Status:      {p.get('status','')}",
            f"Archiviert:  {(p.get('archiviert_am') or '')[:16]}",
            "",
        ]
        if p.get("ereignisse"):
            lines += ["Ereignisse / Vorfälle:", p["ereignisse"], ""]
        if fz:
            lines.append("Fahrzeug-Notizen:")
            for f_ in fz:
                kz = f_.get("fahrzeug_kz") or f"ID {f_.get('fahrzeug_id','?')}"
                n  = f_.get("notiz", "")
                lines.append(f"  • {kz}" + (f": {n}" if n else ""))
            lines.append("")
        if hs:
            lines.append("Handys / Geräte:")
            for h_ in hs:
                lines.append(f"  • Gerät {h_.get('geraet_nr','')}" + (f": {h_.get('notiz','')}" if h_.get('notiz') else ""))
            lines.append("")
        if p.get("uebergabe_notiz"):
            lines += ["Übergabe-Notiz:", p["uebergabe_notiz"], ""]

        from PySide6.QtWidgets import QDialog, QTextEdit as _QTE, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle(f"🔍 Archiv-Protokoll #{archiv_id} – Details")
        dlg.setMinimumWidth(540)
        dlg.setMinimumHeight(420)
        dlg_layout = QVBoxLayout(dlg)
        te = _QTE()
        te.setReadOnly(True)
        te.setPlainText("\n".join(lines))
        te.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        dlg_layout.addWidget(te)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        bb.rejected.connect(dlg.reject)
        dlg_layout.addWidget(bb)
        dlg.exec()

    def _browse_schulungen_excel(self):
        current = self._schulung_excel_edit.text().strip()
        start_dir = os.path.dirname(current) if os.path.isfile(current) else os.path.expanduser("~")
        pfad, _ = QFileDialog.getOpenFileName(
            self, "Schulungen Stammdaten-Excel auswählen", start_dir,
            "Excel-Dateien (*.xlsx *.xls)"
        )
        if pfad:
            self._schulung_excel_edit.setText(pfad)

    def _schulungen_excel_importieren(self):
        pfad = self._schulung_excel_edit.text().strip()
        if not pfad:
            QMessageBox.warning(self, "Kein Pfad", "Bitte zuerst den Excel-Pfad eingeben.")
            return
        if not os.path.isfile(pfad):
            QMessageBox.warning(self, "Datei nicht gefunden", f"Datei nicht gefunden:\n{pfad}")
            return
        # Pfad speichern
        try:
            from functions.settings_functions import set_setting
            set_setting('schulungen_excel_pfad', pfad)
        except Exception:
            pass
        try:
            from functions.schulungen_db import excel_importieren
            imp, skip = excel_importieren(pfad)
            self._schulung_import_status.setText(
                f"✅ Importiert: {imp}  |  Übersprungen: {skip}"
            )
            self._schulung_import_status.setStyleSheet(
                "color: #107e3e; font-size: 10px; padding: 2px 0;"
            )
        except Exception as exc:
            self._schulung_import_status.setText(f"❌ Fehler: {exc}")
            self._schulung_import_status.setStyleSheet(
                "color: #c0392b; font-size: 10px; padding: 2px 0;"
            )

    def _wiederherstellen_aus_archiv(self):
        """Wiederherstellen ausgewählter Archiv-Protokolle in die Haupt-DB."""
        selected = [i for i in self._archiv_list.selectedItems()
                    if i.data(Qt.ItemDataRole.UserRole) is not None]
        if not selected:
            QMessageBox.information(self, "Hinweis", "Bitte mindestens ein Protokoll auswählen.")
            return
        pw, ok = QInputDialog.getText(
            self, "Passwort erforderlich",
            f"Passwort zum Wiederherstellen von {len(selected)} Protokoll(en):",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return
        if pw != "mettwurst":
            QMessageBox.warning(self, "Falsches Passwort", "Das eingegebene Passwort ist falsch.")
            return
        ids = [i.data(Qt.ItemDataRole.UserRole) for i in selected]
        archiv_path = self._archiv_path_edit.text().strip() or None
        try:
            from functions.archiv_functions import importiere_aus_archiv
            count = importiere_aus_archiv(ids, archiv_path)
            QMessageBox.information(
                self, "Erledigt",
                f"✅ {count} Protokoll(e) wurden in die Hauptdatenbank zurückgeführt."
            )
            self._load_archiv_liste()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Wiederherstellen:\n{e}")

    # ------------------------------------------------------------------

    def _save(self):
        ordner = self._ordner_edit.text().strip()
        sa_ordner = self._sa_ordner_edit.text().strip()

        if ordner and not os.path.isdir(ordner):
            QMessageBox.warning(
                self, "Ungültiger Pfad",
                f"Dienstplan-Ordner existiert nicht:\n{ordner}\n\n"
                "Bitte einen gültigen Ordner auswählen."
            )
            return
        if sa_ordner and not os.path.isdir(sa_ordner):
            QMessageBox.warning(
                self, "Ungültiger Pfad",
                f"Sonderaufgaben-Ordner existiert nicht:\n{sa_ordner}\n\n"
                "Bitte einen gültigen Ordner auswählen."
            )
            return
        try:
            from functions.settings_functions import set_setting, set_bulmor_gesamt, set_bulmor_schwellen
            set_setting('dienstplan_ordner', ordner)
            set_setting('sonderaufgaben_ordner', sa_ordner)
            set_setting('aocc_datei', self._aocc_edit.text().strip())
            set_setting('code19_datei', self._c19_edit.text().strip())
            set_setting('schulungen_excel_pfad', self._schulung_excel_edit.text().strip())
            set_bulmor_gesamt(self._bulmor_gesamt_spin.value())
            set_bulmor_schwellen(self._bulmor_rot_spin.value(), self._bulmor_gelb_spin.value())
            QMessageBox.information(
                self, "Gespeichert",
                "✅ Einstellungen wurden gespeichert.\n\n"
                "Die neuen Ordner werden beim nächsten Wechsel\n"
                "zum jeweiligen Tab angezeigt."
            )
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")
