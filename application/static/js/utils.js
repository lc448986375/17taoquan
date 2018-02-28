/**
 * 加载script和css
 * 	script 加载script
 * 	css 加载css
 */
var Load = {
	script : function(url){
		$.getScript(url);
	},

	css : function(url){
		document.write("<link rel='stylesheet' type='text/css' href=' "+ url +" '>");
	}
}

/**
 * Cookie操作
 * 调用方式：
 * 	Cookie.add(name, value, expiresHours)
 * add 添加
 * get 获取
 * delete 删除
 */
var Cookie = {
	// 添加cookie
	// 	name 名
	// 	value 值
	// 	expiresHours 过期时间，单位小时
	add : function(name, value, expiresHours){
		value = escape(encodeURI(value));
		// escape() 函数对特殊符号转义，比如 ‘=’ 和 ‘;’ ，应为在cookie它们有特殊含义
		var strCookie = name + '=' + value;

		if(expiresHours > 0){
			var date = new Date();
			date.setTime(date.getTime() + expiresHours * 3600 * 1000);
			strCookie = strCookie + '; expires=' + date.toGMTString();
		}

		document.cookie = strCookie;
	},

	// 根据名获取cookie
	// 	name 名
	get : function(name){
		var strCookie = document.cookie;
		var arrCookie = strCookie.split('; ');

		for (var i = 0; i < arrCookie.length; i++) {
			var cookie = arrCookie[i].split('=');
			if(cookie[0] === name){
				// unescape() 对特殊字符串解码
				return unescape(decodeURI(cookie[1]));
			}
		};
		return null;
	},

	// 根据名删除cookie
	// 	name 名
	delete : function(name){
		var date = new Date();
		date.setTime(date.getTime() - 10000);
		document.cookie = name + '=destroy; expires=' + date.toGMTString();
	}
}

/**
 * Ajax封装
 * post 请求
 */
var Ajax = {
	post : function (url, param, success, fail, complete){
		$.post(url, param, function(data, stat){
			if(stat != 'success'){
				alert('网络连接失败...');
				return;
			}

			var res = null;
			var errMsg = "";
			try{
				res = JSON.parse(data);
			}catch(e){
				// console.log(e.name + ':'  + e.message);
				errMsg += "异常信息:[" + e.name + ':'  + e.message + "]\n";
			}
			if(!res){
				errMsg += "访问功能:[" + url + "]\n";
				errMsg += "发送的数据:[" + JSON.stringify(param) + "]\n";
				errMsg += "服务器返回信息:[" + data + "]";
				var msg = 'sorry, 服务器可能出错了.\n' + errMsg;
				alert(decodeURI(msg));
				return;
			}

			if(res.success == true){
				success && success(res.data);
			}else{
				var msg = decodeURI(res.msg);
				fail && fail(msg);
				//Notifier.failed(data.msg);
				alert('error:\n' + msg);
			}
		}).complete(function(){
			complete && complete();
		});
	}
}

var DateUtil = {
	format : function(str){
		if(str.length === 8){
			var year = str.substr(0, 4),
				month = str.substr(4, 2),
				date = str.substr(6, 2);

			return year + '-' + month + '-' + date;
		}else if(str.length === 14){
			var year = str.substr(0, 4),
				month = str.substr(4, 2),
				date = str.substr(6, 2),
				hour = str.substr(8, 2),
				minute = str.substr(10, 2),
				second = str.substr(12, 2);

			return year + '-' + month + '-' + date + ' ' + hour + ':' + minute + ':' + second;
		}else{
			return null;
		}
	},

	secondFormatTime:function(seconds){
    	return [parseInt(seconds / 60 / 60), parseInt(seconds / 60 % 60), parseInt(seconds % 60)].join(":").replace(/\b(\d)\b/g, "0$1");
	}
}


/**
 * 正则验证
 * 使用：
 * 		Check.email('lc448986375@163.com')
 */
var Check = {
	// 邮箱验证
	email : function(str){
		var reg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.+[a-zA-Z]{2,3}$/;

		return reg.test(str);
	},

	// 手机号验证
	phoneNumber : function(str){
		var reg = /^[1][358]{1}\d{9}$/;

		return reg.test(str);
	},

	// 身份证号校验
	idCard : function(str){
		var vaildCode = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
		var vaildCode2 = {
			0 : '1',
			1 : '0',
			2 : 'x',
			3 : '9',
			4 : '8',
			5 : '7',
			6 : '6',
			7 : '5',
			8 : '4',
			9 : '3',
			10 : '2'
		};
		var ids = str.split('');
		var idLastNum = ids[ids.length - 1];
		var pre17 = str.substr(0, 17);
		var sum = 0;

		// 1、相乘 求和
		for (var i = 0; i < ids.length - 1; i++) {
			sum += Number(ids[i]) * Number(vaildCode[i]);
		};

		//2、除以 11 取余
		var ba = sum % 11;

		//3、最后一位校验码
		var getLastNum = vaildCode2[ba];

		if(getLastNum != idLastNum){
			// return false;
			return pre17 + getLastNum;
		}

		return true;
	}

}

