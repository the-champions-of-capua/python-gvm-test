
def test_crate_ports():
    from gvmd.task_manager import Task

    _datas = Task().create_port_list()

    print(_datas)
    """da92d575-e96c-46e7-b3f6-7f104abebddf"""

def test_crete_targets():
    from gvmd.task_manager import Task
    _datas = Task(hosts=["192.168.2.175", "192.168.2.99"]).create_target_and_get_targetid()
    print(_datas)
    """d7b7637b-6b19-4ec7-9a49-10a51d05726a"""

def test_start_task():
    from wraper.OpenVasUtil import OpenVASTool
    _resp = OpenVASTool().push_command("start_task", {"task_id": "d7b7637b-6b19-4ec7-9a49-10a51d05726a"})
    print(_resp)

def test2():
    from gvmd.task_manager import Task
    _resp = Task().create_task_and_runnow()
    # print(_resp)
    ########## 打印当前正在运行得任务情况
    print(Task().get_the_lattest_running_task_info())

if __name__ == '__main__':
    # from dao.data_extract import extract_item
    # # apscheduler 重复调用这个接口就可以写入当前得报告到数据库
    # _data = extract_item()
    # print(_data)
    #test_crete_targets()
    test_start_task()


