"""
Example Python EMDR client.
"""
import zlib
import zmq
# You can substitute the stdlib's json module, if that suits your fancy
import json

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
        print market_data

if __name__ == '__main__':
    main()