class AbstructTokenConfig(object):
    def get_login_target(self):
        raise NotImplementedError


class AbstructSignConfig(object):
    def get_sign_detail_target(self):
        raise NotImplementedError

    def get_sign_target(self):
        raise NotImplementedError


class AbstructGenericConfig(object):
    def get_base_head(self):
        raise NotImplementedError


class DefaultConfig(AbstructTokenConfig, AbstructSignConfig, AbstructGenericConfig):
    """
    静态配置单例。  
    请不要引入这个类，当需要使用这个类的实例的时候，请直接引入 `static_config` 单例。
    ```
    # do 👍
    from config import static_config as Conf

    # don't 👎
    # from config import StaticConfig
    # Conf = StaticConfig()
    ```
    """
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


static_config = DefaultConfig()
