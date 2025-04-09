# 🛰️ worker-monitor

`worker-monitor` 是一个为 Kubernetes 工作节点设计的轻量级监控组件，用于采集每秒级别的系统资源状态（CPU、内存、网络速率）以及节点间网络延迟，并通过 HTTP 接口供调度器访问。

本项目用于支持深度强化学习调度器在 5GC 网络中的感知能力。

---

## ✨ 功能特性

- 每秒采集：
  - 🧠 CPU 使用率
  - 🧮 内存使用率
  - 🌐 网络接收/发送速率（Mbps）
- 每 5 秒探测：
  - 📡 与其他节点的网络延迟（ms）
- HTTP REST 接口提供 JSON 格式 `/stats` 响应
- 支持 systemd 启动，开机自启
- 易于集成、扩展和容器化

---

## 📦 安装与部署

### 1️⃣ 准备 `peers.txt`

在根目录创建一个名为 `peers.txt` 的文本文件，用于定义需要探测延迟的节点列表：

```txt
192.168.1.101
192.168.1.102
```

---

### 2️⃣ 一键安装（建议在每个工作节点执行）

```bash
curl -fsSL https://raw.githubusercontent.com/tjkkking/worker-monitor/main/install_monitor.sh | bash
```

> 📌 需要预先确保 `peers.txt` 已存在于仓库中。

---

### 3️⃣ 启动验证

```bash
curl http://localhost:8080/stats
```

预期返回如下结构：

```json
{
  "nodeName": "node-1",
  "timestamp": 1712640000,
  "cpu": 0.35,
  "mem": 0.72,
  "net": {
    "rx": 5.8,
    "tx": 3.2
  },
  "latency": {
    "192.168.1.101": 0.8,
    "192.168.1.102": 1.3
  }
}
```

---

## 🔧 手动操作命令

| 操作                   | 命令                                    |
| ---------------------- | --------------------------------------- |
| 查看运行状态           | `systemctl status worker-monitor`       |
| 重启服务               | `sudo systemctl restart worker-monitor` |
| 修改监控代码后重载服务 | `sudo systemctl daemon-reload` + 重启   |
| 卸载监控服务           | `sudo ./uninstall_monitor.sh`           |

---

## 🧪 开发依赖（本地运行）

```bash
pip install fastapi uvicorn psutil ping3
uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## 📁 目录结构

```text
worker-monitor/
├── main.py                # 监控主程序
├── peers.txt              # 节点列表文件
├── requirements.txt       # Python 依赖
├── install_monitor.sh # 安装脚本
├── uninstall_monitor.sh # 卸载脚本
└── README.md              # 使用说明
```

---

## 📮 接口说明

### `GET /stats`

返回当前节点的监控状态。

字段说明：

| 字段      | 类型   | 说明                 |
| --------- | ------ | -------------------- |
| nodeName  | string | 节点主机名           |
| timestamp | int    | 当前时间戳           |
| cpu       | float  | CPU 使用率（0~1）    |
| mem       | float  | 内存使用率（0~1）    |
| net.rx    | float  | 接收速率（Mbps）     |
| net.tx    | float  | 发送速率（Mbps）     |
| latency   | dict   | 与各节点的延迟（ms） |

---

## 📄 License

MIT License © 2024 [tjkkking](https://github.com/tjkkking)
