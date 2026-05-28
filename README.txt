AI 图片工具箱 - 使用说明
============================

一、快速启动
-----------
1. 先去 https://replicate.com/account/api-tokens 注册并获取免费 API Token
2. 复制 .env.example 为 .env，填入你的 Token
3. 双击 start.bat 启动服务
4. 浏览器打开 http://localhost:5000

二、四大功能
-----------
1. AI 图片增强 - 使用 Real-ESRGAN 超分辨率模型，提升图片清晰度
2. AI 背景移除 - 自动识别主体并移除背景，支持人物/商品/物体
3. 老照片修复 - 使用 GFPGAN 修复模糊面容，还原清晰照片
4. AI 生图 - 使用 Stable Diffusion XL 根据文字描述生成图片

三、赚钱方式
-----------
1. Google AdSense 广告：
   - 去 https://adsense.google.com 注册
   - 网站通过审核后，替换 HTML 底部的 ca-pub-XXXXXXXXXXXXXXXX
   - 广告会自动展示在页面中的 #1 和 #2 广告位

2. 联盟营销：
   - 在页面中加入相关产品推荐链接（修图软件、AI服务等）
   - 通过佣金赚钱

3. 高级功能付费：
   - 无水印高清下载
   - 批量处理
   - API 接口

四、部署上线
-----------
方式一：免费部署到 Vercel
  1. 安装 Vercel CLI: npm i -g vercel
  2. 在项目目录运行: vercel
  3. 绑定自定义域名

方式二：部署到云服务器
  1. 购买一台最低配云服务器（阿里云/腾讯云，约 50元/月）
  2. 安装 Python 3.10+
  3. 上传项目文件
  4. 安装依赖: pip install -r requirements.txt
  5. 使用 gunicorn 运行: gunicorn -w 4 -b 0.0.0.0:5000 app:app
  6. 配置 Nginx 反向代理 + SSL 证书（Let's Encrypt 免费）

五、运营推广
-----------
1. SEO：优化标题、描述、关键词，提交到百度/Google
2. 社交媒体：在抖音/小红书/微博发布使用教程
3. 工具导航站：提交到ai-bot.cn、tool.lu等导航站
4. 内容营销：写AI图片处理相关的公众号文章

六、成本预估
-----------
- 域名：约 60元/年
- 服务器：约 50-100元/月（或免费使用 Vercel）
- Replicate API：按量计费，约 0.01-0.05元/张图片
- 建议先充值 50-100元到 Replicate 测试
