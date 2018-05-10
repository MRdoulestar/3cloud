local remoteIp = ngx.var.remote_addr
local headers = ngx.req.get_headers()
local reqUri = ngx.var.request_uri
local uri = ngx.var.uri

--ngx.exit(ngx.HTTP_FORBIDDEN)
local resp = ngx.location.capture("/aiwaf",{
	methoc = ngx.HTTP_GET,
	args = {uri=reqUri}
})

function dict_parse(body)
	local tab = {}
	local a = string.find(body,"\'")
	local b = string.find(body,"\'",a+1)
	local c = string.find(body,"\'",b+1)
	local d = string.find(body,"\'",c+1)
	local e = string.find(body,"\'",d+1)
	local f = string.find(body,"\'",e+1)
	local g = string.find(body,"\'",f+1)
	local h = string.find(body,"\'",g+1)
	
	local uri = string.sub(body,c+1,d-1)
	local res = string.sub(body,g+1,h-1)
	table.insert(tab,uri)
	table.insert(tab,res)
	return tab
end

if resp then
	local body = tostring(resp.body)
	local tab = dict_parse(body)
	if tab[1] == '1' then
		return
	else
		ngx.say('your request uri:'..tab[2]..' is a attack!')
		ngx.say('<br>we will log it')
		--ngx.exec("/error.html")
	end
else
	ngx.say("sorry,the waf is down!")
end
--ngx.exec("/error.html")
