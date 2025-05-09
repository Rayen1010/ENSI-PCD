import 'package:flutter/material.dart';
import 'package:flutter_application_1/pages/home.dart';

void main() {
  runApp(MyApp());
}

// The main app widget
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SmartShop-app',
      // theme: ThemeData(primarySwatch: Colors.blueGrey),
      theme: ThemeData(
      appBarTheme: AppBarTheme(
         iconTheme: IconThemeData(
           color: Colors.white, // Changes all app bar icons globally
         ),
       ),
      ),
      home: HomePage(),
    );
  }
}