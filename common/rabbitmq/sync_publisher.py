import json
import pika

class SyncPublisher:
    def __init__(self, channel, exchange):
        self.channel = channel
        self.exchange = exchange

    def publish(self, routing_key, exchange_name, data, mandatory=False):
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
            mandatory=mandatory
        )