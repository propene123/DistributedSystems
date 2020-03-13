import sys
import Pyro4
import Pyro4.errors


try:
    FRONTEND = Pyro4.Proxy('PYRONAME:justHungry.frontend')
except Pyro4.errors.PyroError:
    sys.exit('Could not connect to frontend server')


def select_store():
    stores = FRONTEND.getStores()
    print('Please select one of the stores, or type quit to go back')
    if stores == ['ERROR']:
        print('Cannot get stores from server')
        return -1
    for count, store in enumerate(stores, 1):
        print(count, store, sep='. ')
    while True:
        resp = input()
        try:
            if 0 < int(resp) <= len(stores):
                return int(resp)
        except ValueError:
            pass
        if resp.lower() == 'quit':
            return -1
        print('That was not a valid option please try again')


def select_item(store):
    items = FRONTEND.getItems(store)
    print(f'Thank you for selecting {FRONTEND.getStoreName(store-1)}.' +
          f' Please select an item to order or type quit to go back')
    if items == ['ERROR']:
        print('Cannot get items from server')
        return -1
    for count, item in enumerate(items, 1):
        print(f'{count}. {item[0]}\t£{item[1]}\tstock:{item[2]}')
    while True:
        resp = input()
        try:
            if 0 < int(resp) <= len(items):
                return int(resp)
        except ValueError:
            pass
        if resp.lower() == 'quit':
            return -1
        print('That was not a valid option please try again')


def select_quantity(store, order_item):
    item = FRONTEND.getItem(store, order_item)
    print(f'Thank you for selecting ' +
          f'{FRONTEND.getItemName(store, order_item)}.' +
          f' Please enter how much you would like to order or ' +
          f'type quit to go back')
    if not item:
        print('Cannot get item from server')
        return -1
    current_stock = item[2]
    while True:
        resp = input()
        try:
            if 0 < int(resp) <= current_stock:
                return int(resp)
        except ValueError:
            pass
        if resp.lower() == 'quit':
            return -1
        print('That is not a valid stock option please try again')


def place_order(store, order_item, quant):
    return FRONTEND.placeOrder(store, order_item, quant)


def submit_postcode():
    print('Please enter a postcode for the intended delivery location')
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
    return FRONTEND.finaliseOrder(store, order_item, quant, address)


def flow_postcode(store, order_item, quant):
    while True:
        address = submit_postcode()  # add api failed option
        if not address:
            print('Invalid postcode entered')
            return False
        print(f'Please enter building number for location:\n{address}')
        number = house_number()
        print(f'Please enter street name for location:\n{address}')
        street = street_name()
        address = f'{number} {street}\n{address}'
        correct_address = verify_address(address)  # add incorrect option
        if not correct_address:
            continue
        confirm = confirm_order(store, order_item,
                                quant, address)  # add no option
        if not confirm:
            print('You may redo your order')
            return False
        success = finalise_order(store, order_item,
                                 quant, address)  # add failed option
        print('Your order will now be finalised')
        if not success:
            print('There was an error placing your order please try again')
            return False
        print('Your order has been successfully placed. Your goods will arrive' +
              ' neither early nor late but exactly when the mean to')
        return True


def flow_quant(store, order_item):
    while True:
        quant = select_quantity(store, order_item)  # add back option
        if quant == -1:
            return False
        print('Your order will now be placed')
        success = place_order(store, order_item, quant)
        if not success:
            print('There was a problem with your order, you may try again')
            continue
        res = flow_postcode(store, order_item, quant)
        if not res:
            continue
        return True


def flow_order_item(store):
    while True:
        order_item = select_item(store)  # add back option
        if order_item == -1:
            return False
        res = flow_quant(store, order_item-1)
        if not res:
            continue
        return True


def flow_store(store):
    while True:
        res = flow_order_item(store)
        if not res:
            return False
        return True



def order():
    while True:
        store = select_store()
        if store == -1:
            break
        res = flow_store(store-1)
        if not res:
            continue
        break



def view():
    pass


def main():
    print('Welcome to the Just Hungry store. Here you can order various' +
          ' foodstuffs to any location you want.')
    while True:
        print('Would you like to:\n1. Make an order\n2. View your orders\n3. Quit')
        answer = input()
        if answer == '1':
            order()
        elif answer == '2':
            view()
        elif answer.lower() in ['quit', '3']:
            print('Thank you for doing business with us today')
            break
        else:
            print('Not a valid option. Try again')
    # Loopify


try:
    main()
except Pyro4.errors.PyroError:
    sys.exit('Cannot connect to the frontend server. Exiting client')
