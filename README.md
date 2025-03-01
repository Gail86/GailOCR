# GailOCR
DDDDOCR
 增强版DDDDOCR

* StupidOCR 是一个简单的 OCR（光学字符识别）服务，支持图像中的文本提取和验证授权功能。
## 主要特性
  - **Base64 图像处理**：接收 Base64 编码的图像数据进行 OCR 处理。
- **授权验证**：支持基于密钥的授权验证机制。
- **错误处理**：提供友好的错误信息和日志记录功能。

## 使用说明

1. 发送 POST 请求到 `/api/ocr/image` 端点，请求体中包含 Base64 编码的图像数据和授权密钥。
2. 返回 OCR 结果或相应的错误信息。
## 特别说明，及改动事宜
- ** 此版本注释掉了原作者的Github地址，避免由于打不开Github导致无法打开docs页面。
- ** [原项目地址](https://github.com/81NewArk/StupidOCR)
- **授权验证**：允许通过配置文件增加或者删除授权key，并且提供授权开关。
- **自动初始化**：增加了对使用库的自动安装初始化步骤，避免因为环境问题导致无法启动。
- **端口自定义**：配置文件里增加了端口项，避免编译成exe后无法修改端口的问题。
