# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Klasse für Aktien im Spiel
class Aktie:
    def __init__(self, aktien_name, preis, branche):
        self.name = aktien_name
        self.preis = preis
        self.branche = branche
        self.preis_history = [preis]  # Verfolge den Preisverlauf


# Klasse für Aktionskarten
class Aktionskarte:
    def __init__(self, karten_name, up_value, down_value, fixed_up=None, fixed_down=None,
                 multiplier=None, fixed_multiplier=None):
        self.name = karten_name
        self.up_value = up_value
        self.down_value = down_value
        self.fixed_up = fixed_up  # Festgelegte Aktie, die steigt
        self.fixed_down = fixed_down  # Festgelegte Aktie, die fällt
        self.multiplier = multiplier  # Typ der Multiplikator-Karten
        self.fixed_multiplier = fixed_multiplier  # Festgelegte Aktie für Multiplikator


# Spieler-Klasse mit den Hauptaktionen
class Spieler:
    def __init__(self, spieler_name):
        self.name = spieler_name
        self.kapital = 300  # Startkapital
        self.depot = {}  # Aktienbestände
        self.karten = []  # Liste der Aktionskarten
        self.kumulierte_gewinn = 0  # Gesamtgewinn über das Spiel hinweg


# GUI Klasse
class BoersenspielGUI:
    def __init__(self, spieler_list, aktien_list):
        self.root = tk.Tk()
        self.root.title("Börsenspiel")
        self.spieler = spieler_list
        self.aktien = aktien_list
        self.aktueller_spieler_index = 0
        self.aktie_auswahl_fenster_aktiv = False  # Kontrollvariable für die Aktienauswahl
        self.aktuelle_karte = None
        self.zeige_spieler_info()

    def zeige_spieler_info(self):
        self.clear_frame()
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]

        label_name = tk.Label(self.root, text=f"Spieler: {aktueller_spieler.name}")
        label_name.pack()

        label_kapital = tk.Label(self.root, text=f"Verfügbares Kapital: {aktueller_spieler.kapital}€")
        label_kapital.pack()

        label_aktien = tk.Label(self.root, text="Aktuelle Aktien:")
        label_aktien.pack()

        if aktueller_spieler.depot:
            for aktien_name, menge in aktueller_spieler.depot.items():
                label_aktie = tk.Label(self.root, text=f"- {aktien_name}: {menge} Anteile")
                label_aktie.pack()
        else:
            label_keine_aktien = tk.Label(self.root, text="Keine Aktien im Depot.")
            label_keine_aktien.pack()

        # Aktionskarten sortieren und anzeigen
        aktueller_spieler.karten.sort(key=lambda x: (x.fixed_up or x.fixed_down or x.fixed_multiplier or ""))
        label_karten = tk.Label(self.root, text="Verfügbare Aktionskarten:")
        label_karten.pack()
        for i, karte in enumerate(aktueller_spieler.karten):
            if karte.multiplier == "double":
                karte_info = (f"*2 steigt {karte.fixed_up or 'X'} "
                              f"und *0,5 fällt {karte.fixed_down or 'X'}")
            else:
                karte_info = (f"{karte.up_value}€ steigt {karte.fixed_up or 'X'} "
                              f"und {karte.down_value}€ fällt {karte.fixed_down or 'X'}")
            label_karte = tk.Label(self.root, text=f"{i + 1}. {karte_info}")
            label_karte.pack()

        # Buttons für Aktionen
        button_kaufen = tk.Button(self.root, text="Aktien kaufen", command=self.kaufen)
        button_kaufen.pack(pady=5)

        button_verkaufen = tk.Button(self.root, text="Aktien verkaufen", command=self.verkaufen)
        button_verkaufen.pack(pady=5)

        button_karte_spielen = tk.Button(self.root, text="Aktionskarte spielen", command=self.karte_spielen)
        button_karte_spielen.pack(pady=5)

        button_plot = tk.Button(self.root, text="Preisentwicklung anzeigen", command=self.plot_stock_prices)
        button_plot.pack(pady=5)

    def clear_frame(self):
        # Entfernt alle Widgets im aktuellen Fenster
        for widget in self.root.winfo_children():
            widget.destroy()

    def kaufen(self):
        self.clear_frame()
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]

        label_aktien = tk.Label(self.root, text="Verfügbare Aktien zum Kauf:")
        label_aktien.pack()

        for aktie in self.aktien:
            max_kaufbar = aktueller_spieler.kapital // aktie.preis
            if max_kaufbar > 0:
                frame = tk.Frame(self.root)
                frame.pack(pady=5)

                label = tk.Label(frame, text=f"{aktie.name} - Preis: {aktie.preis}€")
                label.pack(side=tk.LEFT)

                slider = tk.Scale(frame, from_=1, to=max_kaufbar, orient=tk.HORIZONTAL, label="Menge")
                slider.pack(side=tk.LEFT)

                button_kaufen = tk.Button(frame, text="Kaufen",
                                          command=lambda a=aktie, s=slider: self.kauf_ausfuehren(a, s.get()))
                button_kaufen.pack(side=tk.LEFT)

        button_back = tk.Button(self.root, text="Zurück", command=self.zeige_spieler_info)
        button_back.pack(pady=5)


    def kauf_auswahl(self, aktien_index):
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        aktie = self.aktien[aktien_index]
        menge = 1  # Einfach gehalten

        kosten = aktie.preis * menge
        if aktueller_spieler.kapital >= kosten:
            aktueller_spieler.kapital -= kosten
            aktueller_spieler.depot[aktie.name] = aktueller_spieler.depot.get(aktie.name, 0) + menge
            messagebox.showinfo("Kauf erfolgreich",
                                f"{aktueller_spieler.name} hat {menge} Aktie(n) von {aktie.name} gekauft.")
        else:
            messagebox.showerror("Fehler", "Nicht genug Kapital.")
        self.zeige_spieler_info()

    def kauf_ausfuehren(self, aktie, menge):
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        kosten = aktie.preis * menge

        if aktueller_spieler.kapital >= kosten:
            # Kapital reduzieren
            aktueller_spieler.kapital -= kosten
            # Aktien dem Depot hinzufügen oder Anzahl erhöhen
            if aktie.name in aktueller_spieler.depot:
                aktueller_spieler.depot[aktie.name] += menge
            else:
                aktueller_spieler.depot[aktie.name] = menge

            # Erfolgsmeldung anzeigen
            messagebox.showinfo("Kauf erfolgreich",
                            f"{aktueller_spieler.name} hat {menge} Aktie(n) von {aktie.name} für {kosten}€ gekauft.")
        else:
            # Fehlermeldung anzeigen
            messagebox.showerror("Nicht genug Kapital", "Du hast nicht genug Kapital, um diese Aktien zu kaufen.")

        # Nach dem Kauf zurück zur Spielerinfo
        self.zeige_spieler_info()

    def verkaufen(self):
        self.clear_frame()
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]

        if not aktueller_spieler.depot:
            messagebox.showinfo("Depot leer", "Du hast keine Aktien im Depot.")
            self.zeige_spieler_info()
            return

        label_depot = tk.Label(self.root, text="Verfügbare Aktien zum Verkauf:")
        label_depot.pack()

        for aktien_name, menge in aktueller_spieler.depot.items():
            aktie = next(a for a in self.aktien if a.name == aktien_name)

            frame = tk.Frame(self.root)
            frame.pack(pady=5)

            label = tk.Label(frame, text=f"{aktie.name} - Preis: {aktie.preis}€ - Verfügbar: {menge} Anteile")
            label.pack(side=tk.LEFT)

            # Slider für die Menge, die verkauft werden soll
            slider = tk.Scale(frame, from_=1, to=menge, orient=tk.HORIZONTAL, label="Menge")
            slider.pack(side=tk.LEFT)

            # Verkaufs-Button mit Verbindung zur verkauf_ausfuehren-Methode
            button_verkaufen = tk.Button(frame, text="Verkaufen",
                                         command=lambda a=aktie, s=slider: self.verkauf_ausfuehren(a, s.get()))
            button_verkaufen.pack(side=tk.LEFT)

        button_back = tk.Button(self.root, text="Zurück", command=self.zeige_spieler_info)
        button_back.pack(pady=5)

    def verkauf_auswahl(self, aktie_name):
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        aktie = next(a for a in self.aktien if a.name == aktie_name)
        menge = 1  # Einfach gehalten

        if aktueller_spieler.depot[aktie_name] >= menge:
            erloese = aktie.preis * menge
            aktueller_spieler.kapital += erloese
            aktueller_spieler.depot[aktie_name] -= menge
            if aktueller_spieler.depot[aktie_name] == 0:
                del aktueller_spieler.depot[aktie_name]
            messagebox.showinfo("Verkauf erfolgreich",
                                f"{aktueller_spieler.name} hat {menge} Aktie(n) von {aktie_name} verkauft.")
        else:
            messagebox.showerror("Fehler", "Nicht genug Aktien im Depot.")
        self.zeige_spieler_info()

    def verkauf_ausfuehren(self, aktie, menge):
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]

        if aktueller_spieler.depot.get(aktie.name, 0) >= menge:
            # Kapital erhöhen
            erloese = aktie.preis * menge
            aktueller_spieler.kapital += erloese
            # Aktienbestand im Depot reduzieren
            aktueller_spieler.depot[aktie.name] -= menge
            if aktueller_spieler.depot[aktie.name] == 0:
                del aktueller_spieler.depot[aktie.name]

            # Erfolgsmeldung anzeigen
            messagebox.showinfo("Verkauf erfolgreich",
                            f"{aktueller_spieler.name} hat {menge} Aktie(n) von {aktie.name} für {erloese}€ verkauft.")
        else:
            # Fehlermeldung anzeigen
            messagebox.showerror("Fehler", "Nicht genug Aktien im Depot.")

        # Nach dem Verkauf zurück zur Spielerinfo
        self.zeige_spieler_info()

    def karte_spielen(self):
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        if not aktueller_spieler.karten:
            messagebox.showinfo("Keine Karten", "Keine Aktionskarten mehr verfügbar.")
            return

        self.clear_frame()
        label_karten = tk.Label(self.root, text="Verfügbare Aktionskarten zum Spielen:")
        label_karten.pack()

        for i, karte in enumerate(aktueller_spieler.karten):
            if karte.multiplier == "double":
                karte_info = (f"*2 steigt {karte.fixed_up or 'X'} "
                              f"und *0,5 fällt {karte.fixed_down or 'X'}")
            else:
                karte_info = (f"{karte.up_value}€ steigt {karte.fixed_up or 'X'} "
                              f"und {karte.down_value}€ fällt {karte.fixed_down or 'X'}")

            button = tk.Button(self.root, text=karte_info, command=lambda k_idx=i: self.spiele_karte(k_idx))
            button.pack(pady=2)

        button_back = tk.Button(self.root, text="Zurück", command=self.zeige_spieler_info)
        button_back.pack(pady=5)

    def spiele_karte(self, karten_index):
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        self.aktuelle_karte = aktueller_spieler.karten.pop(karten_index)

        # Spieler wählt Aktie, die fällt, falls noch nicht gesetzt
        if not self.aktuelle_karte.fixed_down:
            # Filtere die Optionen: Entferne die Aktie, die bereits für den "Up-Effekt" ausgewählt wurde
            verfuegbare_aktien = [a.name for a in self.aktien if a.name != self.aktuelle_karte.fixed_up]
            aktie_name_down = self.waehle_aktie_dialog("Wähle eine Aktie, die fallen soll:", verfuegbare_aktien)
            if aktie_name_down:
                self.aktuelle_karte.fixed_down = aktie_name_down

        # Spieler wählt Aktie, die steigt, falls noch nicht gesetzt
        if not self.aktuelle_karte.fixed_up:
            # Filtere die Optionen: Entferne die Aktie, die bereits für den "Down-Effekt" ausgewählt wurde
            verfuegbare_aktien = [a.name for a in self.aktien if a.name != self.aktuelle_karte.fixed_down]
            aktie_name_up = self.waehle_aktie_dialog("Wähle eine Aktie, die steigen soll:", verfuegbare_aktien)
            if aktie_name_up:
                self.aktuelle_karte.fixed_up = aktie_name_up

        # Bestätigungs-Button zum endgültigen Anwenden der Effekte
        button_bestaetigen = tk.Button(self.root, text="Bestätigen", command=self.karte_effekte_anwenden)
        button_bestaetigen.pack(pady=5)


    def karte_effekte_anwenden(self):
        if not self.aktuelle_karte:
            return

        karte = self.aktuelle_karte

        # Up-Effekt anwenden
        if karte.fixed_up:
            aktie_up = next((a for a in self.aktien if a.name == karte.fixed_up), None)
            if aktie_up:
                aktie_up.preis += karte.up_value
                aktie_up.preis_history.append(aktie_up.preis)

        # Down-Effekt anwenden
        if karte.fixed_down:
            aktie_down = next((a for a in self.aktien if a.name == karte.fixed_down), None)
            if aktie_down:
                new_price = aktie_down.preis - karte.down_value
                if new_price <= 0:
                    new_price = 1
                    # Alle Spieleranteile halbieren
                    for sp in self.spieler:
                        if aktie_down.name in sp.depot:
                            old_amount = sp.depot[aktie_down.name]
                            if old_amount > 1:
                                sp.depot[aktie_down.name] = max(1, old_amount // 2)
                aktie_down.preis = new_price
                aktie_down.preis_history.append(new_price)

        messagebox.showinfo("Karte gespielt", "Die Effekte der Karte wurden angewendet.")

        # Nächster Spieler ist dran
        self.aktuelle_karte = None
        self.aktueller_spieler_index = (self.aktueller_spieler_index + 1) % len(self.spieler)
        self.zeige_spieler_info()

    def waehle_aktie_dialog(self, message, verfuegbare_aktien):
        # Dialog zur Auswahl einer Aktie durch den Spieler
        if self.aktie_auswahl_fenster_aktiv:
            return None  # Verhindert mehrfaches Öffnen

        self.aktie_auswahl_fenster_aktiv = True

        auswahl_fenster = tk.Toplevel(self.root)
        auswahl_fenster.title("Aktie auswählen")

        label = tk.Label(auswahl_fenster, text=message)
        label.pack()

        auswahl_var = tk.StringVar(auswahl_fenster)
        if verfuegbare_aktien:
            auswahl_var.set(verfuegbare_aktien[0])

        aktie_menu = tk.OptionMenu(auswahl_fenster, auswahl_var, *verfuegbare_aktien)
        aktie_menu.pack()

        selected_stock = [None]

        def confirm_selection():
            selected_stock[0] = auswahl_var.get()
            auswahl_fenster.destroy()
            self.aktie_auswahl_fenster_aktiv = False

        button_confirm = tk.Button(auswahl_fenster, text="Bestätigen", command=confirm_selection)
        button_confirm.pack()

        self.root.wait_window(auswahl_fenster)
        return selected_stock[0]


    def plot_stock_prices(self):
        # Grafische Darstellung der Aktienpreise mit animierter Linie
        fig, ax = plt.subplots()
        ax.set_ylim(0, 250)  # Begrenze die Y-Achse auf 250€

        # Erstelle Linien für jede Aktie
        lines = {aktie.name: ax.plot([], [], label=aktie.name, marker='o')[0] for aktie in self.aktien}

        def init():
            if len(self.aktien[0].preis_history) > 1:
                ax.set_xlim(1, len(self.aktien[0].preis_history))
            return lines.values()

        def update(_frame):
            for a in self.aktien:
                rounds = list(range(1, len(a.preis_history) + 1))
                lines[a.name].set_data(rounds, a.preis_history)
            return lines.values()

        # ani wird nicht weiter verwendet, aber wir benötigen die Referenz, um die Animation nicht vorzeitig zu löschen
        _ani = FuncAnimation(fig, update, frames=range(1, len(self.aktien[0].preis_history) + 1),
                             init_func=init, blit=True, repeat=False)

        plt.title("Preisentwicklung der Aktien")
        plt.xlabel("Runde")
        plt.ylabel("Preis (€)")
        plt.legend()
        plt.grid(True)
        plt.show()

    def run(self):
        self.root.mainloop()


def spiel_initialisieren():
    # Aktien initialisieren
    aktien_list = [
        Aktie("Deutsche Bank", 100, "Finanzen"),
        Aktie("BP", 100, "Energie"),
        Aktie("Siemens", 100, "Technologie"),
        Aktie("IBM", 100, "Technologie")
    ]

    # Spieleranzahl und Namen
    spieler_count = int(input("Wie viele Spieler nehmen teil? "))
    spieler_list = [Spieler(input(f"Name von Spieler {i + 1}: ")) for i in range(spieler_count)]

    # Verteilung der Karten an die Spieler
    for s in spieler_list:
        s.karten.extend(
            [
                Aktionskarte("40€ Up / 50€ Down (frei)", 40, 50, fixed_down="Deutsche Bank"),
                Aktionskarte("60€ Up / 30€ Down (frei)", 60, 30, fixed_down="IBM"),
                Aktionskarte("60€ Up / 30€ Down (fest)", 60, 30, fixed_up="Siemens"),
                Aktionskarte("100€ Up / 50€ Down (frei)", 100, 50, fixed_down="Deutsche Bank"),
                Aktionskarte("60€ Up / 30€ Down (frei)", 60, 30, fixed_down="IBM"),
                Aktionskarte("40€ Up / 50€ Down (fest)", 40, 50, fixed_up="Siemens"),
                Aktionskarte("*2 / *0,5", 0, 0, multiplier="double",
                             fixed_multiplier="double", fixed_up="Siemens"),
                Aktionskarte("*2 / *0,5", 0, 0, multiplier="double",
                             fixed_multiplier="half", fixed_down="IBM"),
                Aktionskarte("100€ Up / 50€ Down (frei)", 100, 50, fixed_down="Deutsche Bank"),
                Aktionskarte("60€ Up / 30€ Down (fest)", 60, 30, fixed_up="BP"),
            ]
        )

    # Zufällige Startreihenfolge festlegen
    random.shuffle(spieler_list)
    return aktien_list, spieler_list


if __name__ == "__main__":
    aktien_list, spieler_list = spiel_initialisieren()
    game = BoersenspielGUI(spieler_list, aktien_list)
    game.run()
