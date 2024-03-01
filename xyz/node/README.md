## Node 部分

### 介绍

我们利用 Node 作为容器，可以在其内部根据 config 实例化出不同的 Agent，比如 LLMAgent，FunctionalAgent， ConsciousnessAgent

若无必要，勿增实体。

config 应在最简单、最少的设置的基础上，能够满足我们对他的任务的需求

开闭原则，功能独立

### Config 设计

我们需要利用 json 对象来储存 Node 数据。我们要对 config 的数据进行设计：

```python
node_config = {
    "type" : "",
    "memory_config" : {},

    # LLMAgent part
    # 要包含 模型相关的信息
    "role_config" : {},

    # FunctionalAgent part
    "tools_config" : [{}, {}]

    # ConsciousnessAgent part
    "c_config" : {}
}

role_config = {
    "role_description" : "",
    "template" : "",
    "connection_info" : "",
}

tools_config = {


}


function_call_template = {


}


company_config = {
    "staffs" = [],
}

```


TODO:

1. 如何嵌套？
2. staffs 和 supervisor 之间到底该怎么进行通信。
3. 


