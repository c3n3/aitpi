_consumers = {}

def reset():
    """Clears all subscriptions
    """
    global _consumers
    _consumers = {}

def addConsumer(ids, consumer, priority=0):
    """Adds a new consumer

    Args:
        ids (list<int>): List of all IDs to recieve.
        consumer (Consumer): The consumer to link
        priority (int): Higher is more priority.
    """
    for i in ids:
        if (not i in _consumers):
            _consumers[i] = []
        inserted = False
        for x in range(len(_consumers[i])):
            if priority > _consumers[i][x][1]:
                _consumers[i].insert(x, (consumer, priority))
                inserted = True
                break
        if not inserted:
            _consumers[i].append((consumer, priority))

def sendMessage(msg):
    """Sends a message

    Args:
        msg (Message): The message to send
    """
    sent = False
    if (msg.msgId in _consumers.keys()):
        for c in _consumers[msg.msgId]:
            # If there is no consume function, assume callable
            if 'consume' in dir(c[0]):
                c[0].consume(msg)
            else:
                c[0](msg)
            sent = True
    return sent

def send(msg):
    sendMessage(msg)