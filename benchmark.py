from __future__ import print_function
import importlib
import json
import sys
import timeit
from collections import OrderedDict
from io import open


N_RUNS = 100
MODULES = ('json', 'simplejson', 'ujson', 'rapidjson')

try:
    import __pypy__
    INTERPRETER_NAME = 'PyPy'
except ImportError:
    INTERPRETER_NAME = 'Python'

INTERPRETER = '{} {}'.format(INTERPRETER_NAME, '.'.join(map(str, sys.version_info[:2])))


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
    for name in MODULES:
        try:
            yield importlib.import_module(name)
        except ImportError:
            print('Unable to import {}'.format(name))


def print_results(results):
    for benchmark_name, benchmark_results in results.items():
        print(benchmark_name)
        print('-' * len(benchmark_name))
        for module_name, result in benchmark_results.items():
            print('{:16}{:.3f}s'.format(module_name, result))
        print()


def print_rest_tables(results):
    module_names = list(results.values())[0].keys()
    print('.. csv-table:: {}'.format(INTERPRETER))
    print(':header: , {}'.format(', '.join(module_names)))
    print(':widths: 20{}'.format(', 10' * len(module_names)))
    print()
    for benchmark_name, results in results.items():
        print('*{}*, {}'.format(benchmark_name, ', '.join(['{:.3f}'.format(t) for t in results.values()])))


def save_plots(results):
    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except ImportError:
        print('Unable to import matplotlib')
        return

    matplotlib.rc('xtick', labelsize=10)
    module_names = list(results.values())[0].keys()
    benchmark_names = results.keys()
    modules_results = [[vals[mn] for vals in results.values()] for mn in module_names]
    n_benchmarks = len(benchmark_names)
    width = 1.0 / (len(module_names) + 1)
    fig, ax = plt.subplots()
    prop_iter = iter(plt.rcParams['axes.prop_cycle'])
    next(prop_iter)

    rects = []
    for i, module_results in enumerate(modules_results):
        rc = ax.bar([j + (width * i) for j in range(n_benchmarks)], module_results, width, color=next(prop_iter)['color'], zorder=5)
        rects.append(rc)

    def autolabel(rc):
        for rect in rc:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2., height - 0.105, '{:.2f}'.format(height), ha='center',
                    va='bottom', size=9, zorder=6)

    for rect in rects:
        autolabel(rect)

    ax.legend([rc[0] for rc in rects], module_names, loc='best')
    ax.set_ylabel('Time (s)')
    ax.set_title(INTERPRETER)
    ax.set_xticks([j + 0.38 for j in range(n_benchmarks)])
    ax.set_xticklabels(benchmark_names)
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    ax.yaxis.grid(True, zorder=0)

    plt.savefig('benchmark-json-{}.png'.format(INTERPRETER), bbox_inches='tight', dpi=200)


def run_benchmarks(generate_rest_tables, generate_plots, verbose):
    with open('data/twitter.json', encoding='utf-8') as f:
        large_obj_data = f.read()
    large_obj = json.loads(large_obj_data)

    with open('data/one-json-per-line.txt', encoding='utf-8') as f:
        small_objs_data = f.readlines()
    small_objs = [json.loads(line) for line in small_objs_data]

    benchmarks = [
        ('loads (large obj)', lambda m: benchmark_loads(m, large_obj_data)),
        ('dumps (large obj)', lambda m: benchmark_dumps(m, large_obj)),
        ('loads (small objs)', lambda m: benchmark_loads_byline(m, small_objs_data)),
        ('dumps (small objs)', lambda m: benchmark_dumps_byline(module, small_objs)),
    ]
    print(sys.version)

    results = OrderedDict()
    modules = import_modules()
    for module in modules:
        module_name = module.__name__
        print('Running {} benchmarks...'.format(module_name))
        for bencmark_name, fn in benchmarks:
            time = timeit.timeit(lambda: fn(module), number=N_RUNS)
            results.setdefault(bencmark_name, OrderedDict())
            results[bencmark_name][module_name] = time

    print('\nResults\n=======')
    print_results(results)

    if generate_rest_tables:
        print_rest_tables(results)

    if generate_plots:
        save_plots(results)

    if verbose:
        print(results)

if __name__ == '__main__':
    args = set(sys.argv[1:])
    run_benchmarks(generate_rest_tables='-t' in args, generate_plots='-p' in args, verbose='-v' in args)
