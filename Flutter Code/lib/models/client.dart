class Client {
  String userName;
  String email;
  String password;
  String card_Id;
  // DateTime? cardDate;



  Client({
    required this.userName,
    required this.email,
    required this.password,
    required this.card_Id
    // required this.cardDate,
  });

  Map<String, dynamic> toJson() => {
    'userName' : userName,
    'email' : email,
    'password' : password,
    'card_Id' : card_Id
    // 'cardDate' : cardDate,
  };
}

class UserCredentials {
  String login;
  String password;

  UserCredentials({required this.login, required this.password});

  Map<String, dynamic> toJson() => {
    'login': login,
    'password': password,
  };
}

class Item {
  final String name;
  final double unitPrice;
  final int quantity;
  final double totalPrice;

  Item({
    required this.name,
    required this.unitPrice,
    required this.quantity,
    required this.totalPrice,
  });

  factory Item.fromJson(Map<String, dynamic> json) {
    return Item(
      name: json['name'],
      unitPrice: json['unit_price'].toDouble(),
      quantity: json['quantity'],
      totalPrice: json['total_price'].toDouble(),
    );
  }
}

class ClientR {
  final List<Item> box;
  final double totalAmount;
  final double credit;
  final DateTime entryDate;        
  final DateTime processingDate;   

  ClientR({
    required this.box,
    required this.totalAmount,
    required this.credit,
    required this.entryDate,       
    required this.processingDate,  
  });

  factory ClientR.fromJson(Map<String, dynamic> json) {
    try {
      final boxJson = json['box'] as List? ?? [];
      return ClientR(
        box: boxJson.map((item) => Item.fromJson(item)).toList(),
        totalAmount: (json['total_amount'] ?? 0).toDouble(),
        credit: (json['credit'] ?? 0).toDouble(),
        entryDate: DateTime.parse(json['entry_date'] ?? DateTime.now().toIso8601String()),
        processingDate: DateTime.parse(json['processing_date'] ?? DateTime.now().toIso8601String()),
      );
    } catch (e) {
       throw FormatException('Failed to parse Client: $e');
    }
  }
}