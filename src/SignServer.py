from requests import post, get
from json import loads
from . import core_logger as log


class SignServer(object):
    def sign(self, info):
        raise NotImplementedError

    def get_info(self, token):
        raise NotImplementedError

    def login(self, username, password):
        raise NotImplementedError

    def debug_post(self, **kargs):
        raise NotImplementedError

    class SignServerException(Exception):
        @property
        def context(self):
            return self.__context

        def __init__(self, info, context):
            super().__init__(info)
            self.__context = context

    def throw_exception_with(self, reason, context=None):
        if context is None:
            context = self
        raise SignServer.SignServerException(reason, context)


class CSUSTServer(SignServer):
    protocol = "https"
    base_host_name = "csust.edu.chsh8j.com"
    port = "443"
    sign_path = "/dorm/app/dormsign/sign/student/edit"
    sign_detail_path = "/dorm/app/dormsign/sign/student/detail"
    login_path = "/magus/appuserloginapi/userlogin"
    base_head = {
        "User-Agent": "ScienceAndEngineerOnHand/2.5.8 (iPhone; iOS 12.0.1; Scale/2.00)",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    def get_login_target(self):
        return self.protocol + "://" + self.base_host_name + ":" + self.port + self.login_path

    def get_sign_detail_target(self):
        return self.protocol + "://" + self.base_host_name + ":" + self.port + self.sign_detail_path

    def get_sign_target(self):
        return self.protocol + "://" + self.base_host_name + ":" + self.port + self.sign_path

    def get_base_head(self):
        return self.base_head

    def sign(self, info):
        """
        info: {
            data: {
                $"bleID",
                $"devUuid",
                $"osName",
                $"signId"
            },
            header: {
                $"user-agent",
                $"token"
            }
        }
        """
        fields = ["bleId", "devUuid", "osName", "signId"]
        if all([x in info.get('data', []) for x in fields]):
            return self.dosign(info)
        self.throw_exception_with(
            f"缺少了必要的信息：{set(fields) - set(info.get('data', dict()).keys())}", info)

    def dosign(self, info):
        headers = dict(**self.base_head, **info.get('header', {}))
        r = post(self.get_sign_target(), data=info['data'], headers=headers)
        response_json = loads(r.content)
        if response_json.get("data", {}).get("isSuccess") != "1":
            log.error(f"签到失败了；原因是：{response_json.get('message') or '不知道。'}")
            self.throw_exception_with(
                f"签到失败，原因是：{response_json.get('message') or '不知道。'}", response_json)
        log.info(f"签到成功；相关数据：{info}")
        return 0
