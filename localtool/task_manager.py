from utils.OpenVasUtil import OpenVASTool, logging
from uuid import uuid4
from datetime import datetime

TCP_PORT_MAX = UDP_PORT_MAX = 20000
DEFAULT_PORTS = "T:1-" + str(TCP_PORT_MAX) + ",U:1-" + str(UDP_PORT_MAX)
DEFAULT_HOSTS = "127.0.0.1,192.168.2.99"

class Task():
    def __init__(self, hosts=DEFAULT_HOSTS, ports=DEFAULT_PORTS, task_desc=None):
        """
        任务设置的初始化
        :param hosts: 主机列表 --支持IP段
        :param ports: 端口列表 -- 格式如上
        :param task_desc: ---任务描述
        """
        self.config_info = "Full and very deep" # 最深扫描
        self.hosts = hosts
        self.ports = ports
        self.ud = str(uuid4())
        self.udt = str(datetime.now())
        self.task_desc = task_desc if task_desc else "脚本任务-" + self.ud + "["+self.udt+"]"

    def create_port_list(self):
        """
        创建端口列表
        :return:
        """
        _data = OpenVASTool().push_command("create_port_list", dict(
            name="端口列表-"+ self.ud,
            comment="产生端口列表",
            port_range=self.ports
        ))
        return _data["@id"]

    def create_target_and_get_targetid(self):
        """
        创建扫描主机目标并且获取该目标的id
        :return:
        """
        params = dict(name="扫描目标-" + self.ud,
                      make_unique=True,
                      asset_hosts_filter=None,
                      hosts=self.hosts,
                      comment="创建目标",
                      exclude_hosts=None,
                      alive_tests="Scan Config Default",
                      reverse_lookup_only=None,
                      reverse_lookup_unify=None,
                      port_range=None,
                      port_list_id="33d0cd82-57c6-11e1-8ed1-406186ea4fc5"
                      )
        _datas = OpenVASTool().push_command("create_target", params)
        return _datas["@id"]

    def get_active_scanner(self):
        """
        获取当前生效的扫描器
        :return:
        """
        datas = OpenVASTool().push_command("get_scanners", None)
        try:
            return [x["@id"] for x in datas["scanner"] if x["host"]][0]
        except:
            logging.error("缺少有效的扫描器")

    def configs(self):
        """
        获取所有的扫描配置; 可以自己添加，目前没有做这个
        :return:
        """
        datas = OpenVASTool().push_command("get_configs", None)
        _config_infos = []
        keys = ["@id", "name", "comment"]
        try:
            for x in datas["config"]:
                _temp = {}
                for key in keys:
                    _temp.setdefault(key, x[key])
                _config_infos.append(_temp)
            return _config_infos
        except:
            logging.error("缺少有效的扫描器")

    def get_config(self):
        """
        选择扫描方案的配置。有主机发现，端口返现，深度扫描，浅层次扫描
        :return:
        """
        return [x["@id"] for x in self.configs() if x["name"] == self.config_info][0]

    def create_task(self):
        """
        常见扫描任务
        :return:
        """
        params = dict(name=self.task_desc,
                      config_id=self.get_config(),
                      target_id=self.create_target_and_get_targetid(),
                      scanner_id=self.get_active_scanner(),
                      comment="脚本任务"
                      )
        _data = OpenVASTool().push_command("create_task", params)

        from utils.redis_cli import RC
        RC.set("task_id", _data["@id"])

        return _data

    def run_lattest_task_atnow(self):
        """
        立即执行最近的一次扫描任务
        :return:
        """
        _tasks = OpenVASTool().push_command("get_tasks", {"details": True})["task"]
        _dict_tasks = []
        _keys = ["@id", "name", "creation_time", "comment"]
        for task in _tasks:
            _temp = {}
            for key in _keys:
                _temp[key] = task[key]
            _dict_tasks.append(_temp)
        _res = sorted(_dict_tasks, key=lambda x:x['creation_time'], reverse=True)
        lattest_taskid = _res[0]["@id"]
        _resp = OpenVASTool().push_command("start_task", {"task_id": lattest_taskid})
        if _resp["@status"] == 400:
            logging.error(_resp["@status_text"])
        else:
            self.report_recode(_resp["report_id"])  ## 记录下 report_id 后面要用
        return _resp

    def get_task_info(self):
        """
        查看当前任务的情况, 是否正在执行
        :return:
        """
        from utils.redis_cli import RC
        _resp = OpenVASTool().push_command("get_task", {"task_id": RC.get("task_id")})
        return _resp


    def create_task_and_runnow(self):
        """
        创建任务并立即执行
        :return:
        """
        task_id = self.create_task()["@id"]
        _resp = OpenVASTool().push_command("start_task", {"task_id": task_id})
        self.report_recode(_resp["report_id"]) ## 记录下 report_id 后面要用
        return _resp

    def report_recode(self, report_id):
        """
        记录 report_id 到本地
        :param report_id:
        :return:
        """
        from utils.redis_cli import RC
        return RC.set('report_id', report_id)

    @staticmethod
    def get_report_id():
        """
        从本地获取report_id
        :return:
        """
        from utils.redis_cli import RC
        return RC.get("report_id")











