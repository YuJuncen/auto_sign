from uuid import uuid4
from random import choice
from cursesmenu import SelectionMenu 

class DeviceInfo(object):
    def __init__(self, os_name, device_uuid):
        self.os_name = os_name
        self.device_uuid = device_uuid

    def __repr__(self):
        return f"< Device {self.device_uuid} >"


class DeviceInfoFactory(object):
    random_device_list = [
        "小米 Mix 3",
        "华为 Mate 20",
        "一加 6t",
        "三星 Galaxy S9",
        "OPPO R19",
        "VIVO NEX"
    ]

    random_carrier_list = [
        "中国联通",
        "中国移动",
        "中国电信"
    ]

    random_android_version = [
        "6.0.1",
        "5.1.1",
        "7.1.2",
        "8.0.1",
        "9"
    ]

    @classmethod
    def random_os_name(cls):
        return choice(cls.random_device_list) + \
            "运营商：" + choice(cls.random_carrier_list) + \
            "\n" + choice(cls.random_android_version)

    @classmethod
    def make_random_device(cls):
        os_name = cls.random_os_name()
        return DeviceInfo(os_name, uuid4())

    @classmethod
    def prompt_device(cls):
        device_name = input("输入你的手机名字，空值是随机生成：") or choice(cls.random_device_list)
        carrier = cls.random_carrier_list[SelectionMenu.get_selection(cls.random_carrier_list, title="选择你的运营商：", exit_option=False)]
        android_version = input("输入你的系统版本号，空值是随机生成：") or choice(cls.random_android_version)
        os_name = f"{device_name}运营商：{carrier}\n{android_version}"
        device_id = input("输入手机的 IMEI，空值是随机生成：") or uuid4()
        return DeviceInfo(os_name, device_id)

