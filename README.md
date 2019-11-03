# SmartContract-Env

智能合约题目部署环境

## 使用说明

使用前需填写 `src` 目录下的 `config.py` 文件，内有如下几个关键字段：

```python
#!/usr/bin/python3

HOST = '0.0.0.0'
PORT = 10000                    # 端口

FLAG_PATH = '/flag'             # 对应相应的 flag 路径
SOURCE_PATH = '/demo.sol'       # 对应相应的源码路径
CONTRACT_NAME = 'Challenge'     # 对应的合约名
EVENT_NAME = 'GetFlag'          # 获得 flag 对应的 Event

INFURA_PROJECT_ID = ''          # Project ID of infura
```

其中最为关键的是 `INFURA_PROJECT_ID`，需要到 https://infura.io/ 上注册后填入相应 Project ID
　
## 设计说明

用 python3 的 tcpserver 简单实现了个智能合约类型题目的自动化分发环境，题目的分发逻辑如下：

1. 随机生成外部地址，由 metamask 提供的水龙头向外部地址转入 1 ETH
2. 在合约源码加入一些随机无意义的变量后进行编译
3. 利用随机生成的外部地址部署合约
4. 程序返回生成的合约地址

## 总结

为了减少智能合约题目抄作业和捣乱的现象所做的一个智能分发题目的平台。然后加上了随机变量影响合约的字节码，防止通过相似合约的来定位所有题目的合约地址。

