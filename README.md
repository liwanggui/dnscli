# DNSCLI2

一个用于管理多云DNS记录的命令行工具，支持阿里云DNS、腾讯云DNS和Cloudflare DNS。

## 功能特点

- 支持阿里云DNS、腾讯云DNS和Cloudflare DNS
- 支持多配置管理
- 支持DNS记录的增删改查
- 支持Cloudflare CDN代理功能
- 命令行界面，操作简单直观

## 安装

```bash
pip install dnscli
```

## 使用方法

### 生成示例配置

```bash
dnscli config example
```

### 添加云服务商配置

```bash
# 添加阿里云配置
dnscli config configure --provider aliyun

# 添加腾讯云配置
dnscli config configure --provider tencent

# 添加Cloudflare配置
dnscli config configure --provider cloudflare
```

### 查看DNS记录

```bash
# 查看指定域名的所有记录
dnscli record list example.com

# 按记录类型筛选
dnscli record list example.com --type A
```

### 添加DNS记录

```bash
# 添加A记录
dnscli record add example.com www A "192.168.1.1"

# 添加CNAME记录
dnscli record add example.com www CNAME "cdn.example.com"

# 添加启用CDN代理的记录（仅Cloudflare）
dnscli record add example.com www A "192.168.1.1" --proxied
```

### 更新DNS记录

```bash
# 更新记录值
dnscli record update example.com <record-id> www A "192.168.1.2"

# 更新CDN代理状态（仅Cloudflare）
dnscli record update example.com <record-id> www A "192.168.1.2" --proxied true
```

### 删除DNS记录

```bash
dnscli record delete example.com <record-id>
```

## 许可证

MIT License