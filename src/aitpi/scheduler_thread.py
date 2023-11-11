import sched
import time
import threading

class SchedulerThread():
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.worker = threading.Thread(target=self.run)
        self.running = False
        self.shouldRun = False

    def run(self):
        print("Run")
        while (self.shouldRun):
            self.scheduler.run()
            print("Running")
            time.sleep(0.5)
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        self.shouldRun = True
        print("Run")
        self.worker.start()

    def stop(self, blockWait=False):
        if not self.running:
            return False
        self.shouldRun = False
        while blockWait and self.running:
            time.sleep(0.25)

    def scheduleItem(self, delay, fun, arguments=(), priority=0):
        return self.scheduler.enter(delay, priority, fun, arguments)

