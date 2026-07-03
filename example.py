import time
from rab_q import Messaging

def handle_invoice(data):
    print(f"Received invoice: {data}")

def main():
    # Initialize the SDK with the mock API key
    mq = Messaging(api_key="ank@8250255103#sark_$")
    
    # Start consuming in the background
    mq.consume("invoice", callback=handle_invoice)
    
    # Publish some messages
    for i in range(5):
        mq.publish("invoice", {"order_id": i, "amount": 100 + i * 10})
        time.sleep(1)
        
    print("Sleeping to allow consumption...")
    time.sleep(2)
    mq.shutdown()

if __name__ == "__main__":
    main()
