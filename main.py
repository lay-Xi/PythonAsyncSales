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

async def create_stock_list(item, inventory):
    stock_dict = {}

    stock_dict[item] = stock_dict.get(item, 0) + await inventory.get_stock(item)

    return stock_dict

async def check_stock(order, inventory):
    tasks = []

    stock_dict = {}

    for item in order.keys():
        tasks.append(asyncio.create_task(create_stock_list(item, inventory)))

    results = await asyncio.gather(*tasks)

    for result in results:
        stock_dict.update(result)

    for item, amount_ordered in order.items():
        amount_left = stock_dict[item] - amount_ordered
        
        if (amount_left < 0):
            for _ in range(amount_left, 0):
                print(f"Unfortunately item number {item} is out of stock and has been removed from your order. Sorry!")
                order[item] -= 1
        else:
            stock_dict[item] = amount_ordered

    print()

    return (order, stock_dict)

def get_order(number_of_items):
    order = {}
    
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
                order[item] = order.get(item, 0) + 1
        except ValueError:
            print("Please enter a valid number.")
    
    print("Placing order...")

    return order

async def create_combo(order, inventory):
    combo_burger = {}
    combo_side = {}
    combo_drink = {}

    tasks = []

    for item, amount in order.items():
        for _ in range(amount):
            tasks.append(asyncio.create_task(inventory.get_item(item)))

    items_list = await asyncio.gather(*tasks)

    burgers = list(filter(lambda item: item["category"] == "Burgers", items_list))
    sides = list(filter(lambda item: item["category"] == "Sides", items_list))
    drinks = list(filter(lambda item: item["category"] == "Drinks", items_list))
    
    sub_total = 0

    print()
    print("Here is a summary of your order:")
    print()

    if len(items_list) >= 3:
        while len(burgers) > 0 and len(sides) > 0 and len(drinks) > 0:
            burgers.sort(key=lambda item: item["price"], reverse=True)
            sides.sort(key=lambda item: item["price"], reverse=True)
            drinks.sort(key=lambda item: item["price"], reverse=True)

            combo_burger = burgers.pop(0)
            combo_side = sides.pop(0)
            combo_drink = drinks.pop(0)

            combo_price = round((combo_burger["price"] + combo_side["price"] + combo_drink["price"]) * 0.85, 2)

            print(f"${combo_price:.2f} Burger Combo")
            print(f" {combo_burger['name']}")
            print(f" {combo_side['size']} {combo_side['subcategory']}")
            print(f" {combo_drink['size']} {combo_drink['subcategory']}")

            sub_total += combo_price
    
    while len(burgers) > 0:
        burger = burgers.pop()

        print(f"${burger['price']} {burger['name']}")
        sub_total += burger["price"]

    while len(sides) > 0:
        side = sides.pop()

        print(f"${side['price']} {side['size']} {side['subcategory']}")
        sub_total += side["price"]

    while len(drinks) > 0:
        drink = drinks.pop()

        print(f"${drink['price']} {drink['size']} {drink['subcategory']}")
        sub_total += drink["price"]

    print()

    return sub_total

def calculate_tax(subtotal):
    tax = round(subtotal * 0.05, 2)
    total = subtotal + tax

    print(f"Subtotal: ${subtotal:.2f}")
    print(f"Tax: ${tax:.2f}")
    print(f"Total: ${total:.2f}")

    return total

async def update_stock(stock_change_amount, inventory):
    tasks = []

    for item, amount in stock_change_amount.items():
        for _ in range(amount):
            tasks.append(asyncio.create_task(inventory.decrement_stock(item)))

    await asyncio.gather(*tasks)

async def confirm_order(order, inventory, new_stock_amount):
    if len(order) > 0:
        subtotal = await create_combo(order, inventory)
        total = calculate_tax(subtotal)

        confirm_purchase = input(f"Would you like to purchase this order for ${total:.2f} (yes/no)? ")

        if (confirm_purchase == "yes"):
            await update_stock(new_stock_amount, inventory)
            print("Thank you for your order!")
        else:
            print("No problem, please come again!")

async def main():
    print("Welcome to the ProgrammingExpert Burger Bar!")
    print("Loading catalogue...")

    inventory = Inventory()
    number_of_items = await inventory.get_number_of_items()

    display_catalogue(inventory.catalogue)

    while True: 
        order = get_order(number_of_items)
        order, stock_change_amount = await check_stock(order, inventory)
        await confirm_order(order, inventory, stock_change_amount)
        order_again = input("Would you like to make another order (yes/no)? ")

        if order_again == "no":
            break
    
    print("Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
