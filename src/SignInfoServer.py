from requests import post
from json import loads

from .Config import AbstructSignConfig, AbstructGenericConfig, static_config

class BaseSignInfoServer(object):
    def get_sign_info(self, token):
        raise NotImplementedError
    
    def get_ble_list(self, token):
        r, e = self.get_sign_info(token)
        if e != 0:
            return r, e
        
        return r.get("bleinfoList"), 0

    def get_sign_id(self, token):
        r, e = self.get_sign_info(token)
        if e != 0:
            return r, e
        
        return r.get("signId"), 0

class ConfigedSignInfoServer(BaseSignInfoServer):
    __err_codes = {
        0: "成功。",
        1: "返回参数出现异常。",
        2: "返回的列表里面没有 data 段。",
        3: "现在没有可用的签到。",
        4: "令牌过期了。"
    }

    def __init__(self, conf: AbstructSignConfig, gconf: AbstructGenericConfig):
        self.__conf = conf
        self.__gconf = gconf
        self.__mem = None

    def get_sign_info(self, token: str):
        r = post(self.__conf.get_sign_detail_target(),
                 headers=dict(**self.__gconf.get_base_head(), **{
                     "token": token
                 }))
        response_json = loads(r.content)

        if response_json.get('status') == 11051:
            return response_json, (4, self.__err_codes[4])
        if response_json.get('data') is None:
            return response_json, (2, self.__err_codes[2])
        if response_json.get('status') != 1:
            return response_json, (1, self.__err_codes[1])
        if response_json.get('data').get('isAvailable') == '0':
            return response_json, (3, self.__err_codes[3])

        self.__mem = response_json.get('data')
        return self.__mem, 0

default_infod = ConfigedSignInfoServer(static_config, static_config)