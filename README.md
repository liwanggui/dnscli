# dnscli

DNS 命令行工具，支持域名解析记录的增删改查。 现已适配以下DNS服务商

- [阿里云](https://www.aliyun.com/)
- [腾讯云](https://cloud.tencent.com/)
- ...

## 安装

```bash
pip install dnscli
```

## 命令说明

- alidns: 阿里云 DNS 命令行工具
- dnspod: 腾讯云 DNS 命令行工具

## 使用说明

以 alidns 为例，其他命令使用方式类似

1. 配置 API 信息
    ```bash
    alidns configure --secret-id xxxxx --secret-key xxxxx
    ```
2. 查看域名列表
    ```bash
    alidns list-domain
    +------+---------------+--------------+--------+
    | 序号 | 域名           | 创建时间       | 记录数  |
    +------+---------------+--------------+--------+
    | 1    | test1.com     | 1592393820.0 | 9      |
    | 2    | test2.com     | 1592393160.0 | 6      |
    | 3    | test.cn       | 1448347860.0 | 14     |
    +------+---------------+--------------+--------+
    ```
3. 查看域名解析记录
    ```bash
    alidns list test.cn
    +------+--------+----------+-------------------------------------+---------+-----+--------------------+--------------+--------------+
    | 序号 | 子域名 | 记录类型 | 记录值                              | 线路    | TTL | 记录 ID            | 创建时间     | 更新时间     |
    +------+--------+----------+-------------------------------------+---------+-----+--------------------+--------------+--------------+
    | 1    | tt     | AAAA     | ::12                                | default | 600 | 913272411669522432 | 1724317196.0 | 1724317196.0 |
    | 2    | wfga   | CNAME    | www.baidu.com                       | default | 600 | 913225766055557120 | 1724294954.0 | 1724311099.0 |
    +------+--------+----------+-------------------------------------+---------+-----+--------------------+--------------+--------------+
    ```
4. 添加域名解析记录
    ```bash
    alidns create test.cn -n abc -v 1.2.3.4
    +------+--------+----------+---------+---------+-----+----------+
    | 序号 | 子域名 | 记录类型 | 记录值  | 线路    | TTL | 执行状态 |
    +------+--------+----------+---------+---------+-----+----------+
    | 1    | abc    | A        | 1.2.3.4 | default | 600 | 创建成功 |
    +------+--------+----------+---------+---------+-----+----------+
    ```
5. 更新域名解析记录
    ```bash
    alidns update test.cn -n abc -v 1.2.3.4 -nn foo -nv 22.2.111.1
    +------+--------+----------+------------+---------+-----+--------------------+----------+
    | 序号 | 子域名 | 记录类型 | 记录值     | 线路    | TTL | 记录ID             | 执行状态 |
    +------+--------+----------+------------+---------+-----+--------------------+----------+
    | 1    | foo    | A        | 22.2.111.1 | default | 600 | 913431792258240512 | 修改成功 |
    +------+--------+----------+------------+---------+-----+--------------------+----------+
    ```
6. 删除域名解析记录
    ```bash
    alidns delete test.cn -n foo
    +------+--------+----------+------------+---------+-----+----------+
    | 序号 | 子域名 | 记录类型 | 记录值     | 线路    | TTL | 执行状态 |
    +------+--------+----------+------------+---------+-----+----------+
    | 1    | foo    | A        | 22.2.111.1 | default | 600 | 删除成功 |
    +------+--------+----------+------------+---------+-----+----------+
    ```
    > 注意：
    > 1. 删除记录时, 子域名为必须参数
    > 2. 删除记录时，只指定子域名，删除与子域名匹配的所有记录。
    > 3. 如需删除特定的记录，请指定 记录ID (--record-id)

## 开发测试

1. 创建虚拟环境
2. 安装 `pip install -e .`
