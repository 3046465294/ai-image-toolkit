# 部署指南

## 准备工作

1. 注册 Replicate 账号并获取 API Token: https://replicate.com/account/api-tokens
2. 复制 `.env.example` 为 `.env`，填入你的 `REPLICATE_API_TOKEN`
3. 购买一个域名（推荐 NameSilo/Cloudflare/阿里云，约 60 元/年）

---

## 方案一：Render.com 免费部署（推荐新手）

1. 把项目上传到 GitHub（私有或公开仓库）
2. 注册 https://render.com （用 GitHub 登录）
3. 点击 "New +" → "Web Service" → 选择你的仓库
4. Render 会自动读取 `render.yaml` 配置
5. 在 Environment Variables 中添加 `REPLICATE_API_TOKEN`
6. 点击 "Create Web Service"
7. 等待部署完成，你会得到一个 `xxx.onrender.com` 域名
8. 在 Render 设置中绑定自定义域名

**优点**: 免费、自动部署、无需管理服务器
**缺点**: 免费版 15 分钟无访问会休眠，国内访问可能较慢

---

## 方案二：Railway 部署

1. 注册 https://railway.app
2. 安装 Railway CLI: `npm i -g @railway/cli`
3. 在项目目录运行: `railway init`
4. 添加环境变量: `railway variables set REPLICATE_API_TOKEN=your_token`
5. 部署: `railway up`
6. 绑定域名

**优点**: 比 Render 快，免费额度充足
**缺点**: 需要信用卡验证

---

## 方案三：阿里云/腾讯云 VPS 部署（国内用户最佳）

### 购买服务器
- 阿里云 ECS 或腾讯云轻量应用服务器
- 配置: 1核2G，约 50-60 元/月
- 选择 CentOS 7.9 或 Ubuntu 22.04
- 选择香港/新加坡节点（免备案）或大陆节点（需要备案）

### 部署步骤

```bash
# 1. SSH 登录服务器
ssh root@你的服务器IP

# 2. 安装 Python 3.11
# Ubuntu:
sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip nginx -y

# 3. 上传项目文件
# 在本地电脑执行:
scp -r ai-image-toolkit root@你的服务器IP:/opt/

# 4. 在服务器上设置
cd /opt/ai-image-toolkit
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. 创建 .env 文件
echo "REPLICATE_API_TOKEN=your_token_here" > .env

# 6. 配置 systemd 服务
sudo tee /etc/systemd/system/ai-toolkit.service << 'SERVICE'
[Unit]
Description=AI Image Toolkit
After=network.target

[Service]
User=root
WorkingDirectory=/opt/ai-image-toolkit
Environment="PATH=/opt/ai-image-toolkit/venv/bin"
ExecStart=/opt/ai-image-toolkit/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# 7. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable ai-toolkit
sudo systemctl start ai-toolkit

# 8. 配置 Nginx 反向代理
sudo tee /etc/nginx/sites-available/ai-toolkit << 'NGINX'
server {
    listen 80;
    server_name 你的域名.com;

    client_max_body_size 15M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 180s;
    }
}
NGINX

sudo ln -s /etc/nginx/sites-available/ai-toolkit /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 9. 安装 SSL 证书（Let's Encrypt 免费）
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d 你的域名.com
```

---

## 方案四：Docker 部署

```bash
# 在服务器上
docker build -t ai-toolkit .
docker run -d -p 5000:5000 \
  -e REPLICATE_API_TOKEN=your_token \
  -v $(pwd)/uploads:/app/uploads \
  --restart always \
  --name ai-toolkit \
  ai-toolkit
```

---

## 部署后检查清单

- [ ] 网站能正常访问
- [ ] 上传一张图片测试 AI 增强功能
- [ ] `/privacy` 页面存在
- [ ] `/ads.txt` 文件可访问
- [ ] HTTPS 正常工作
- [ ] 提交到 Google Search Console
- [ ] 申请 Google AdSense