/**
 * 参数
 * @type {Object}
 */
var Param = {
	// 获取所有参数，返回Object类型，然后根据参数名获取对应的参数值
	urlArgsObj :function(){
		var url = location.search, // 参数
			str = '',
			params = {};
			
		if(url.indexOf('?') != -1){
			str = url.substr(1);
		}else{
			return null;
		}
		strs = str.split('&');
		for(var i = 0; i < strs.length; i++){
			var sub = strs[i].split('=');
			params[sub[0]] = unescape(sub[1]);
		}
		return params;
	},

	// 获取所有参数，返回array，当URL为 www.liuchang.org/blog/show/3.html 时使用。
	// 该方法返回的为 ['blog', 'show', '3.html']
	urlArgsArr:function(){
		var url = location.href,
			host = app_config['domain'],
			params = [];

		url = url.substr(url.indexOf(host) + host.length + 1);

		params = url.split('/');
		return params;
	}

}

function Base64() {

	// private property
	_keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

	// public method for encoding
	this.encode = function (input) {
		var output = "";
		var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
		var i = 0;
		input = _utf8_encode(input);
		while (i < input.length) {
			chr1 = input.charCodeAt(i++);
			chr2 = input.charCodeAt(i++);
			chr3 = input.charCodeAt(i++);
			enc1 = chr1 >> 2;
			enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
			enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
			enc4 = chr3 & 63;
			if (isNaN(chr2)) {
				enc3 = enc4 = 64;
			} else if (isNaN(chr3)) {
				enc4 = 64;
			}
			output = output +
					_keyStr.charAt(enc1) + _keyStr.charAt(enc2) +
					_keyStr.charAt(enc3) + _keyStr.charAt(enc4);
		}
		return output;
	}

	// public method for decoding
	this.decode = function (input) {
		var output = "";
		var chr1, chr2, chr3;
		var enc1, enc2, enc3, enc4;
		var i = 0;
		input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
		while (i < input.length) {
			enc1 = _keyStr.indexOf(input.charAt(i++));
			enc2 = _keyStr.indexOf(input.charAt(i++));
			enc3 = _keyStr.indexOf(input.charAt(i++));
			enc4 = _keyStr.indexOf(input.charAt(i++));
			chr1 = (enc1 << 2) | (enc2 >> 4);
			chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
			chr3 = ((enc3 & 3) << 6) | enc4;
			output = output + String.fromCharCode(chr1);
			if (enc3 != 64) {
				output = output + String.fromCharCode(chr2);
			}
			if (enc4 != 64) {
				output = output + String.fromCharCode(chr3);
			}
		}
		output = _utf8_decode(output);
		return output;
	}

	// private method for UTF-8 encoding
	_utf8_encode = function (string) {
		string = string.replace(/\r\n/g, "\n");
		var utftext = "";
		for (var n = 0; n < string.length; n++) {
			var c = string.charCodeAt(n);
			if (c < 128) {
				utftext += String.fromCharCode(c);
			} else if ((c > 127) && (c < 2048)) {
				utftext += String.fromCharCode((c >> 6) | 192);
				utftext += String.fromCharCode((c & 63) | 128);
			} else {
				utftext += String.fromCharCode((c >> 12) | 224);
				utftext += String.fromCharCode(((c >> 6) & 63) | 128);
				utftext += String.fromCharCode((c & 63) | 128);
			}

		}
		return utftext;
	}

	// private method for UTF-8 decoding
	_utf8_decode = function (utftext) {
		var string = "";
		var i = 0;
		var c = c1 = c2 = 0;
		while (i < utftext.length) {
			c = utftext.charCodeAt(i);
			if (c < 128) {
				string += String.fromCharCode(c);
				i++;
			} else if ((c > 191) && (c < 224)) {
				c2 = utftext.charCodeAt(i + 1);
				string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
				i += 2;
			} else {
				c2 = utftext.charCodeAt(i + 1);
				c3 = utftext.charCodeAt(i + 2);
				string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
				i += 3;
			}
		}
		return string;
	}

}