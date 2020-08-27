from confluent_kafka import Producer
import sys
import time

# kafka
props = {'bootstrap.servers': 'IP:9092'}
producer = Producer(props)
topicName = 'newUser'

try:
    keyy = 'newUser'
    # kafka_msg = 'userID|sex|Birth|Height|Weight|target' #格式麻煩照這樣
    # kafka_msg = 'M000000099|1|19831014|172|89|tg01'
    kafka_msg = 'M000000069|0|19700514|159|86|tg01'
    producer.produce(topicName, key=keyy, value=kafka_msg)
    producer.flush()
    print(f' ==> message sent to kafka : {kafka_msg}')
except BufferError:
    sys.stderr.write('%% Local producer queue is full ({} messages awaiting delivery): try again\n'
                     .format(len(producer)))
except Exception as e:
    print(e)
producer.flush()
