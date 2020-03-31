# 3cloud
三清网盾（云勺盾）：Web应用WAF SSH防爆破 攻击日志实时可视化



#### 安装：

1、修改nginx_3cloud_lua文件夹中的www.conf部分，设置需要防护的网站根目录和location等配置

2、将error.html放到网站根目录下

3、将项目的nginx_3cloud_lua文件夹放到/usr/下并更名为3cloud

4、在openresty的nginx.conf配置中加入

```
default_type application/octet-stream;

charset UTF-8;

##the 3cloud_view

upstream flask{

​    server 127.0.0.1:8000;

​    keepalive 100;

}

##the 3cloud_waf

upstream aiwaf{

​    server 127.0.0.1:5000;

​    keepalive 100;

}

include /usr/3cloud/www.conf;
```

5、修改3cloud_waf下的waf.py文件中posturl地址，准备将结果发送到日志服务器（日志服务器可以自行设定）

如果搭配3cloud_view可视化，可以在nginx的conf.d加入下述nginx配置，将本地接收日志消息并且存储mongodb和可视化

```
server{

​    listen 80;

​    server_name 3cloudlog.yourhost.com;

​    access_log /var/log/nginx/3cloud_access.log;

​    error_log /var/log/nginx/3cloud_error.log;

​    location / {

​        proxy_set_header Host $host;

​        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

​        proxy_pass http://flask/;

​    }

 

}
```

6、执行waf.py等待openresty转发流量，将监听5000端口

7、修改3cloud_view下py_mogo.py文件中的mongodb配置并执行，将监听8000端口



#### 展示



![云勺盾功能图](https://github.com/MRdoulestar/3cloud/blob/master/imgs/function.png?raw=true)

![云勺盾拦截提示](https://github.com/MRdoulestar/3cloud/blob/master/imgs/alert.png?raw=true)

![云勺盾可视化全球图](https://github.com/MRdoulestar/3cloud/blob/master/imgs/map.png?raw=true)

![云勺盾可视化地球](https://github.com/MRdoulestar/3cloud/blob/master/imgs/globe.png?raw=true)

