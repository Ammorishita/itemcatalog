from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import FoodGroup, Base, FoodItem, User

engine = create_engine('sqlite:///nutritioncatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items in Grains food group
Grains = FoodGroup(user_id=1, name="Grains")

session.add(Grains)
session.commit()

foodItem1 = FoodItem(user_id=1, name="Wheat Bread",
                     carbs="25", sugars="0", fats="0", calories="120", foodGroup=Grains)

session.add(foodItem1)
session.commit()

foodItem2 = FoodItem(user_id=1, name="White Rice",
                     carbs="80", sugars="0", fats="1", calories="360", foodGroup=Grains)

session.add(foodItem2)
session.commit()

foodItem3 = FoodItem(user_id=1, name="Tortilla",
                     carbs="23", sugars="0", fats="4", calories="140", foodGroup=Grains)

session.add(foodItem3)
session.commit()

# Items in Meats and Poultry food group
Meats = FoodGroup(user_id=1, name="Meats and Poultry")

session.add(Meats)
session.commit()

foodItem1 = FoodItem(user_id=1, name="Beef",
                     carbs="0", sugars="0", fats="2.69", calories="117", foodGroup=Meats)

session.add(foodItem1)
session.commit()

foodItem2 = FoodItem(user_id=1, name="Steak",
                     carbs="0", sugars="0", fats="6", calories="133", foodGroup=Meats)

session.add(foodItem2)
session.commit()

foodItem3 = FoodItem(user_id=1, name="Chicken",
                     carbs="0", sugars="0", fats="8", calories="143", foodGroup=Meats)

session.add(foodItem3)
session.commit()

# Items in Milks and Cheese food group
Milks = FoodGroup(user_id=1, name="Milks and Cheese")

session.add(Milks)
session.commit()

foodItem1 = FoodItem(user_id=1, name="Cheddar Cheese",
                     carbs="1", sugars="0", fats="9", calories="110", foodGroup=Milks)

session.add(foodItem1)
session.commit()

foodItem2 = FoodItem(user_id=1, name="Yogurt",
                     carbs="27", sugars="23", fats="2", calories="150", foodGroup=Milks)

session.add(foodItem2)
session.commit()

foodItem3 = FoodItem(user_id=1, name="Nonfat Milk",
                     carbs="12", sugars="12", fats="0", calories="91", foodGroup=Milks)

session.add(foodItem3)
session.commit()

# Items in Fruits food group
Fruits = FoodGroup(user_id=1, name="Fruits")

session.add(Fruits)
session.commit()

foodItem1 = FoodItem(user_id=1, name="Fuji Apple",
                     carbs="15", sugars="12", fats="0", calories="84", foodGroup=Fruits)

session.add(foodItem1)
session.commit()

foodItem2 = FoodItem(user_id=1, name="Orange",
                     carbs="13", sugars="9", fats="0", calories="49", foodGroup=Fruits)

session.add(foodItem2)
session.commit()

foodItem3 = FoodItem(user_id=1, name="Pineapple",
                     carbs="13", sugars="10", fats="0", calories="50", foodGroup=Fruits)

session.add(foodItem3)
session.commit()

# Items in Vegetables food group
Vegetables = FoodGroup(user_id=1, name="Vegetables")

session.add(Vegetables)
session.commit()

foodItem1 = FoodItem(user_id=1, name="Broccoli",
                     carbs="7", sugars="2", fats="0", calories="34", foodGroup=Vegetables)

session.add(foodItem1)
session.commit()

foodItem2 = FoodItem(user_id=1, name="Carrots",
                     carbs="10", sugars="5", fats="0", calories="41", foodGroup=Vegetables)

session.add(foodItem2)
session.commit()

foodItem3 = FoodItem(user_id=1, name="Peas",
                     carbs="14", sugars="6", fats="0", calories="81", foodGroup=Vegetables)

session.add(foodItem3)
session.commit()




print "added food items!"