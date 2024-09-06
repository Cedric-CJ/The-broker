import tkinter as tk
from tkinter import messagebox
import random

# Klasse für Aktien im Spiel
class Aktie:
    def __init__(self, name, preis, branche):
        self.name = name
        self.preis = preis
        self.branche = branche

# Klasse für Aktionskarten
class Aktionskarte:
    def __init__(self, name, up_value, down_value, fixed_up=None, fixed_down=None, multiplier=None, fixed_multiplier=None):
        self.name = name
        self.up_value = up_value
        self.down_value = down_value
        self.fixed_up = fixed_up  # Festgelegte Aktie, die steigt
        self.fixed_down = fixed_down  # Festgelegte Aktie, die fällt
        self.multiplier = multiplier  # Typ der Multiplikator-Karten
        self.fixed_multiplier = fixed_multiplier  # Festgelegte Aktie für Multiplikator

# Spieler Klasse mit den Hauptaktionen
class Spieler:
    def __init__(self, name):
        self.name = name
        self.kapital = 300  # Startkapital
        self.depot = {}  # Aktienbestände
        self.karten = []  # Liste der Aktionskarten
        self.kumulierte_gewinn = 0  # Gesamtgewinn über das Spiel hinweg

# GUI Klasse
class BoersenspielGUI:
    def __init__(self, spieler, aktien):
        self.root = tk.Tk()
        self.root.title("Börsenspiel")
        self.spieler = spieler
        self.aktien = aktien
        self.aktueller_spieler_index = 0
        self.zeige_spieler_info()

    def zeige_spieler_info(self):
        # Aktuelle Spielerinformationen anzeigen
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        self.clear_frame()

        label_name = tk.Label(self.root, text=f"Spieler: {aktueller_spieler.name}")
        label_name.pack()

        label_kapital = tk.Label(self.root, text=f"Verfügbares Kapital: {aktueller_spieler.kapital}€")
        label_kapital.pack()

        label_aktien = tk.Label(self.root, text="Aktuelle Aktien:")
        label_aktien.pack()
        if aktueller_spieler.depot:
            for aktie, menge in aktueller_spieler.depot.items():
                label_aktie = tk.Label(self.root, text=f"- {aktie}: {menge} Anteile")
                label_aktie.pack()
        else:
            label_keine_aktien = tk.Label(self.root, text="Keine Aktien im Depot.")
            label_keine_aktien.pack()

        # Aktionskarten sortieren und anzeigen
        aktueller_spieler.karten.sort(key=lambda x: (x.fixed_up or x.fixed_down or x.fixed_multiplier or ""))
        label_karten = tk.Label(self.root, text="Verfügbare Aktionskarten:")
        label_karten.pack()
        for idx, karte in enumerate(aktueller_spieler.karten):
            karte_info = f"{karte.up_value}€ steigt "
            if karte.fixed_up:
                karte_info += f"{karte.fixed_up} und {karte.down_value}€ fällt X"
            elif karte.fixed_down:
                karte_info += f"X und {karte.down_value}€ fällt {karte.fixed_down}"
            elif karte.multiplier == "double":
                if karte.fixed_multiplier == "double":
                    karte_info = f"*2 steigt {karte.fixed_up} und *0,5 fällt X"
                else:
                    karte_info = f"*2 steigt X und *0,5 fällt {karte.fixed_down}"
            else:
                karte_info += f"X und {karte.down_value}€ fällt X"
            label_karte = tk.Label(self.root, text=f"{idx + 1}. {karte_info}")
            label_karte.pack()

        # Buttons für Aktionen
        button_kaufen = tk.Button(self.root, text="Aktien kaufen", command=self.kaufen)
        button_kaufen.pack(pady=5)

        button_verkaufen = tk.Button(self.root, text="Aktien verkaufen", command=self.verkaufen)
        button_verkaufen.pack(pady=5)

        button_karte_spielen = tk.Button(self.root, text="Aktionskarte spielen", command=self.karte_spielen)
        button_karte_spielen.pack(pady=5)

    def clear_frame(self):
        # Entfernt alle Widgets im aktuellen Fenster, um Platz für neue zu schaffen
        for widget in self.root.winfo_children():
            widget.destroy()

    def kaufen(self):
        # Funktion für den Kauf von Aktien
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        self.clear_frame()
        label_aktien = tk.Label(self.root, text="Verfügbare Aktien zum Kauf:")
        label_aktien.pack()
        aktien_buttons = []

        for idx, aktie in enumerate(self.aktien):
            button = tk.Button(self.root, text=f"{aktie.name} - Preis: {aktie.preis}€",
                               command=lambda idx=idx: self.kauf_auswahl(idx))
            button.pack(pady=2)
            aktien_buttons.append(button)

        button_back = tk.Button(self.root, text="Zurück", command=self.zeige_spieler_info)
        button_back.pack(pady=5)

    def kauf_auswahl(self, aktien_index):
        # Auswahlmenge der zu kaufenden Aktien
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        aktie = self.aktien[aktien_index]
        menge = 1  # Für eine einfachere Implementierung auf 1 gesetzt

        kosten = aktie.preis * menge + 1
        if aktueller_spieler.kapital >= kosten:
            aktueller_spieler.kapital -= kosten
            if aktie.name in aktueller_spieler.depot:
                aktueller_spieler.depot[aktie.name] += menge
            else:
                aktueller_spieler.depot[aktie.name] = menge
            messagebox.showinfo("Kauf erfolgreich", f"{aktueller_spieler.name} hat {menge} Aktie(n) von {aktie.name} gekauft.")
        else:
            messagebox.showerror("Fehler", "Nicht genug Kapital.")
        self.zeige_spieler_info()

    def verkaufen(self):
        # Funktion für den Verkauf von Aktien
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        self.clear_frame()
        if not aktueller_spieler.depot:
            messagebox.showinfo("Depot leer", "Du hast keine Aktien im Depot.")
            self.zeige_spieler_info()
            return

        label_depot = tk.Label(self.root, text="Verfügbare Aktien zum Verkauf:")
        label_depot.pack()
        depot_buttons = []

        for idx, (name, menge) in enumerate(aktueller_spieler.depot.items()):
            button = tk.Button(self.root, text=f"{name} - Menge: {menge}",
                               command=lambda name=name: self.verkauf_auswahl(name))
            button.pack(pady=2)
            depot_buttons.append(button)

        button_back = tk.Button(self.root, text="Zurück", command=self.zeige_spieler_info)
        button_back.pack(pady=5)

    def verkauf_auswahl(self, aktie_name):
        # Verkauf der ausgewählten Aktien
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        aktie = next(a for a in self.aktien if a.name == aktie_name)
        menge = 1  # Für eine einfachere Implementierung auf 1 gesetzt

        if aktueller_spieler.depot[aktie_name] >= menge:
            erlöse = aktie.preis * menge - 1
            aktueller_spieler.kapital += erlöse
            aktueller_spieler.depot[aktie_name] -= menge
            if aktueller_spieler.depot[aktie_name] == 0:
                del aktueller_spieler.depot[aktie_name]
            messagebox.showinfo("Verkauf erfolgreich", f"{aktueller_spieler.name} hat {menge} Aktie(n) von {aktie_name} verkauft.")
        else:
            messagebox.showerror("Fehler", "Nicht genug Aktien im Depot.")
        self.zeige_spieler_info()

    def karte_spielen(self):
        # Funktion für das Spielen einer Aktionskarte
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        if not aktueller_spieler.karten:
            messagebox.showinfo("Keine Karten", "Keine Aktionskarten mehr verfügbar.")
            return

        self.clear_frame()
        label_karten = tk.Label(self.root, text="Verfügbare Aktionskarten zum Spielen:")
        label_karten.pack()

        for idx, karte in enumerate(aktueller_spieler.karten):
            karte_info = f"{karte.up_value}€ steigt "
            if karte.fixed_up:
                karte_info += f"{karte.fixed_up} und {karte.down_value}€ fällt X"
            elif karte.fixed_down:
                karte_info += f"X und {karte.down_value}€ fällt {karte.fixed_down}"
            elif karte.multiplier == "double":
                if karte.fixed_multiplier == "double":
                    karte_info = f"*2 steigt {karte.fixed_up} und *0,5 fällt X"
                else:
                    karte_info = f"*2 steigt X und *0,5 fällt {karte.fixed_down}"
            else:
                karte_info += f"X und {karte.down_value}€ fällt X"

            button = tk.Button(self.root, text=karte_info, command=lambda idx=idx: self.spiele_karte(idx))
            button.pack(pady=2)

        button_back = tk.Button(self.root, text="Zurück", command=self.zeige_spieler_info)
        button_back.pack(pady=5)

    def spiele_karte(self, karten_index):
        # Effekte der Aktionskarte anwenden
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        karte = aktueller_spieler.karten.pop(karten_index)

        # Implementierung der Karten-Effekte kann hier weitergeführt werden
        messagebox.showinfo("Karte gespielt", "Die Effekte der Karte wurden angewendet.")
        self.zeige_spieler_info()

    def run(self):
        self.root.mainloop()

