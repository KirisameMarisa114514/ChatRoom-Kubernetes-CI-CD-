# 使用 Nginx 提供前端静态页面
FROM nginx:alpine
# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf
# 复制前端文件
COPY index.html /usr/share/nginx/html/index.html
COPY css /usr/share/nginx/html/css 
COPY js /usr/share/nginx/html/js
# 暴露 Nginx 默认端口
EXPOSE 80
