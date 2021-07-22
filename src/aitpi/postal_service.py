from aitpi.message import Message
from aitpi.printer import Printer

class PostalService():
    """Big class handles sending messages to 'subscriptions' via message IDs

       Has three types of subscriptions currently:
           - Global -> Everything is always sent and consumed whenever
           - PASSIVE -> Everything is always sent to you, but instead of
                        consuming right aways, is stored in a queue
           - ACTIVE -> Things are sent and consumed only when you are set as 'active'
    """
    GLOBAL_SUBSCRIPTION = 0
    PASSIVE_SUBSCRIPTION = 1
    ACTIVE_SUBSCRIPTION = 2

    _mainNode = None
    _instantIds = []
    _globalIdToConsumers = {}
    _passiveIdToConsumers = {}
    _activeIdToConsumers = {}

    @staticmethod
    def reset():
        """Clears all subscriptions
        """
        _instantIds = []
        PostalService._mainNode = None
        PostalService._ = None
        PostalService._globalIdToConsumers = {}
        PostalService._passiveIdToConsumers = {}

    @staticmethod
    def setInstantConsumer(ids, consumer):
        """Sets an instant consumer.

           The instant consumer always gets the messages first when set, and blocks all other subscriptions from receiving it.
           This is true no matter the subscription. There can only be one instant subscriber at any given point.

        Args:
            ids (list<int>): A list of all message IDs the consumer will consume
            consumer (Consumer): The instant consumer
        """
        PostalService._mainNode = consumer
        PostalService._instantIds = ids

    @staticmethod
    def addConsumer(ids, subscriptionType, consumer):
        """Adds a new consumer

        Args:
            ids (list<int>): List of all IDs to recieve.
            subscriptionType (int): The type of subscription.
            consumer (Consumer): The consumer to link
        """
        if (subscriptionType == PostalService.GLOBAL_SUBSCRIPTION):
            for i in ids:
                if (not i in PostalService._globalIdToConsumers):
                    PostalService._globalIdToConsumers[i] = []
                PostalService._globalIdToConsumers[i].append(consumer)
        elif (subscriptionType == PostalService.PASSIVE_SUBSCRIPTION):
            for i in ids:
                if (not i in PostalService._passiveIdToConsumers):
                    PostalService._passiveIdToConsumers[i] = []
                PostalService._passiveIdToConsumers[i].append(consumer)
        elif (subscriptionType == PostalService.ACTIVE_SUBSCRIPTION):
            for i in ids:
                if (not i in PostalService._activeIdToConsumers):
                    PostalService._activeIdToConsumers[i] = []
                PostalService._activeIdToConsumers[i].append(consumer)

    @staticmethod
    def sendMessage(msg):
        """Sends a message

        Args:
            msg (Message): The message to send
        """
        assert isinstance(msg, Message)
        sent = False
        # Currently messages could be received more than one time.
        # We may need to add a unique send for each consumer.

        # The instant consumer is all powerfull, and eats the messages if consumed
        if (not PostalService._sendInstant(msg)):
            sent = PostalService._sendActive(msg) or sent
            sent = PostalService._sendGlobal(msg) or sent
            sent = PostalService._sendPassive(msg) or sent
            if (not sent):
                Printer.print("Message has no subscriber. ID: {}".format(msg.msgId))

    @staticmethod
    def _sendGlobal(msg):
        """Sends all global messages

        Args:
            msg (Message): The message

        Returns:
            bool: True if sent, false otherwise
        """
        sent = False
        if (msg.msgId in PostalService._globalIdToConsumers.keys()):
            for c in PostalService._globalIdToConsumers[msg.msgId]:
                c.consume(msg)
                sent = True
        return sent

    @staticmethod
    def _sendInstant(msg):
        """Sends to the instant consumer

        Args:
            msg (Message): The message to send

        Returns:
            [bool]: True if send, false otherwise
        """
        if (PostalService._mainNode == None):
            return False
        if (msg.msgId in PostalService._instantIds):
            PostalService._mainNode.consume(msg)
            return True
        return False

    @staticmethod
    def _sendPassive(msg):
        """Sends all passive messages

        Args:
            msg (Message): The message to send

        Returns:
            bool: True if any sent, false otherwise
        """
        sent = False
        if (msg.msgId in PostalService._passiveIdToConsumers.keys()):
            for c in PostalService._passiveIdToConsumers[msg.msgId]:
                c.receiveBuffer.append(msg)
                sent = True
        return sent

    @staticmethod
    def _sendActive(msg):
        """Sends all active messages

        Args:
            msg (Message): The message to send

        Returns:
            bool: If any sent, True, false otherwise
        """
        sent = False
        if (msg.msgId in PostalService._activeIdToConsumers.keys()):
            for c in PostalService._activeIdToConsumers[msg.msgId]:
                if (c.isActive):
                    c.consume(msg)
                    sent = True
        return sent