# Initialisierung des Spiels
def spiel_initialisieren():
    # Aktien initialisieren
    aktien = [
        Aktie("Deutsche Bank", 100, "Finanzen"),
        Aktie("BP", 100, "Energie"),
        Aktie("Siemens", 100, "Technologie"),
        Aktie("IBM", 100, "Technologie")
    ]

    # Spieleranzahl und Namen
    spieler_anzahl = int(input("Wie viele Spieler nehmen teil? "))
    spieler = [Spieler(input(f"Name von Spieler {i + 1}: ")) for i in range(spieler_anzahl)]

    # Verteilung der Karten an die Spieler
    for s in spieler:
        s.karten.extend(
            [
                Aktionskarte("40€ Up / 50€ Down (frei)", 40, 50, fixed_down="Deutsche Bank"),
                Aktionskarte("60€ Up / 30€ Down (frei)", 60, 30, fixed_down="IBM"),
                Aktionskarte("60€ Up / 30€ Down (fest)", 60, 30, fixed_up="Siemens"),
                Aktionskarte("100€ Up / 50€ Down (frei)", 100, 50, fixed_down="Deutsche Bank"),
                Aktionskarte("60€ Up / 30€ Down (frei)", 60, 30, fixed_down="IBM"),
                Aktionskarte("40€ Up / 50€ Down (fest)", 40, 50, fixed_up="Siemens"),
                Aktionskarte("*2 / *0,5", 0, 0, multiplier="double", fixed_multiplier="double", fixed_up="Siemens"),
                Aktionskarte("*2 / *0,5", 0, 0, multiplier="double", fixed_multiplier="half", fixed_down="IBM"),
                Aktionskarte("100€ Up / 50€ Down (frei)", 100, 50, fixed_down="Deutsche Bank"),
                Aktionskarte("60€ Up / 30€ Down (fest)", 60, 30, fixed_up="BP"),
            ]
        )

    # Zufällige Startreihenfolge festlegen
    random.shuffle(spieler)

    return aktien, spieler

# Start des Spiels
aktien, spieler = spiel_initialisieren()
game = BoersenspielGUI(spieler, aktien)
game.run()


