【一】阿里云安装环境及步骤：
1，申请ECS服务器，选择Alibaba Cloud Linux 3.2104 LTS 64位操作系统。
该系统版本新，所以支持常用开发语言环境。
2，ECS实例启动后，通过自动化运维页面，安装Docker、NodeJs、Python3.13环境有的新版本。
3，安装git。
sudo yum update -y
sudo yum install -y git
4，下载代码：
git clone https://github.com/mssnzxm/banana-slides
git pull

【二】自己编译安装
cd banana-slides
##安装uv工具
curl -LsSf https://astral.sh/uv/install.sh | sh
##安装依赖
uv sync
##配置环境变量
cp .env.example .env
进入前端目录
cd frontend
npm install
##启动后端服务
cd backend
uv run alembic upgrade head && uv run python app.py
由于uv默认用了python3.14导致错误，需要在项目下，增加一个配置文件：
# 在backend目录下新增uv.toml文件，内容如下：
[python]
version = "3.13.3"
path = "/usr/local/python3.13/bin/python3.13"


【三】通过docker来一站式编译安装。
##编译
docker compose build --no-cache
##启动服务
docker compose up -d
##停止服务
docker compose down