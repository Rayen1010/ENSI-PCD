import 'package:flutter/material.dart';

class CategoryModel {
  String name;
  String iconPath;
  Color boxColor;

  CategoryModel({
    required this.name,
    required this.iconPath,
    required this.boxColor,
  });
  
  static List<CategoryModel> getCategories1() {
    List<CategoryModel> categories = [];
    
    categories.add(
      CategoryModel(
        name: 'Groceries',
        iconPath: 'assets/icons/new/grocery.jpg',
        boxColor: Color(0xff9DCEFF)
      )
    );

    categories.add(
      CategoryModel(
        name: 'Clothing & Fashion',
        iconPath: 'assets/icons/new/clothing.jpg',
        boxColor: Colors.blueGrey
      )
    );

    categories.add(
      CategoryModel(
        name: 'Home & Furniture',
        iconPath: 'assets/icons/new/home.jpg',
        boxColor: Color(0xff9DCEFF)
      )
    );

    categories.add(
      CategoryModel(
        name: 'Food & Beverages',
        iconPath: 'assets/icons/new/food.jpg',
        boxColor: Colors.blueGrey
      )
    );
    return categories;
  }

  static List<CategoryModel> getCategories2() {
    List<CategoryModel> categories = [];
    
    categories.add(
      CategoryModel(
        name: 'Electronics',
        iconPath: 'assets/icons/new/electronics.jpg',
        boxColor: Color(0xff9DCEFF)
      )
    );

    categories.add(
      CategoryModel(
        name: 'Books & Stationery',
        iconPath: 'assets/icons/new/books.jpg',
        boxColor: Colors.blueGrey
      )
    );

    categories.add(
      CategoryModel(
        name: 'Sports & Fitness',
        iconPath: 'assets/icons/new/sports.jpg',
        boxColor: Color(0xff9DCEFF)
      )
    );

    categories.add(
      CategoryModel(
        name: 'Toys & Games',
        iconPath: 'assets/icons/new/toys.jpg',
        boxColor: Colors.blueGrey
      )
    );
    

    return categories;
  }
}