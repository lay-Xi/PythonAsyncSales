import asyncio
from inventory import Inventory


def display_catalogue(catalogue):
    burgers = catalogue["Burgers"]
    sides = catalogue["Sides"]
    drinks = catalogue["Drinks"]

    print("--------- Burgers -----------\n")
    for burger in burgers:
        item_id = burger["id"]
        name = burger["name"]
        price = burger["price"]
        print(f"{item_id}. {name} ${price}")

    print("\n---------- Sides ------------")
    for side in sides:
        sizes = sides[side]

        print(f"\n{side}")
        for size in sizes:
            item_id = size["id"]
            size_name = size["size"]
            price = size["price"]
            print(f"{item_id}. {size_name} ${price}")

    print("\n---------- Drinks ------------")
    for beverage in drinks:
        sizes = drinks[beverage]

        print(f"\n{beverage}")
        for size in sizes:
            item_id = size["id"]
            size_name = size["size"]
            price = size["price"]
            print(f"{item_id}. {size_name} ${price}")

    print("\n------------------------------\n")

async def get_order(number_of_items):
    order = []
    
    print("Please enter the number of items that you would like to add to your order. Enter q to complete your order.")

    item = ""

    while item != "q":
        try:
            item = input("Enter an item number: ")

            if (item == "q"):
                break

            item = int(item)

            if (item < 0):
                raise ValueError
            elif (item > number_of_items):
                print(f"Please enter a number below {number_of_items + 1}")
            else:
                order.append(item)
        except ValueError:
            print("Please enter a valid number.")
    
    print("Placing order...")

    return order

async def main():
    print("Welcome to the ProgrammingExpert Burger Bar!")
    print("Loading catalogue...")

    inventory = Inventory()
    number_of_items = await inventory.get_number_of_items()

    display_catalogue(inventory.catalogue)

    order = await get_order(number_of_items)

if __name__ == "__main__":
    asyncio.run(main())
