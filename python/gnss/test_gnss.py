from GNSS import GNSS_receiver
import time

def run_test():
    gps = GNSS_receiver()
    gps.run()
    while True:
        print(gps.get_data())
        time.sleep(1)

if __name__ == '__main__':
    run_test()
