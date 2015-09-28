from __future__ import print_function
import timeit
import importlib
import json
from collections import defaultdict


NUMBER = 100


def benchmark_loads(module, data):
    module.loads(data)


def benchmark_dumps(module, obj):
    module.dumps(obj)


def benchmark_loads_byline(module, lines):
    for line in lines:
        module.loads(line)


def benchmark_dumps_byline(module, lines):
    for obj in lines:
        module.dumps(obj)


def import_modules():
    for name in ['json', 'simplejson', 'ujson']:
        try:
            yield importlib.import_module(name)
        except ImportError:
            print('Unable to import {}'.format(name))
            continue


def print_results(results):
    for suite_name, suite_results in results.items():
        print(suite_name)
        print('-' * 20)
        for module_name, result in suite_results.items():
            print('{:10} {:.5f} s'.format(module_name, result))
        print()


def run_benchmarks():
    with open('data/twitter.json') as f:
        data = f.read()
    obj = json.loads(data)

    with open('data/one-json-per-line.txt') as f:
        data_byline = f.readlines()
    objects_byline = [json.loads(line) for line in data_byline]

    results = defaultdict(dict)
    modules = import_modules()
    for module in modules:
        module_name = module.__name__
        print('Running {} benchmarks...'.format(module_name))
        results['loads'][module_name] = timeit.timeit(lambda: benchmark_loads(module, data), number=NUMBER)
        results['dumps'][module_name] = timeit.timeit(lambda: benchmark_dumps(module, obj), number=NUMBER)
        results['loads by line'][module_name] = timeit.timeit(lambda: benchmark_loads_byline(module, data_byline), number=NUMBER)
        results['dumps by line'][module_name] = timeit.timeit(lambda: benchmark_dumps_byline(module, objects_byline), number=NUMBER)

    print('\nResults\n=======')
    print_results(results)

if __name__ == '__main__':
    run_benchmarks()
