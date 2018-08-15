--3cloud waf
--author:yunsle
local _M = {}
local headers = ngx.req.get_headers()
local reqUri = ngx.var.request_uri
local uri = ngx.var.uri

-- parse the dict
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

function _M.IDS(reqURL, ip)
	--post the url and user ip to the aiwaf.
	local resp = ngx.location.capture("/aiwaf",{
		methoc = ngx.HTTP_GET,
		args = {uri=reqURL,remoteip=ip}
	})
	--get the aiwaf result and return the html to user
	if resp then
		local body = tostring(resp.body)
		local tab = dict_parse(body)
		if tab[2] == '1' then
			return '1'
		else
			--ngx.exec("/error.html")
			return '0'
		end
	else
		--ngx.say("sorry,the waf is down!")
		return '-1'
	end
end

return _M
