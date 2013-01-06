"""
Example Python EMDR client.
"""
import zlib
import zmq
# You can substitute the stdlib's json module, if that suits your fancy
import json
from datetime import datetime
import sys
from pprint import pprint

data = {}
uniqueOrders = 0

def processOrdersPacket(market_data):
    start = datetime.now()
    columns = market_data['columns']
    global uniqueOrders

    for rowset in market_data['rowsets']:
        regionID = rowset['regionID']
        typeID = rowset['typeID']
        generatedTime = rowset['generatedAt']

        if regionID <> 10000002:
            continue

        if typeID not in data.keys():
            data[typeID] = {}

        for row in rowset['rows']:
            row = dict(zip(columns, row))
            orderID = row['orderID']
            typeIDDict = data[typeID]

            if orderID not in typeIDDict.keys():
                typeIDDict[orderID] = row
                typeIDDict[orderID]['generatedAt'] = generatedTime
                uniqueOrders += 1
            elif typeIDDict[orderID]['generatedAt'] < generatedTime:
                print 'Updating entry from: ', typeIDDict[orderID], 'to', row
                typeIDDict[orderID] = row
                typeIDDict[orderID]['generatedAt'] = generatedTime
    print 'Hit Data!', (datetime.now() - start), len(data.keys()), uniqueOrders
    #print data

def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    # Connect to the first publicly available relay.
    subscriber.connect('tcp://relay-us-central-1.eve-emdr.com:8050')
    # Disable filtering.
    subscriber.setsockopt(zmq.SUBSCRIBE, "")

    print 'Relay started, waiting for data...'
    while True:
        # Receive raw market JSON strings.
        market_json = zlib.decompress(subscriber.recv())
        # Un-serialize the JSON data to a Python dict.
        market_data = json.loads(market_json)

        # Dump the market data to stdout. Or, you know, do more fun
        # things here.
        #print market_data

        if market_data['resultType'] == 'orders':
            processOrdersPacket(market_data)
        else:
            #print market_data
            pass

if __name__ == '__main__':
    main()