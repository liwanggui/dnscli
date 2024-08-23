import sys
import json
import argparse

from pathlib import Path
from typing import List, NamedTuple

from prettytable.colortable import ColorTable, Themes

from .. import print_version

"""配置文件
{ "aliyun": { "secret_id": "", "secret_key": "" }, "dnspod": { "secret_id": "", "secret_key": "" } }
"""
CONFIG_DIR = "~/.config/dnscli.json"
RECORD_TYPES = ("A", "AAAA", "TXT", "CNAME", "NS", "MX")

class VersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print_version()
        parser.exit()

class DnsCli:
    def __init__(self, dnsname: str):
        self.dnsname = dnsname
        self.parser = argparse.ArgumentParser(description=f'DNS Cli Client for {self.dnsname}',  usage="%(prog)s command [options]")
        self.parser.add_argument('-v', '--version', action=VersionAction, nargs=0, help="显示版本号")
        self.subparser = self.parser.add_subparsers(title="subcommands", dest="func", metavar="", prog=self.parser.prog)

    def auth_parameter(self):
        auth_parser = argparse.ArgumentParser(add_help=False)
        auth = auth_parser.add_argument_group("authentication")
        auth.add_argument("--secret-id", metavar="", type=str, help="API 请求密钥 id")
        auth.add_argument("--secret-key", metavar="", type=str, help="API 请求密钥 key")
        return auth_parser

    def prettyprint_parameter(self):
        prettyprint_parser = argparse.ArgumentParser(add_help=False)
        prettyprint = prettyprint_parser.add_argument_group("prettytable arguments")
        prettyprint.add_argument("--header", action=argparse.BooleanOptionalAction, default=True, help="输出信息标题开关，默认显示")
        prettyprint.add_argument("--border", action=argparse.BooleanOptionalAction, default=True, help="输出信息边框开关，默认显示")
        prettyprint.add_argument("--number", action=argparse.BooleanOptionalAction, default=True, help="输出信息序号开关，默认显示")
        return prettyprint_parser

    def public_parameter(self, default_type="A", default_line="default"):
        public_parser = argparse.ArgumentParser(add_help=False)
        public_parser.add_argument("domain", metavar="DOMAIN", help="主域名")
        public_parser.add_argument("-n", "--name", metavar="", help="子域名")
        if default_type is None:
            type_help_msg=f'解析记录类型, 可用值：{"|".join(RECORD_TYPES)}'
        else:
            type_help_msg=f'解析记录类型, 可用值：{"|".join(RECORD_TYPES)}，默认值: "{default_type}"'
        if default_line is None:
            line_help_msg="解析线路名"
        else:
            line_help_msg=f'解析线路名，默认值: "{default_line}"'
        public_parser.add_argument("-t", "--type", metavar="", default=default_type, choices=RECORD_TYPES, help=type_help_msg)
        public_parser.add_argument("-l", "--line", metavar="", default=default_line, help=line_help_msg)
        return public_parser

    def custom_parameter(self):
        return argparse.ArgumentParser(add_help=False)

    def add_subparser(self, name: str, help: str, parents: List[argparse.ArgumentParser] = None, aliases: List[str] = None):
        if parents is None:
            parents = []
        if aliases is None:
            aliases = []
        return self.subparser.add_parser(name, help=help, parents=parents, aliases=aliases)

    def parse_args(self):
        return self.parser.parse_args()


def confirm(question):
    while True:
        response = input("%s [y/n] " % question).lower()
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Your input is incorrect, please re-enter. '(y)es' or '(n)o'.")

def write_config(dns_server, secret_id=None, secret_key=None):
    config_file = Path(CONFIG_DIR).expanduser()
    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)
    try:
        config = {}
        if not all((secret_id, secret_key)):
            print(f"配置 {dns_server.upper()} API 请求信息")
            secret_id = input("请输入 API 请求 ID: ").strip()
            secret_key = input("请输入 API 请求 Key: ").strip()
    
        if config_file.exists():
            with config_file.open('r') as f:
                config = json.load(f)
            if dns_server in config:
                if confirm(f"配置项 {dns_server} 已存在，是否覆盖"):
                    config[dns_server]["secret_id"] = secret_id
                    config[dns_server]["secret_key"] = secret_key
                else:
                    return True
        if dns_server not in config:
            config[dns_server] = {
                "secret_id": secret_id,
                "secret_key": secret_key
            }

        with config_file.open('w') as f:
            json.dump(config, f, indent=4)
            print(f"配置文件写入: {config_file.as_posix()}")
    except KeyboardInterrupt:
        raise SystemExit()

