# 这个技巧是在看《小林家的妹抖龙》的时候学到的。
try:
    import cpickle as P
except ImportError:
    import pickle as P
from uuid import uuid1
from os import listdir, path, makedirs
from getpass import getpass
import texttable as TT

from . import from_username_password
from .DeviceInfo import DeviceInfoFactory

class Handler(object):
        def __init__(self, callback, params: list, nullable_params: list, help : str, name : str):
            self.__callback = callback
            self.__params = params
            self.__nullable_params = nullable_params
            self.__help = help
            self.__name = name
        
        @property
        def name(self):
            return self.__name

        @property
        def help(self):
            return self.__help

        @property
        def params(self):
            return self.__params

        @property
        def nullable_params(self):
            return self.__nullable_params

        def __check_params(self, gived):
            success = True
            for p in self.__params:
                if not p in gived:
                    print(f"缺少必要的参数：{p}")
                    success = False
            return success

        def __str__(self):
            if len(self.params) + len(self.nullable_params) == 0:
                usage = "无参数"
            else:
                usage = "必须参数：%s\t可选参数：[%s]" % (", ".join(self.params), ", ".join(self.nullable_params))
            return "\t".join([self.name, self.help, usage])

        def call(self, **kargs):
            params = set(kargs.keys())
            if self.__check_params(params):
                try:
                    return self.__callback(**kargs)
                except Exception as e:
                    print(f"发生高阶错误：{type(e)}, {e}")
                    return -1
                except BaseException as e:
                    print(f"发生底层错误：{str(type(e))}, {e}")
            return -1

class BaseController(object):
    def __init__(self):
        self.__handlers = {}
        self.__default_event = None

    def handler(self, name, params:list = [], optional_params:list = [], help: str = None):
        def handler_impl(f):
            self.__handlers[name.lower()] = Handler(f, params, optional_params, help, name.lower())
            return f
        return handler_impl

    def seek_hander(self, name):
        return self.__handlers.get(name.lower())

    @property
    def default_event(self):
        return self.__default_event
    
    def set_default_event(self, new:str):
        self.__default_event = self.seek_hander(new.lower())

    def run_event(self, event_name, **kcontext):
        handler = self.seek_hander(event_name) or self.default_event
        if handler is not None:
            return handler.call(**kcontext)
        raise KeyError("Can't resolve the command, and no default handler setted.")

    def print_help(self):
        table = TT.Texttable()
        table.header(['命令名字', '帮助', '必须参数', '可选参数'])
        for h in self.__handlers.values():
            table.add_row([h.name, h.help, h.params, h.nullable_params])
        print(table.draw())

class AutoSignUser(object):
    def __init__(self, id, client):
        self.__id = id
        self.__client = client
    
    @property
    def client(self):
        return self.__client

    def __str__(self):
        return "\t".join([self.__id, self.client])

core_controller = BaseController()
base_path = ['$HOME', '.autosign']

def get_users():
    def load_pickle(name):
        with open(name, 'wb') as p:
            return P.load(p)
    l = [ load_pickle(name) for name in listdir(path.join(*base_path)) if name.endswith('userdump.pickle') ]
    return l

@core_controller.handler("add", ['username'], ['password'], "从用户名和密码新增一个用户。")
def add_user(username = None, password = None, **_):
    if password is None:
        password = getpass()
    user_uuid = uuid1()
    device = DeviceInfoFactory.prompt_device()

    u = AutoSignUser(user_uuid , from_username_password(username, password, device))
    makedirs(path.join(*base_path))
    with open(path.join(*base_path, f'{user_uuid}.userdump.pickle'), 'wb') as p:
        P.dump(u, p)
    return 0

@core_controller.handler("list", help="展示所有的用户。")
def list_user(**_):
    print(get_users(), sep='\n')

@core_controller.handler("allmen", help="为所有用户签到。")
def sign_all(**_):
    ans = [ c.client.auto_sign() for c in get_users() ]
    print(ans)
    return 0

@core_controller.handler("help", help="显示这条帮助信息。")
def useage_help(**_):
    general_help = """usage: python3 main.py <command> (<params>)* where
<params> := <key>'='<value>
example: python3 main.py add username=liuxin
-- 使用 add 命令，参数 username 的值为 liuxin。
    """
    print(general_help)
    print("命令列表：")
    core_controller.print_help()
    return 0

@core_controller.handler("crondump", help="将自动签到转储到 corntab 中，\n定时执行自动签到。")
def crondump(**_):
    pass