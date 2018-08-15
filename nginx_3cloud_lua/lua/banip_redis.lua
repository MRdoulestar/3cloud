-- Lua
local IDS = require('IDS')
if not IDS then
    ngx.say("Faild to require 3cloud")
end

local function close_redis(red)
    if not red then
        return
    end
    --释放连接(连接池实现)
    local pool_max_idle_time = 10000 --毫秒
    local pool_size = 100 --连接池大小
    local ok, err = red:set_keepalive(pool_max_idle_time, pool_size)

    if not ok then
        ngx_log(ngx_ERR, "set redis keepalive error : ", err)
    end
end

-- 连接redis
local redis = require('resty.redis')
local red = redis.new()
red:set_timeout(1000)

local ip = "127.0.0.1"  ---修改变量
local port = "6379" ---修改变量
local ok, err = red:connect(ip,port)
if not ok then
    return close_redis(red)
end

local clientIP = ngx.req.get_headers()["X-Real-IP"]
if clientIP == nil then
   clientIP = ngx.req.get_headers()["x_forwarded_for"]
end
if clientIP == nil then
   clientIP = ngx.var.remote_addr
end

--获取请求的URL
local reqURL = ngx.var.request_uri

local incrKey = "user:"..clientIP..":freq"
local blockKey = "user:"..clientIP..":block"

local is_block,err = red:get(blockKey) -- check if ip is blocked
--ngx.say(tonumber(is_block))
if tonumber(is_block) == 1 then
    ngx.exit(499)
    close_redis(red)
end

--攻击识别
local tell_atk = IDS.IDS(reqURL, clientIP, ngx)
if tell_atk ~= '1' then
    inc  = red:incr(incrKey)
    if inc < 5 then
       inc = red:expire(incrKey,60)
    end

    if inc > 5 then --1分钟内5次以上识别为攻击即进行封禁，会阻止1分钟的访问
        red:set(blockKey,1) --设置block 为 True 为1
        red:expire(blockKey,60)
    end
    ngx.exec("/error.html")
else
    return
end

close_redis(red)
