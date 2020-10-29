import numpy as np
import random
for i in range(np.random.randint(10,50)):
    var = ['0'] * 4
    for i in range(2):
        if i == 0:
            var[i] = np.random.randint(0,480)
            var[i+1] = var[i]+32
        else:
            var[i+1] = np.random.randint(0,480)
            var[i+2] = var[i+1]+32
    var = map(str, var)
    print(' '.join(var) + ' %s'%random.choice(['6000095799', '6000095829', '6000095904', '6000095921', '6000096175', '6000096206', '6000096294', '6000096220']))