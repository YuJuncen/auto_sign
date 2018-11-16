from src.UserInterface import core_controller
from sys import argv
from functools import reduce

def main(argv = argv):
    if len(argv) < 2:
        argv.append('')
    core_controller.set_default_event('help')
    kvs = {}
    def go(_, new):
        k, v = new.split('=', maxsplit=1)
        kvs[k] = v
    reduce(go, argv[2:], None)
    return core_controller.run_event(argv[1], **kvs)

if __name__ == '__main__':
    main()