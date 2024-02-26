## Memory (NetMind.AI-XYZ)

本文档不是正式文档，只是为了方便 team 内部沟通，进行编写的。
Author: BlackSheep-Team

### 文件介绍：

```bash
memory
├── _embedding_setting
│   ├── EmbeddingTypeEnum.py
│   ├── IdxTypeEnum.py
│   ├── __init__.py
│   └── MetricTypeEnum.py
├── __init__.py
├── BasicAttributeStorage.py
├── BasicMemoryMechanism.py
├── MemoryAgent.py
├── MemoryClient.py
├── _memory_config_template.py
├── README.md
└── utils.py
```

Group 1:
`_embedding_setting/*`, `BasicAttributeStorage.py`, `BasicMemoryMechanism.py`
我们利用这些 python 脚本，实现了最基础的 Milvus 向量数据库或者 MongoDB。
我们可一利用这些实例化对象 `BasicAttributeStorage, BasicMemoryMechanism` 对数据库进行 增删改查。

Group 2:
`MemoryClient.py`, `MemoryAgent.py`
在实际项目中我们用到的接口：
`MemoryClient` 在一个项目中起到与服务连接的能力，独例模式，在一个项目的 runtime 中只有一个实例化对象。
MemoryAgent` 在一个项目中会有许多个不同的实例化对象，本身并不与服务器上的database进行连接，而是通过 Client 进行连接。
好处是：不需要每个 Agent 都单独和远程服务创建连接。（这一点需要 Zhouhan 进行确认，是不是我们想要的这种形式。）

一些必要的说明：
1. 连接数据库的时候，建议使用 `MemoryAgent` 根据 config 进行连接。如果那台服务器上有要链接的数据库，就会自动连接；如果没有，则根据 `db_name, collection_name, partition_name` 去创建。
2. config 用例 请看 `test/memory_test/unit_test_client.py` 文件和 `BasicMemoryMechanism.py`的构造函数。
3. 一个数据库要根据 `db_name, collection_name, partition_name` 去确定。 `memory_name` 只是我们用来给他起名用的，但是建议和 `collection_name` 或 `partition_name` 其中一个相等。 
4. 项目还在完善中，有更优雅的方式请尽管使用。
4. 可以对已有函数、方法、对象进行修改，但是要保证 所有的 test 文件能够顺利全部通过。

快速熟悉代码的方式：
1. 阅读代码：`BasicAttributeStorage.py`, `BasicMemoryMechanism.py`，`MemoryClient.py`, `MemoryAgent.py` 所有的功能内容都写在 docstring 里了。
2. 沟通，
   1. Zhouhan Zhang: `BasicAttributeStorage.py`, `BasicMemoryMechanism.py`
   2. Tianlei: 部署于 AWS EC2
   3. Bin Liang: `MemoryClient.py`, `MemoryAgent.py`
3. 看 test 文件，`NetMind_AI_XYZ/test/memory_test`.
   
    client_config 主要参数的说明:
     - `collection_name`: collection_name用于标识向量数据库中的一个collection. 一个collection通常用来存储一个agent的一类数据, 比如存储一个agent 的某一类知识. 一个collection 中每条数据需要有相同的metadata.
     - `partition_name`: partition_name 用于标识一个 collection 的子集. 一个collection 中的partition数量是有限的, 使用 partition 主要用于在collection的子集中做检索, 一个 collection 中不同partition有相同的metadata.
     - `db_name`: db_name 用来标识一个向量数据库的服务. 一个db_name有多个 collection, 不同collection可以有不同的metadata.
     - `memory_name`: 一个agent可能有多个collection, memory_name 用于在逻辑上区分一个agent的不同知识库或记忆库.

### 目前进展

#### Marketing 需求

经过和 He Yan 确认，我们目前的 client、agent 结构已经能够满足 Marketing 项目的需求。

#### 复杂 retrieval 方式开发

开发形式（暂定）：
1. 建立新的 branch
2. 在独立的 branch 内开发
3. 使用 PEP8 的规范，docstring用 numpy style。
   1. Class 命名：驼峰命名法
   2. 变量 命名：下划线命名法
   3. 命名尽量不要使用缩写
4. 对于 整个 memory 文件夹内的所有内容 都可以根据自己的需求进行增加或者修改。

目前目标：

1. 结构化搜索
2. 联想

以下内容仅仅是参考：
这两个功能都应该在 `MemoryAgent` 内部进行开发。

`MemoryAgent.structured_search(Chain, query)`:
1. MemoryAgent 有这个对象方法。
   1. 可以是多种形式，我只是打个比方，比如 
      1. `MemoryAgent.create_chain()`
      2. `MemoryAgent.chain["xxx"].search(quert)`
2. 定义 Chain 这个对象的形式。
   1. 如何创建这个对象，内部包含一个 类似TF.sequential() 的内容。
   2. 需要实现 Knowledge 1 -> Agent input -> Agent output -> Knowledge 2 -> ...

`MemoryAgent.associate(query)`
1. 比如，可以在指定步数内，重复 搜索、agent 处理、搜索....这个过程。
2. 重点是，在每一次 当前信息内容、信息量发生变化的时候，可以自行选择 下一个要去搜索的知识库是什么。

