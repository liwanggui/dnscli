from .cli import main_cli, write_config, read_config, prettyprint
from ..dns.dnspod import DnsPodApi

DNS_SERVER = "dnspod"

def get_domains(dns, header=True, border=True, number=True):
    title = ("域名", "创建时间", "记录数")
    data = [[d.domain_name, d.create_time, d.record_count] for d in dns.get_domain()]
    return prettyprint(title, data, header=header, border=border, number=number)

def get_lines(dns, args, header=True, border=True, number=True):
    title = ["线路名"]
    result = dns.get_lines(args.domain)
    data = [[v] for v in result]
    return prettyprint(title, data, header=header, border=border, number=number)

def get_records(dns, args, header=True, border=True, number=True):
    title = ("子域名", "记录类型", "记录值", "线路", "TTL", "记录 ID", "创建时间", "更新时间")
    record_list = dns.get_record(domain=args.domain, sub_domain=args.name, record_type=args.type, line=args.line)
    data = [[r.sub_domain, r.type, r.value, r.line, r.ttl, r.record_id, r.create_timestamp, r.update_timestamp] for r in record_list]
    data = sorted(data, key= lambda x: x[1]) # 按记录类型排序
    return prettyprint(title, data, header=header, border=border, number=number)

def create_record(dns, args, header=True, border=True, number=True):
    title = ("子域名", "记录类型", "记录值", "线路", "TTL", "执行状态")
    data = []
    record = dns.get_record(domain=args.domain, sub_domain=args.name, record_type=args.type, line=args.line)
    if record and args.value in [r.value for r in record]:
        data.append([args.name, args.type, args.value, args.line, args.ttl, "记录已存在"])
    else:
        code = dns.create_record(domain=args.domain, sub_domain=args.name, record_type=args.type, value=args.value, line=args.line, ttl=args.ttl)
        data.append([args.name, args.type, args.value, args.line, args.ttl, "创建成功" if code else "创建失败"])
    prettyprint(title, data, header=header, border=border, number=number)

def _change_record(dns, args, header=True, border=True, number=True):
    title = ("子域名", "记录类型", "记录值", "线路", "TTL", "记录ID", "执行状态")
    data = []
    args.new_name = args.new_name or args.name
    args.new_type = args.new_type or args.type
    args.new_value = args.new_value or args.value
    args.new_line = args.new_line or args.line
    args.new_ttl = args.new_ttl or args.ttl

    if all(( 
        (args.new_name == args.name), 
        (args.new_type == args.type), 
        (args.new_value == args.value), 
        (args.new_line == args.line), 
        (args.new_ttl == args.ttl) 
    )):
        raise SystemExit("记录值无变化，请修改后重试")

    data.append([args.new_name, args.new_type, args.new_value, args.new_line, args.new_ttl, args.record_id])

    if dns.change_record(domain=args.domain, sub_domain=args.new_name, record_id=args.record_id, 
                            record_type=args.new_type, value=args.new_value, line=args.new_line, ttl=args.new_ttl):
        data[0].append("修改成功")
    else:
        data[0].append("修改失败")
    return prettyprint(title, data, header=header, border=border, number=number)

def change_record(dns, args, header=True, border=True, number=True):
    if args.name and args.value:
        records = dns.get_record(domain=args.domain, sub_domain=args.name, 
                                 record_type=args.type, line=args.line, keyword=args.value)
        if not records:
            raise SystemExit("您要更改的 DNS 记录不存在，请检查参数后重试")
        for r in records:
            if args.name == r.sub_domain and args.value == r.value and args.type == r.type and args.line == r.line:
                args.record_id = r.record_id
                break
    elif args.record_id:
        records = dns.get_record(domain=args.domain)
        if not records:
            raise SystemExit("您要更改的 DNS 记录不存在，请检查后重试")
        if not records or args.record_id not in [r.record_id for r in records]:
            raise SystemExit(f"记录ID 不存在: {args.record_id}")
        for r in records:
            if r.record_id == args.record_id:
                args.name = r.sub_domain
                args.type = r.type
                args.value = r.value
                args.line = r.line
                args.ttl = r.ttl
                break
    else:
        raise SystemExit("缺少必要的参数，请检查后重试")
    return _change_record(dns, args, header=header, border=border, number=number)

def delete_record(dns, args, header=True, border=True, number=True):
    if args.record_id:
        title = ("子域名", "记录ID", "执行状态")
        data = [[args.name, args.record_id, "删除成功" if dns.del_record(domain=args.domain, record_id=int(args.record_id)) else "删除失败"]]
        return prettyprint(title, data)
    
    if any((args.type, args.line)):
        print(args)
        record_list = dns.get_record(domain=args.domain, sub_domain=args.name, record_type=args.type, line=args.line)
        title = ("子域名", "记录类型", "记录值", "线路", "TTL", "执行状态")
        data = []
        if not record_list:
            data.append([args.name, args.type, "", args.line, "", "无记录, 删除失败"])
            return prettyprint(title, data)
        for r in record_list:
            if dns.del_record(domain=args.domain, record_id=r.record_id):
                data.append([r.sub_domain, r.type, r.value, r.line, r.ttl, "删除成功"])
            else:
                data.append([r.sub_domain, r.type, r.value, r.line, r.ttl, "删除失败"])
        return prettyprint(title, data)
    
    title = ("子域名", "执行状态")
    data = [[args.name, "删除成功" if dns.del_record_by_domain(domain=args.domain, sub_domain=args.name) else "删除失败"]]
    return prettyprint(title, data, header=header, border=border, number=number)


def main():
    args = main_cli(DNS_SERVER, default_line="默认")
    # print(args)

    if args.func in ("configure", "config"):
        return write_config(DNS_SERVER, args.secret_id, args.secret_key)

    header = not args.no_header
    border = not args.no_border
    number = not args.no_number

    if all((args.secret_id, args.secret_key)):
        secret_id = args.secret_id
        secret_key = args.secret_key
    else:
        config = read_config(DNS_SERVER)
        secret_id = config["secret_id"]
        secret_key = config["secret_key"]

    if not all((secret_id, secret_key)):
        raise SystemExit("必须同时提供 secret_id 和 secret_key, 请检查配置文件或命令行参数")

    dns = DnsPodApi(secret_id, secret_key)

    if args.func in ("list-line", "ll"):
        return get_lines(dns, args, header=header, border=border, number=number)

    if args.func in ("list-domain", "ld"):
        return get_domains(dns, header=header, border=border, number=number)

    if args.func in ("list", "ls"):
        return get_records(dns, args, header=header, border=border, number=number)
    
    if args.func in ("create", "add"):
        return create_record(dns, args, header=header, border=border, number=number)

    if args.func in ("change", "update"):
        return change_record(dns, args, header=header, border=border, number=number)

    if args.func in ("delete", "del"):
        return delete_record(dns, args, header=header, border=border, number=number)