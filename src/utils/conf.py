import os
dir_path = os.path.dirname(os.path.realpath(__file__))

fixture_path = os.path.join(dir_path, "../../fixtures")

party = ['manufacturer', 'operator', 'supplier', 'location']

share = {'operator': 0.7, 'manufacturer': 0.1, 'supplier': 0.1, 'location': 0.1}

item_names = ["Snickers", "Peanut M&M’s", "Twix", "Butterfinger", 
"Milk Duds", "Milky Way", "Baby Ruth", "Doritos", "Cheetos", 
"Lay's potato chips", "Oreos", "Grandma’s Cookies", "Rice Crispy Treats", 
"Cheez-It's", "Granola Bars", "Mountain Dew", "Dr. Pepper", "Pepsi", 
"Coke", "Sprite", "Diet Coke", "Diet Pepsi", "Gatorade"]

