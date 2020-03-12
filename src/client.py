import Pyro4


FRONTEND = Pyro4.Proxy('PYRONAME:justHungry.frontend')


def select_store():
    stores = FRONTEND.getStores()
    for count, store in enumerate(stores, 1):
        print(count, store, sep='. ')
    resp = input()
    while True:
        if int(resp) < len(stores):
            return int(resp)
        if resp.lower == 'quit':
            return -1
        print('That was not a valid option please try again')


def select_item(store):
    items = FRONTEND.getItems(store)
    for count, item in enumerate(items, 1):
        print(f'{count}. {item[0]}\t£{item[1]}\tstock:{item[2]}')
    resp = input()
    while True:
        if int(resp) < len(items):
            return int(resp)
        if resp.lower == 'quit':
            return -1
        print('That was not a valid option please try again')


def select_quantity(store, order_item):
    item = FRONTEND.getItem(store, order_item)
    current_stock = item[2]
    resp = input()
    while True:
        if 0 <= int(resp) <= current_stock:
            return int(resp)
        if resp.lower == 'quit':
            return -1
        print('That is not a valid stock option please try again')


def place_order(store, order_item, quant):
    return FRONTEND.placeOrder(store, order_item, quant)


def submit_postcode():
    postcode = input()
    return FRONTEND.getAddress(postcode)


def verify_address(address):
    print(f'You entered:\n{address}\n\nIs this the correct address y/n')
    response = input()
    while True:
        if response.lower == 'y':
            return True
        if response.lower == 'n':
            return False
        print('That was not a correct response to the question enter y or n')


def confirm_order(store, order_item, quant, address):
    item = FRONTEND.getItem(store, order_item)
    total_cost = item[1] * quant
    print(f'You are ordering {quant} {item[0]} from ' +
          f'{FRONTEND.getStoreName(store)} for a total cost of ' +
          f'£{total_cost} and having it delivered to:\n{address}\n\n' +
          f' is this correct y/n')
    response = input()
    while True:
        if response.lower == 'y':
            return True
        if response.lower == 'n':
            return False
        print('That was not a correct response to the question enter y or n')


def finalise_order(store, order_item, quant, address):
    return FRONTEND.finalise_order(store, order_item, quant, address)


def main():
    print('Welcome to the Just Hungry store. Here you can order various' +
          ' foodstuffs to any location you want.')
    print('Please select one of the stores, or type quit to exit')
    store = select_store()  # add back option
    print(f'Thank you for selecting {FRONTEND.getStoreName(store-1)}.' +
          f' Please select an item to order or type quit to go back')
    order_item = select_item(store-1)  # add back option
    print(f'Thank you for selecting ' +
          f'{FRONTEND.getItemName(store-1, order_item-1)}.' +
          f' Please enter how much you would like to order or ' +
          f'type quit to go back')
    quant = select_quantity(store-1, order_item-1)  # add back option

    print('Your order will now be placed')
    # add order failed option
    order = place_order(store-1, order_item-1, quant)
    print('Please enter a postcode for the intended delivery address')
    address = submit_postcode()  # add api failed option
    correct_address = verify_address(address)  # add incorrect option
    confirm = confirm_order(store-1, order_item-1,
                            quant, address)  # add no option
    print('Your order will now be finalised')
    success = finalise_order(store-1, order_item-1,
                             quant, address)  # add failed option
    print('Your order has been successfully placed. Your goods will arrive' +
          ' neither early nor late but exactly when the mean to')
    # Loopify
