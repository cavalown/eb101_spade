from confluent_kafka import Producer
import sys
import time

# kafka
props = {'bootstrap.servers': 'IP:9092'}
producer = Producer(props)
topicName = 'dailyEat'

try:
    kafka_msg = 'M10000001' #userID
    producer.produce(topicName, value=kafka_msg)
    producer.flush()
    print(f' ==> message sent to kafka : {kafka_msg}')
except BufferError:
    sys.stderr.write('%% Local producer queue is full ({} messages awaiting delivery): try again\n'
                     .format(len(producer)))
except Exception as e:
    print(e)
producer.flush()
