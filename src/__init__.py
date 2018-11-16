import logging
from configparser import ConfigParser
try:
    import cPickle as P
except ImportError:
    import pickle as P

logging.basicConfig(
    format="%(asctime)-15s %(name)s::[%(levelname)s] %(message)s")
core_logger = logging.getLogger("core")
core_logger.setLevel(1)

from .SignClient import SignClient
from .TokenFactory import StaticTokenFactory, UsernamePasswordTokenFactory
from .SignInfoServer import default_infod
from .DeviceInfo import DeviceInfo, DeviceInfoFactory

def with_pickled_client(filename, continutaion):
    try:
        with open(filename, 'rb') as p:
            c = P.load(p)
            continutaion(c)
    finally:
        with open(filename, 'wb') as p:
            P.dump(c, p)


def local_auto_sign(max_delay = -1):
    try:
        with_pickled_client('client.pickle', id)
        if max_delay > 0:
            delay = __import__('random').randrange(max_delay)
            core_logger.info('最大延迟时间设置：{}; 随机生成延迟时间：{}。'.format(max_delay, delay))
            __import__('time').sleep(delay)
        return with_pickled_client('client.pickle', lambda c: c.auto_sign())
    except KeyboardInterrupt:
        core_logger.info('签到取消。')
    except RuntimeError as e:
        core_logger.error(f"运行时错误：{e}")


def from_username_password(username, password, device=DeviceInfoFactory.make_random_device()):
    return SignClient(
        UsernamePasswordTokenFactory(username, password),
        device,
        default_infod
    )


def from_token(token, device=DeviceInfoFactory.make_random_device()):
    return SignClient(
        StaticTokenFactory(token),
        device,
        default_infod
    )


def get_test_client():
    cp = ConfigParser()
    cp.read("conf.ini")

    myDevice = DeviceInfo(
        os_name=cp['static-config'].get('os_name'),
        device_uuid=cp['static-config'].get('device_uuid')
    )

    myTokenFactoty = UsernamePasswordTokenFactory(cp['personal-info'].get('username'),
                                                  cp['personal-info'].get('password'))
    myClient = SignClient(
        StaticTokenFactory(cp['personal-info'].get('token')),
        myDevice,
        default_infod
    )
    return myClient, myDevice, myTokenFactoty
