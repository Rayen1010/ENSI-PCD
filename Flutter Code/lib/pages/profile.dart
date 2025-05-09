import 'package:flutter/material.dart';
import 'package:flutter_application_1/pages/receipts.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ProfilePage extends StatefulWidget {

  const ProfilePage({
    super.key
    // required this.userName,
    // required this.email,
  });

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final storage = FlutterSecureStorage();

  String userName = '';

  String email = '';

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  void _loadUserData() async {
    userName = await storage.read(key: 'userName') ?? 'Rami';
    email = await storage.read(key: 'email') ?? 'rami@gmail.com';

    setState(() {});
  }

@override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: appBar(),
    body: Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 24),
      child: Column(
        mainAxisSize: MainAxisSize.max,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(Icons.account_circle, size: 100, color: Colors.blueGrey[800]),
          const SizedBox(height: 60),

          // Centered user details
          Center(
            child: Table(
              columnWidths: const {
                0: IntrinsicColumnWidth(),
                1: IntrinsicColumnWidth(),
              },
              defaultVerticalAlignment: TableCellVerticalAlignment.middle,
              children: [
                TableRow(
                  children: [
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text(
                        'Username :',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 8.0),
                      child: Text(
                        userName!,
                        style: const TextStyle(fontSize: 18, fontWeight : FontWeight.bold, color : Colors.blueGrey),
                      ),
                    ),
                  ],
                ),
                TableRow(
                  children: [
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text(
                        'Email :',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 8.0),
                      child: Text(
                        email!,
                        style: const TextStyle(fontSize: 18, fontWeight : FontWeight.bold, color : Colors.blueGrey),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),

          // Centered button
          Center(
            child: ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const ReceiptsPage()),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueGrey[800],
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              // child: const Text('Go', style: TextStyle(color: Colors.white)),
              child: const Text('Receipts', style: TextStyle(fontSize: 18, color: Colors.white)),
            ),
          ),
        ],
      ),
    ),
  );
}

AppBar appBar() {
  return AppBar(
    title : Text(
      'Profile',
      style : TextStyle(
        color : Colors.white,
        fontSize: 24,
        fontWeight : FontWeight.bold
      )
    ),
    backgroundColor: Colors.blueGrey[800],
    elevation: 0,
  );
}
}
