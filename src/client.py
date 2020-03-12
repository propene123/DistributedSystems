import sys
import Pyro4


FRONTEND = Pyro4.Proxy('PYRONAME:justHungry.frontend')


def select_store():
    stores = FRONTEND.getStores()
    for count, store in enumerate(stores, 1):
        print(count, store, sep='. ')
    while True:
        resp = input()
        try:
            if int(resp) < len(stores):
                return int(resp)
        except ValueError:
            pass
        if resp.lower() == 'quit':
            return -1
        print('That was not a valid option please try again')


def select_item(store):
    items = FRONTEND.getItems(store)
    for count, item in enumerate(items, 1):
        print(f'{count}. {item[0]}\t£{item[1]}\tstock:{item[2]}')
    while True:
        resp = input()
        try:
            if int(resp) < len(items):
                return int(resp)
        except ValueError:
            pass
        if resp.lower() == 'quit':
            return -1
        print('That was not a valid option please try again')


def select_quantity(store, order_item):
    item = FRONTEND.getItem(store, order_item)
    current_stock = item[2]
    while True:
        resp = input()
        try:
            if 0 <= int(resp) <= current_stock:
                return int(resp)
        except ValueError:
            pass
        if resp.lower() == 'quit':
            return -1
        print('That is not a valid stock option please try again')


def place_order(store, order_item, quant):
    return FRONTEND.placeOrder(store, order_item, quant)


def submit_postcode():
    postcode = input()
    return FRONTEND.getAddress(postcode)


def house_number():
    while True:
        resp = input()
        try:
            num = int(resp)
            return num
        except ValueError:
            print('That is not a number, please try again')


def street_name():
    return input()


def verify_address(address):
    print(f'You entered:\n{address}\n\nIs this the correct address y/n')
    while True:
        response = input()
        if response.lower() == 'y':
            return True
        if response.lower() == 'n':
            return False
        print('That was not a correct response to the question enter y or n')


def confirm_order(store, order_item, quant, address):
    item = FRONTEND.getItem(store, order_item)
    total_cost = item[1] * quant
    print(f'You are ordering {quant} {item[0]} from ' +
          f'{FRONTEND.getStoreName(store)} for a total cost of ' +
          f'£{total_cost} and having it delivered to:\n{address}\n\n' +
          f' is this correct y/n')
    while True:
        response = input()
        if response.lower() == 'y':
            return True
        if response.lower() == 'n':
            return False
        print('That was not a correct response to the question enter y or n')


def finalise_order(store, order_item, quant, address):
    return FRONTEND.finalise_order(store, order_item, quant, address)


def flow_postcode(store, order_item, quant):
    address = submit_postcode()  # add api failed option
    print(f'Please enter building number for location:\n{address}')
    number = house_number()
    print(f'Please enter street name for location:\n{address}')
    street = street_name()
    address = number + '\n' + street + '\n' + address
    correct_address = verify_address(address)  # add incorrect option
    if not correct_address:
        return correct_address
    confirm = confirm_order(store, order_item,
                            quant, address)  # add no option
    if not confirm:
        return confirm
    print('Your order will now be finalised')
    success = finalise_order(store, order_item,
                             quant, address)  # add failed option
    if not success:
        return False
    print('Your order has been successfully placed. Your goods will arrive' +
          ' neither early nor late but exactly when the mean to')
    return True


def flow_quant(store, order_item):
    quant = select_quantity(store, order_item)  # add back option
    if quant == -1:
        return False
    print('Your order will now be placed')
    order = place_order(store, order_item, quant)
    if not order:
        return order
    print('Please enter a postcode for the intended delivery location')
    return flow_postcode(store, order_item, quant)


def flow_order_item(store):
    order_item = select_item(store-1)  # add back option
    if order_item == -1:
        return False
    print(f'Thank you for selecting ' +
          f'{FRONTEND.getItemName(store-1, order_item-1)}.' +
          f' Please enter how much you would like to order or ' +
          f'type quit to go back')
    return flow_quant(store, order_item-1)


def main():
    print('Welcome to the Just Hungry store. Here you can order various' +
          ' foodstuffs to any location you want.')
    print('Please select one of the stores, or type quit to exit')
    store = select_store()
    if store == -1:
        sys.exit('Thank you for doing business with us today')
    print(f'Thank you for selecting {FRONTEND.getStoreName(store-1)}.' +
          f' Please select an item to order or type quit to go back')
    # Loopify


main()
