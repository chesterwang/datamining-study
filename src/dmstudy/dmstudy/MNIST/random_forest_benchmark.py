import sys
import csv
import time
import numpy as np

from PIL import Image
from collections import defaultdict
from multiprocessing import Pool


PROFILE = '-p' in sys.argv

VERBOSE = '-v' in sys.argv
def trace(msg):
    if not VERBOSE:
        return
    print(msg)


PERF = {}


def memoize(func):
    func.__value = None

    def wrapper(*args, **kw):
        if func.__value is None:
             func.__value = func(*args, **kw)
        return func.__value

    return wrapper


def perf(func):
    if not PROFILE:
        return func
    PERF[func.__name__] = (0, 0)
    def wrapper(*args, **kw):
        start = time.time()
        ret = func(*args, **kw)
        end = time.time()
        elapsed, calls = PERF[func.__name__]
        PERF[func.__name__] = (elapsed + (end - start), calls + 1)
        return ret

    return wrapper


@perf
def read_csv(filename):
    with open(filename, 'r') as fp:
        reader = csv.reader(fp)

        # skips first line
        reader.next()
        return np.array([map(int, row) for row in reader])


@memoize
def get_train():
    trace('processing train.csv...')
    return read_csv('../train.csv')


@memoize
def get_test():
    trace('processing test.csv...')
    return read_csv('../test.csv')


def euclidean(elem1, elem2):
    arr = np.subtract(elem2, elem1)
    arr = arr**2
    return arr.sum()


@perf
def knn(k, dist_func, dataset, elem):
    trace('knn k=%s' % k)
    neighbors = []
    furthest_neighbor_dist = None
    furthest_neighbor_i = None

    for test_i, test_elem in enumerate(dataset):
        cls, data = test_elem[0], test_elem[1:]
        dist = dist_func(data, elem)

        # checks if the new tested elem is relevant
        if (furthest_neighbor_dist is not None) and (dist > furthest_neighbor_dist):
            continue

        # appends or replaces previous neighbor
        if k > len(neighbors):
            neighbors.append((cls, dist))
        else:
            neighbors[furthest_neighbor_i] = (cls, dist)

        # updates furthest neighbor's info
        furthest_neighbor_dist = max(neighbors, key=lambda x: x[1])[1]
        distances = [x[1] for x in neighbors]
        furthest_neighbor_i = distances.index(max(distances))
    trace(neighbors)

    results = defaultdict(lambda : 0)
    for neighbor in neighbors:
        cls = neighbor[0]
        results[cls] += 1

    return max(results, key=lambda x: results[x])


def show(pixels):
    im = Image.new('L', (28, 28), None)
    im.putdata(pixels)
    im.show()


def test(train_set, validation_set, verbose=False):
    num_elems = len(validation_set)
    ok = 0
    for i, pic in enumerate(validation_set):
        expected = pic[0]
        result = knn(3, euclidean, train_set, pic[1:])
        if expected == result:
            ok += 1

        if verbose:
            print('%i/%i\r' % (i, num_elems), end='')
            sys.stdout.flush()

    return ok


def run(x):
    return test(*x)


if __name__ == '__main__':
    train = get_train()[:-1000]
    validation = get_train()[-1000:]

    print('train', len(train))
    print('validation', len(validation))

    start = time.time()

    num_pools = 4
    pool = Pool(num_pools)
    set_size = len(validation) // num_pools
    inputs = [validation[i*set_size: (i+1)*set_size] for i in range(num_pools)]
    result = pool.map(run, [(train, subset) for subset in inputs])

    print('pools', num_pools)
    print('elems per pool', set_size)
    print('elapsed time:', (time.time() - start))

    ok = sum(result)
    print('ok', ok, '(%s%%)' % ((float(ok) / (set_size * num_pools)) * 100))

    if PERF:
        for func in PERF:
            elapsed, calls = PERF[func]
            if not calls:
                continue
            print(func, 'elapsed total:', elapsed, 'in %s calls' % calls, 'time per call:', elapsed / calls)
