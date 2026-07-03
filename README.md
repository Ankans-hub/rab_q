# Enterprise-Grade Messaging SDK (rab_q)

A commercial, enterprise-grade Messaging SDK that enables developers to integrate RabbitMQ with only a few lines of code.

## Features (v1.0)
* Zero configuration defaults
* Enterprise reliability
* Retry mechanism
* Delay queue
* Dead Letter Queue

## Getting Started

```python
from rab_q import Messaging

mq = Messaging(api_key="ank@8250255103#sark_$")

mq.publish(
    queue="invoice",
    data={"order_id": 12345}
)
```
