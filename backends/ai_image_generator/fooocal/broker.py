import pika

class Rabbit:
    def __init__(self, hostname: str, username: str, password: str):
        self.credentials = pika.PlainCredentials(username, password)
        self.conneciton_parameters = pika.ConnectionParameters(
            host=hostname,
            credentials=self.credentials,
            heartbeat=120
        )
        self.connection = pika.BlockingConnection(self.conneciton_parameters)
        self.channel = self.connection.channel()

    def consume(self, queue_name: str, callback: callable):
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=False
        )
        self.channel.start_consuming()