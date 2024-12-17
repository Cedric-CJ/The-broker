class Aktie {
  String name;
  double preis;
  String branche;
  List<double> preisHistory;

  Aktie(this.name, this.preis, this.branche) : preisHistory = [preis];
}

class Aktionskarte {
  String name;
  double upValue;
  double downValue;
  String? fixedUp;
  String? fixedDown;

  Aktionskarte({
    required this.name,
    required this.upValue,
    required this.downValue,
    this.fixedUp,
    this.fixedDown,
  });
}

class Spieler {
  String name;
  double kapital = 300;
  Map<String, int> depot = {};
  List<Aktionskarte> karten = [];

  Spieler(this.name);
}
