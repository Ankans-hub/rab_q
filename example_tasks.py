import time
from rab_q import Messaging

def main():
    # Initialize the SDK with the mock API key
    mq = Messaging(api_key="ank@8250255103#sark_$")
    
    # 1. Register a task
    @mq.task("send_invoice")
    def handle_invoice(order_id, amount):
        print(f"[{time.strftime('%X')}] Sending invoice for Order {order_id} (Amount: ${amount})")

    # 2. Start consuming tasks in the background
    print(f"[{time.strftime('%X')}] Starting task worker...")
    mq.consume_tasks(queue="task_queue")
    
    # 3. Publish Immediate Tasks
    print(f"[{time.strftime('%X')}] Publishing immediate tasks...")
    for i in range(3):
        mq.send_task("send_invoice", queue="task_queue", args=[i, 100 + i * 10])
        
    # 4. Publish Delayed Tasks
    print(f"[{time.strftime('%X')}] Publishing a task with 3-second delay...")
    mq.send_task("send_invoice", queue="task_queue", args=[999, 500], delay_ms=3000)
        
    print(f"[{time.strftime('%X')}] Sleeping to allow consumption (wait for the delayed task)...")
    time.sleep(5)
    
    mq.shutdown()

if __name__ == "__main__":
    main()
