from aitpi.src import aitpi
import pytest

class DummyMsg(aitpi.Message):
    msgId = 10

class Watch():
    watchall = []
    def __init__(self) -> None:
        Watch.watchall = []
        self.calls = []

    def consume(self, msg):
        print("Consume")
        self.calls.append(msg)
        Watch.watchall.append(self)

def test_basic():
    aitpi.router.reset()
    watch = Watch()
    aitpi.router.addConsumer([DummyMsg.msgId], watch)
    aitpi.router.send(DummyMsg("Data"))
    assert len(watch.calls) == 1

def test_multi():
    aitpi.router.reset()
    watch = Watch()
    aitpi.router.addConsumer([DummyMsg.msgId], watch)
    aitpi.router.send(DummyMsg("Data"))
    aitpi.router.send(DummyMsg("Data"))
    assert len(watch.calls) == 2

def test_priority():
    print("Prio")
    aitpi.router.reset()
    watch = Watch()
    watch2 = Watch()
    aitpi.router.addConsumer([DummyMsg.msgId], watch)
    aitpi.router.addConsumer([DummyMsg.msgId], watch2, 1)
    aitpi.router.send(DummyMsg("Data"))
    assert len(watch.calls) == 1
    assert len(watch2.calls) == 1
    assert Watch.watchall[0] is watch2
    assert Watch.watchall[1] is watch
