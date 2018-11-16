from .Config import AbstructTokenConfig, AbstructGenericConfig, static_config
from requests import post
from json import dumps, loads
from sys import exc_info


class AbstractTokenFactory(object):
    def make_token(self):
        raise NotImplementedError


class StaticTokenFactory(AbstractTokenFactory):
    def __init__(self, token):
        self.__token = token

    def make_token(self):
        return self.__token


class UsernamePasswordTokenFactory(AbstractTokenFactory):
    def __init__(self, username, password, conf: AbstructTokenConfig = static_config, gconf: AbstructGenericConfig = static_config):
        self.__username = username
        self.__password = password
        self.__conf = conf
        self.__gconf = gconf

    def make_token(self):
        """
        usage:   
        ** get the token. **

        args:  

        |name     | usage    |  
        |: ----- :|: ------ :|  
        |*config*   | the config object, see `config.py`. |  
        |*username* | username.|  
        |*password* | password.|  

        return:  
        ** the token. **
        """
        r = post(self.__conf.get_login_target(),
                 headers=self.__gconf.get_base_head(),
                 data={"params": dumps({
                     "userName": self.__username,
                     "password": self.__password
                 })
        })

        response_json = loads(r.content)
        try:
            assert response_json['result']['isSuccess'] == '1'
            return response_json['result']['token']
        except AssertionError:
            trace = exc_info()[2]
            raise RuntimeError(
                f"登录失败，原因是：{response_json.get('result').get('message') or '不知道。'}").with_traceback(trace)
        except KeyError as e:
            trace = exc_info()[2]
            raise RuntimeError(
                f"登陆失败，返回的包里面似乎没有需要的信息。\n\tMORE: {e}").with_traceback(trace)
