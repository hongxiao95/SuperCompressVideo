import time
import random
a = time.time()
time.sleep(1)
print(time.time() - a)
for i in range(20):
    print(random.randint(0,3))