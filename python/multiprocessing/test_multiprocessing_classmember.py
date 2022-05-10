# coding: utf-8
class test:
    def __init__(self):
        self.q = Queue()
        self.proc = Process(target=self._do_something,)

    def __del__(self):
        try:
            print('* stopping process ')
            self.proc.terminate()
        except Exception as e:
            print('* failed to terminate process, sending SIGKILL')
            self.proc.kill()

    def _do_something(self):
        while True:
            self.q.put('{}: blubb'.format(time.time()))
            time.sleep(1)
    
    def run(self):
        self.proc.start()
        
    def get_data(self):
        while not self.q.empty():
            print(self.q.get())
            
