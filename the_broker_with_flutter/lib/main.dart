import 'package:flutter/material.dart';
import 'game_screen.dart';

void main() {
  runApp(const BoersenspielApp());
}

class BoersenspielApp extends StatelessWidget {
  const BoersenspielApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Börsenspiel',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const GameScreen(),
    );
  }
}
