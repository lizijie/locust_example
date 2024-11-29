本工程locust_example，基于压测工具[locust](https://github.com/cloudwu/sproto)，数据协议[Sproto](https://github.com/cloudwu/sproto)，[python websocket-client](https://github.com/websocket-client/websocket-client)和本人过往游戏开发的经验，封装的一个示例程序。

# 目录
- proto 协议配置文件.sproto
- simple_robot 基于locust的压测前端
- simple_server 处理simple_robot请求的简单后端服务

# 安装&运行
* 首次运行前先安装
```shell
cd ./simple_server/ && sh install.sh
cd ./simple_robot/ && sh install.sh
```

* 运行样例
```shell
cd ./simple_server/ && sh start.sh
cd ./simple_robot/ && sh start.sh
```

# 业务压测
mods目录下是各个模块的对象，除了示例role_mod，你还可以增加hero_mod，friend_mod和battle_mod等，每个xxx_mod里，你应该做的事
- 定义tasks压测任务
- 监听网络协议，处理业务
- 缓存后端返回的数据,如role_mod.my_value，方便在task做判断走不同压测逻辑

# 关于locust

***我以下谈及的内容，基于版本locust==2.32.1***

***我以下谈及的内容，基于版本locust==2.32.1***

***我以下谈及的内容，基于版本locust==2.32.1***

若对部分内容不理解，先看看官方教程 [https://docs.locust.io/en/stable/](https://docs.locust.io/en/stable/)

##  locust约定

- 压测逻辑的入口是各个User子类。当然也可以将locust以第三方库的形式导入你的python工程，见官方文档[Using Locust as a library](https://docs.locust.io/en/stable/use-as-lib.html#using-locust-as-a-library)，这是更重度使用locust的方案，此处不讨论。
- 每个User代表着一个网络连接（如HttpUser）、多份压测TaskSet

我的理解是以上约定不适合游戏场景

## User
官方以及网上的教程，都偏向以网络协议的角度去包装User，如WebSocketUser，TcpUser。我认为这种将网络协议和User强行绑定的概念不好，它们完全是两个概念，两者应该用组合的方式联系。游戏场景，有时候会多开socket，如大厅服和战斗服连接，它应该是同一个user主体，并且是数据状态共享的。而locust看待user是一个独单的主体，也没提供User间通信和共享数据的接口。

## TaskSet
User.tasks是用来定义压测任务，但请注意它是一个静态成员，静态成员，静态成员！！！！ locust内部每次随机选中某个task class并创建实例，注意注意~~！我说的是每次每次都创建实例。具体可以去看看启动TaskSet的代码[user.run](https://github.com/locustio/locust/blob/2.32.1/locust/user/users.py#L142)和[DefaultTaskSet.execute_task](https://github.com/locustio/locust/blob/master/locust/user/task.py#L467)
* TaskSet是一个临时对象，不要在TaskSet里存放要共享的数据状态。
* 小心动态添加TaskSet，因为多个User对象，都会执行添加TaskSet的代码，将会导致重复添加了多个TaskSet

对于游戏场景，我们需要角色登录成功后，才能执行压测逻辑。locust控制TaskSet的启动时机，需要重写User.start，见示例GameUser.start

以上问题可以通过，改写locust内部流程，深度制定解决[Using Locust as a library](https://docs.locust.io/en/stable/use-as-lib.html#using-locust-as-a-library)。
前提你对locust源码有深度了解，hold得住locust的版本变化。


# TODO:
- mods目录路径可配置化
- proto目录路径可配置化
- game_socket细化报告日志
