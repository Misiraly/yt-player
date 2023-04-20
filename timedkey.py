import msvcrt
import time
import os

from multiprocessing import Process, Value

def count(seconds, v):
    time.sleep(seconds)
    key = 'q'
    v.value = key
    print(f"\nI am finished counting at time: {str(time.time())}")
    
def ask(v):
    key = v.value
    while key != 'q':
        if msvcrt.kbhit():
            key = msvcrt.getch().decode("ASCII").lower()
            v.value = key
    print(f"\nfinshed the key is: {key} at time: {str(time.time())}")


if __name__ == '__main__':
    key = 'n'
    v = Value('u', key)
    print(time.time())
    print("hey")
    p1 = Process(target=count, args=(2,v,))
    p2 = Process(target=ask, args=(v,))
    p1.start()
    p2.start()
    i = 0
    while True:
        if v.value == 'q':
            print()
            break
        time.sleep(0.5)
        i += 1
        print(i, end=" ", flush=True)
        

    p1.terminate()
    p2.terminate()
    p1.join()
    p2.join()
    s = input()
    