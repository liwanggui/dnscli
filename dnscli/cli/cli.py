import sys
import click

from .config import config
from .domain import domain
from .record import record
from ..version import __version__

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "-v", "--version", prog_name='dnscli', message='%(prog)s %(version)s')
def cli():
    """dnscli - 一个用于管理多云DNS记录的命令行工具"""
    pass

@cli.command()
def completion():
    """开启命令行自动补全"""
    if sys.platform == 'win32':
        click.echo('Windows 系统不支持自动补全')
        return
    prog_name = __name__.split('.')[0]
    cmd = f'$ eval "$(_{prog_name.upper()}_COMPLETE=bash_source {prog_name})"'
    click.echo(f"""\
{click.style("开启 BASH 自动补全，步骤如下:", bold=True)}
1. 复制以下命令，写入 ~/.bashrc
    {click.style(cmd, fg='green')}     
2. 重新加载 ~/.bashrc
    {click.style('$ source ~/.bashrc', fg='green')}
> 其他 SHELL 自动补全，参考官方文档: https://click.palletsprojects.com/en/stable/shell-completion/""")

# 添加子命令
cli.add_command(config)
cli.add_command(domain)
cli.add_command(record)

if __name__ == '__main__':
    cli()