import ccxt

print(ccxt.exchanges)

bittrex = ccxt.bittrex()
load_markets = bittrex.load_markets()

markets = bittrex.markets
print(markets)

symbols = bittrex.symbols
print(symbols)

symbols_qty = len(symbols)
print(symbols_qty)

symbols_active = []
for sym in range(symbols_qty):
    if markets[symbols[sym]]['active']==True:
        symbols_active.append(symbols[sym])
        print(symbols[sym], markets[symbols[sym]]['active'])
print(symbols_active)

symbols_active_qty = len(symbols_active)
print(symbols_active_qty)

markets_active = []
for sym in range(symbols_active_qty):
    print(markets[symbols_active[sym]])

