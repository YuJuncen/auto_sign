from requests import post
from json import dumps, loads
from datetime import datetime as D
from sys import exc_info
from random import choice, random
from asyncio import sleep, run

from .Config import static_config as SConf
from .TokenFactory import AbstractTokenFactory
from .SignInfoServer import BaseSignInfoServer
from . import core_logger as log
from .DeviceInfo import DeviceInfo


class SignClient(object):
    """
    签到的控制器(Controllor)。  
    组合所有元素，并且最后发出签到请求。
    ```
    __err_codes = {
        0: "成功。",
        1: "还没有到签到时间，如果强行签到的话可能会导致一些难以预测的后果。",
        2: "服务器返回失败。",
        3: "其它模块出现错误。",
        4: "令牌错误，但是已经重新生成（不一定能生成有效令牌，具体取决于令牌工厂的力量）。"
    }
    ```
    """
    __err_codes = {
        0: "成功。",
        1: "还没有到签到时间，如果强行签到的话可能会导致一些难以预测的后果。",
        2: "服务器返回失败。",
        3: "其它模块出现错误。",
        4: "令牌错误，但是已经重新生成（不一定能生成有效令牌，具体取决于令牌工厂的力量）。"
    }

    def __init__(self,
                 tfactory: AbstractTokenFactory,
                 dev: DeviceInfo,
                 infod: BaseSignInfoServer,
                 conf=SConf
                 ):
        self.__conf = conf
        self.__tfactory = tfactory
        self.__dev = dev
        self.__infod = infod
        self.__token = self.__tfactory.make_token()
        self.__sign_info = None

    @property
    def device(self):
        """
        获得客户端的设备信息。
        """
        return self.__dev

    @property
    def sign_info(self):
        if self.__sign_info is None:
            self.update_sign_info()

        return self.__sign_info

    def update_sign_info(self):
        self.__sign_info, err = self.__infod.get_sign_info(self.__token)
        if err != 0:
            _, info = self.handle_with_data_getter_error(err)
            raise RuntimeError(info)
        log.debug(f"信息成功刷新。字段：{[k for k in self.__sign_info.keys()]}")
        return 0

    def auto_sign(self, force=False):
        return run(self.async_auto_sign(force))

    def handle_with_data_getter_error(self, err):
        code, info = err
        log.warning(f"获得信息的时候，出现了错误：{info}")
        if code == 4:
            self.__token = self.__tfactory.make_token()
            return 4, self.__err_codes[4]
        return 3, info

    async def make_sign_data(self, bleChoicer: callable = choice):
        """
        仅仅制造签到时所需要的请求数据（不包括 token），然后返回。
        """
        datas = {
            "bleId": bleChoicer([bled['bleId'] for bled in self.sign_info.get('bleinfoList')]),
            "devUuid": self.__dev.device_uuid,
            "osName": self.__dev.os_name,
            "signId": self.sign_info.get("signId")
        }

        return datas

    def check_time_is_vaild(self):
        sign_info = self.sign_info

        if (sign_info.get('sponsorStatus') == '0'):
            log.warning('签到自己说它没有开始。')
            log.info(f'签到启动时间：{sign_info.get("startTime")}。')
            return False

        return True

    async def safety_delay(self):
        delay_time = random() * 5 + 3
        log.info(f"正在“搜索”蓝牙设备，预计用时 {delay_time}s。")
        await sleep(delay_time)

    async def async_auto_sign(self, force=False):
        """
        usage:   
        ** 自动签到。 **

        args:  
        |name      | usage    |  
        |: -----  :|: ------ :|  
        |*force*    | 不到时间也强制签到。|

        return:  
        如果成功了，返回 None, 0。
        否则，返回 context, (errcode, errinfo)。
        """
        self.update_sign_info()
        datas = await self.make_sign_data()
        if not self.check_time_is_vaild():
            if not force:
                return datas, (1, self.__err_codes[1])
            log.warning(f"强制在签到时间外签到。")
        await self.safety_delay()

        headers = dict(
            **self.__conf.get_base_head(),
            **{
                "token": self.__token
            })
        r = post(self.__conf.get_sign_target(),
                 data=datas,
                 headers=headers)
        response_json = loads(r.content)
        if response_json.get("data").get("isSuccess") != "1":
            log.error(f"签到失败了；原因是：{response_json.get('message') or '不知道。'}")
            return response_json, (2, f"签到失败，原因是：{response_json.get('message') or '不知道。'}")
        log.info(f"签到成功；相关数据：{datas}")
        return None, 0