def read_config(dns_server):
    config_file = Path(CONFIG_DIR).expanduser()
    if not config_file.exists():
        raise SystemExit("配置文件不存在，请配置后重试")
    with config_file.open('r') as f:
        config = json.load(f)
        if dns_server in config:
            return config[dns_server]
        else:
            raise SystemExit(f"配置项 {dns_server} 不存在，请配置后重试")

def prettyprint(title, data, header=True, border=True, number=True):
    if number:
        if not isinstance(title, list):
            title = list(title)
        title.insert(0, "序号")
    table = ColorTable(title, theme=Themes.OCEAN)
    table.align = "l"
    table.header = header
    table.border = border
    for i, row in enumerate(data, start=1):
        if number:
            row.insert(0, i)
        table.add_row(row)
    print(table)

def main_cli(dns_server: str, default_type: str = None, default_line: str = "default") -> NamedTuple:
    dnscli = DnsCli(dns_server)
    auth_parameter = dnscli.auth_parameter()
    prettyprint_parameter = dnscli.prettyprint_parameter()
    # list-domain
    dnscli.add_subparser("list-domain", help="获取域名列表", parents=[auth_parameter, prettyprint_parameter], aliases=["ld"])

    # line or lines
    line_parameter = dnscli.custom_parameter()
    line_parameter.add_argument("-d", "--domain", metavar="", help="查询域名")
    dnscli.add_subparser("list-line", help="查看解析线路", parents=[auth_parameter, prettyprint_parameter, line_parameter], aliases=["ll"])

    # list
    dnscli.add_subparser(name="list", help="获取 DNS 解析记录", parents=[auth_parameter, prettyprint_parameter, dnscli.public_parameter(default_type=default_type, default_line=None)], aliases=["ls"])

    # create or add
    create_parameter = dnscli.public_parameter(default_line=default_line)
    create_parameter.add_argument("-v", "--value", metavar="", help="解析记录值")
    create_parameter.add_argument("-p", "--priority", metavar="", type=int, default=10, help="MX 解析记录优先级，默认值: 10")
    create_parameter.add_argument("--ttl", metavar="", type=int, default=600, help="解析记录缓存时间，默认值: 600")
    dnscli.add_subparser(name="create", help="创建 DNS 解析记录", parents=[auth_parameter, prettyprint_parameter, create_parameter], aliases=["add"])

    # change or update
    change_parameter = dnscli.custom_parameter()
    change_parameter.add_argument("domain", metavar="DOMAIN", help="主域名")
    old_group = change_parameter.add_argument_group("old record arguments")
    old_group.add_argument("-n", "--name", metavar="", help="子域名")
    old_group.add_argument("-v", "--value", metavar="", help="解析记录值")
    old_group.add_argument("-t", "--type", metavar="", default="A", choices=RECORD_TYPES, help=f'解析记录类型, 可用值：{"|".join(RECORD_TYPES)}, 默认值: "A"')
    old_group.add_argument("-l", "--line", metavar="", default=default_line, help=f'解析线路名，默认值: "{default_line}"')
    old_group.add_argument("-L", "--ttl", metavar="", type=int, default=600, help="解析记录缓存时间，默认值: 600")
    old_group.add_argument("--record-id", metavar="", help="解析记录ID, 如果提供了记录ID，其他参数将失效")

    new_group = change_parameter.add_argument_group("new record arguments")
    new_group.add_argument("-nn", "--new-name", metavar="", help="子域名")
    new_group.add_argument("-nv", "--new-value", metavar="", help="解析记录值")
    new_group.add_argument("-nt", "--new-type", metavar="", choices=RECORD_TYPES, help=f'解析记录类型, 可用值：{"|".join(RECORD_TYPES)}')
    new_group.add_argument("-nl", "--new-line", metavar="", help='解析线路名')
    new_group.add_argument("-nL", "--new-ttl", metavar="", type=int, help="解析记录缓存时间")
    dnscli.add_subparser(name="change", help="修改/更新 DNS 解析记录", parents=[auth_parameter, prettyprint_parameter, change_parameter], aliases=["update"])

    # delete or del
    delete_parameter = dnscli.public_parameter(default_type=default_type, default_line=None)
    delete_parameter.add_argument("--record-id", metavar="", help="解析记录ID, 如果提供了记录ID，其他参数将失效")
    dnscli.add_subparser(name="delete", help="删除 DNS 解析记录", parents=[auth_parameter, prettyprint_parameter, delete_parameter], aliases=["del"])

    # configure or config
    dnscli.add_subparser("configure", help="配置 API 请求密钥", parents=[auth_parameter], aliases=["config"])

    args = dnscli.parse_args()
    if args.func is None:
        raise SystemExit(dnscli.parser.print_help())
    return args

if __name__ == "__main__":
    print(main_cli("dnspod"))