from getgauge.python import step, before_spec, Messages, DataStoreFactory
from src import get_test_client, SignClient, default_infod
from os import chdir, curdir

# --------------------------
# Gauge step implementations
# --------------------------
data_store = DataStoreFactory.spec_data_store()
@step("We can get a token if we input right username and password.")
def get_token():
    Messages.write_message("考虑到频繁执行这个测试的风险，我们暂时搁置这个测试。")
    """
    _, _, token_fact = get_test_client()
    token = token_fact.make_token() 
    assert token is not None
    Messages.write_message(f"the token is {len(token)}.")
    assert len(token) >= 64
    data_store.put('token', token)
    """

@step("after sign, we will get no sign infomation.")
def sign_test():
    c, _, _ = get_test_client()
    _, status = c.auto_sign()
    if status == 0:
        Messages.write_message("签到看起来成功了，接下来看看我们还能不能签。")
        _, (e, _) = c.auto_sign()
        assert e == 3
        Messages.write_message("我们签完了。")
    else:
        status, _ = status
        if status == 1:
            Messages.write_message("现在还没到时间。")
            return
        if status == 3:
            Messages.write_message("已经签过到了。")
            return
        Messages.write_message("很奇怪，这里出问题了。")
        assert False


# ---------------
# Execution Hooks
# ---------------

@before_spec()
def before_spec_hook():
    chdir("step_impl")
