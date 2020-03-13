import sys
import Pyro4
import Pyro4.errors


CLIENT_ID = 0

# Try to connect to frontend
try:
    FRONTEND = Pyro4.Proxy('PYRONAME:justHungry.frontend')
except Pyro4.errors.PyroError:
    sys.exit('Could not connect to frontend server')


def select_store():
    # Query frontend for available sotres
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
    # Query frontend for items in a particular stall
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
    # Get sepcific info about an item
    item = FRONTEND.getItem(store, order_item)
    print(f'Thank you for selecting ' +
          f'{FRONTEND.getItemName(store, order_item)}.' +
          f' Please enter how much you would like to order or ' +
          f'type quit to go back')
    if not item:
        print('Cannot get item from server')
        return -1
    current_stock = item[2]
    if current_stock == 0:
        print('That item is currently unavailable')
        return -1
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
    # Ask server to validate a draft order
    return FRONTEND.placeOrder(store, order_item, quant)


def submit_postcode():
    # Get better location info from server about the given postcode
    print('Please enter a postcode for the intended delivery location')
    postcode = input()
    return FRONTEND.getAddress(postcode)


def house_number():
    # Query user for house_number
    while True:
        resp = input()
        try:
            num = int(resp)
            return num
        except ValueError:
            print('That is not a number, please try again')


def street_name():
    # query user for street name
    return input()


def verify_address(address):
    # ask user if they entered the correct address
    print(f'You entered:\n{address}\n\nIs this the correct address y/n')
    while True:
        response = input()
        if response.lower() == 'y':
            return True
        if response.lower() == 'n':
            return False
        print('That was not a correct response to the question enter y or n')


def confirm_order(store, order_item, quant, address):
    # Get item specific info from server
    item = FRONTEND.getItem(store, order_item)
    total_cost = item[1] * quant
    # ask user to confirm there order
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
    # pass order to server to be processed
    return FRONTEND.finaliseOrder(store, order_item, quant, address, CLIENT_ID)


def flow_postcode(store, order_item, quant):
    while True:
        address = submit_postcode()
        if not address:
            print('Invalid postcode entered')
            return False
        print(f'Please enter building number for location:\n{address}')
        number = house_number()
        print(f'Please enter street name for location:\n{address}')
        street = street_name()
        address = f'{number} {street}\n{address}'
        correct_address = verify_address(address)
        if not correct_address:
            continue
        confirm = confirm_order(store, order_item,
                                quant, address)
        if not confirm:
            print('You may redo your order')
            return False
        success = finalise_order(store, order_item,
                                 quant, address)
        print('Your order will now be finalised')
        if not success:
            print('There was an error placing your order please try again')
            return False
        print('Your order has been successfully placed. Your goods will arrive' +
              ' neither early nor late but exactly when the mean to')
        return True


def flow_quant(store, order_item):
    while True:
        quant = select_quantity(store, order_item)
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
        order_item = select_item(store) 
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
    orders = FRONTEND.getOrders(CLIENT_ID)
    if orders == ['ERROR']:
        print('There was an error retrieving your orders. Please try again')
    print('Here are your orders:')
    for data in orders:
        print(f'Store: {data[0]}')
        print(f'Item: {data[1]}')
        print(f'Quantity: {data[2]}')
        print(f'Total Cost: {data[3]}')
        print('Address:')
        print(data[4])
        print('##############################################################################')


def main():
    global CLIENT_ID
    CLIENT_ID = FRONTEND.getClientID()
    if not CLIENT_ID:
        sys.exit('Cannot connect to the Just Hungry store. Exiting client')
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


# Catch any communication errors
try:
    main()
except Pyro4.errors.PyroError as e:
    print(e)
    sys.exit('Cannot connect to the Just Hungry Store. Exiting client')
