# Kanojo

<div align="center">
    <img src="images/favicon.ico" alt="logo" width="100">
</div>

## **部署**

1. 从 [这里](https://github.com/plsy1/kanojo/blob/main/docker/compose.yml) 下载 `compose.yml` 文件到你的服务器
2. 运行此命令来启动所有服务：`docker compose up -d`
3. 详细可参考此[文档](https://zread.ai/plsy1/kanojo)
   
## **配置**

- 在首次启动后，可以从设置页面调整环境变量。
- 初始启动时，会生成一个随机密码，可在容器日志中找到该密码。


## **功能**

- **数据浏览**：支持查看包括影片详情、标签、演员信息等。
- **内容订阅**：按演职员/影片订阅。
- **搜索下载**：搜索影片并推送到下载器，集成下载器管理功能。
- **自动归档**：下载内容自动按演职员名称进行文件夹分类。
- **消息通知**：订阅/下载信息可推送到消息通知工具。
- **文件过滤**：可配置关键字过滤，取消下载种子中的广告文件。
