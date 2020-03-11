import Pyro4


frontend = Pyro4.Proxy('PYRONAME:justHungry.frontend')


def select_store():
    stores = frontend.getStores()
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
    items = frontend.getItems(store)
    for count, item in enumerate(items, 1):
        print(f'{count}. {item[0]}\t{item[1]}\tstock:{item[2]}')
    resp = input()
    while True:
        if int(resp) < len(items):
            return int(resp)
        if resp.lower == 'quit':
            return -1
        print('That was not a valid option please try again')


def main():
    print('Welcome to the Just Hungry store. Here you can order various' +
          ' foodstuffs to any location you want.')
    print('Please select one of the stores, or type quit to go back')
    store = select_store()  # add back option
    print(f'Thank you for selecting {frontend.getStoreName(store)}.' +
          f' Please select an item to order or type quit to go back')
    order_item = select_item(store)  # add back option
    print(f'Thank you for selecting ' +
          f'{frontend.getItemName(store, order_item)}.' +
          f' Please enter how much you would like to order')
