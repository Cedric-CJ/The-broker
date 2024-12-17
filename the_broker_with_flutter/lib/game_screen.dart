import 'package:flutter/material.dart';
import 'models.dart';
import 'package:fl_chart/fl_chart.dart';

class GameScreen extends StatefulWidget {
  const GameScreen({Key? key}) : super(key: key);

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  List<Aktie> aktien = [
    Aktie('Deutsche Bank', 100, 'Finanzen'),
    Aktie('BP', 100, 'Energie'),
    Aktie('Siemens', 100, 'Technologie'),
    Aktie('IBM', 100, 'Technologie'),
  ];

  List<Spieler> spieler = [];
  int aktuellerSpielerIndex = 0;
  Map<String, double> sliderWerte = {};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _spielerAbfrage();
    });
  }

  Future<void> _spielerAbfrage() async {
    List<Spieler> neueSpieler = [];
    int anzahl = await _spielerAnzahlDialog();
    for (int i = 0; i < anzahl; i++) {
      String? name = await _spielerNameDialog(i + 1);
      if (name != null && name.isNotEmpty) {
        neueSpieler.add(Spieler(name));
      }
    }
    setState(() {
      spieler = neueSpieler;
      sliderWerte = {for (var aktie in aktien) aktie.name: 1};
    });
  }

  Future<int> _spielerAnzahlDialog() async {
    int anzahl = 1;
    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          title: const Text("Spieleranzahl"),
          content: DropdownButton<int>(
            value: anzahl,
            items: [1, 2, 3, 4]
                .map((e) => DropdownMenuItem(value: e, child: Text("$e Spieler")))
                .toList(),
            onChanged: (value) {
              anzahl = value!;
              Navigator.pop(context);
            },
          ),
        );
      },
    );
    return anzahl;
  }

  Future<String?> _spielerNameDialog(int spielerNummer) async {
    TextEditingController controller = TextEditingController();
    String? name;
    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          title: Text("Name für Spieler $spielerNummer"),
          content: TextField(
            controller: controller,
            decoration: const InputDecoration(labelText: "Name"),
          ),
          actions: [
            TextButton(
              onPressed: () {
                name = controller.text;
                Navigator.pop(context);
              },
              child: const Text("OK"),
            ),
          ],
        );
      },
    );
    return name;
  }

  void _aktienKaufen(Aktie aktie, int menge) {
    var spielerAktuell = spieler[aktuellerSpielerIndex];
    double kosten = aktie.preis * menge;
    if (spielerAktuell.kapital >= kosten) {
      setState(() {
        spielerAktuell.kapital -= kosten;
        spielerAktuell.depot[aktie.name] = (spielerAktuell.depot[aktie.name] ?? 0) + menge;
      });
      _zeigeSnackBar("Gekauft: $menge Anteile von ${aktie.name}");
    } else {
      _zeigeSnackBar("Nicht genug Kapital.");
    }
  }

  void _aktienVerkaufen(Aktie aktie, int menge) {
    var spielerAktuell = spieler[aktuellerSpielerIndex];
    int depotAnzahl = spielerAktuell.depot[aktie.name] ?? 0;

    if (depotAnzahl >= menge) {
      setState(() {
        spielerAktuell.kapital += aktie.preis * menge;
        spielerAktuell.depot[aktie.name] = depotAnzahl - menge;
        if (spielerAktuell.depot[aktie.name] == 0) spielerAktuell.depot.remove(aktie.name);
      });
      _zeigeSnackBar("Verkauft: $menge Anteile von ${aktie.name}");
    } else {
      _zeigeSnackBar("Nicht genug Aktien im Depot.");
    }
  }

  void _zeigeSnackBar(String text) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  }

  @override
  Widget build(BuildContext context) {
    var spielerAktuell = spieler.isNotEmpty ? spieler[aktuellerSpielerIndex] : null;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Börsenspiel'),
      ),
      body: spieler.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : Column(
        children: [
          ListTile(
            title: Text("Spieler: ${spielerAktuell!.name}"),
            subtitle: Text("Kapital: ${spielerAktuell.kapital.toStringAsFixed(2)} €"),
          ),
          const Divider(),
          const Text("Verfügbare Aktien zum Kauf:"),
          ...aktien.map((aktie) => ListTile(
            title: Text("${aktie.name} - ${aktie.preis.toStringAsFixed(2)} €"),
            trailing: SizedBox(
              width: 200,
              child: Row(
                children: [
                  Expanded(
                    child: Slider(
                      value: sliderWerte[aktie.name]!,
                      min: 1,
                      max: 10,
                      divisions: 10,
                      label: sliderWerte[aktie.name]!.toStringAsFixed(0),
                      onChanged: (value) {
                        setState(() {
                          sliderWerte[aktie.name] = value;
                        });
                      },
                    ),
                  ),
                  ElevatedButton(
                      onPressed: () => _aktienKaufen(aktie, sliderWerte[aktie.name]!.toInt()),
                      child: const Text("Kaufen"))
                ],
              ),
            ),
          )),
          const Divider(),
          const Text("Dein Depot:"),
          ...spielerAktuell.depot.entries.map((entry) {
            Aktie aktie = aktien.firstWhere((a) => a.name == entry.key);
            return ListTile(
              title: Text("${aktie.name} - ${entry.value} Anteile"),
              trailing: ElevatedButton(
                onPressed: () => _aktienVerkaufen(aktie, 1),
                child: const Text("Verkaufen"),
              ),
            );
          }),
        ],
      ),
    );
  }
}
