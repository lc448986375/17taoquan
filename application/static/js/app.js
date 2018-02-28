var base_url = 'https://www.17taoquan.wang/';
var version = 'v1.0'; // 调用接口需要添加版本号，程序升级后可以兼容就版本
var app = angular.module('17taoquan', ['ionic']);

// 防止与flask模板标签{{}}冲突、把angular标签标识符改为{[]}
app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);


// 对$http.post 做处理，否则flask无法从form中获取参数
app.config(function($httpProvider){
    $httpProvider.defaults.transformRequest = function (obj) {
        var str = [];
        for (var p in obj) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        }
        return str.join("&");
    };
    $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';
});

// 本地数据存储
app.factory('locals', ['$window', function ($window) {
    return {
        set:function(key, value){
            $window.localStorage[key] = value; // 字符串存储
        },
        get:function(key, defaultValue){
            return $window.localStorage[key] || defaultValue;
        },
        setObject:function(key, value){
            $window.localStorage[key] = JSON.stringify(value); // 将对象以字符串保存
        },
        getObject:function(key, defaultValue){
            if($window.localStorage[key]){
                return JSON.parse($window.localStorage[key]); // 获取字符串并解析成对象
            }
            return defaultValue;
        }
    }
}]);

// 配置路由
app.config(function($stateProvider, $urlRouterProvider) {

    $stateProvider.state('tabs', {
        url: "/tab",
        abstract: true,
        templateUrl: "templates/tabs.html"
    }).state('tabs.home', {
        url: "/home",
        views: {
            'home-tab': {
                templateUrl: "templates/home.html",
                controller: 'HomeTabCtrl'
            }
        }
    }).state('details', {
        params:{'id':null},
        url: "/details",
        templateUrl: "templates/details.html",
        controller: 'DetailCtrl'
    }).state('tabs.search', {
        url: "/search",
        views: {
            'search-tab': {
                templateUrl: "templates/search.html",
                controller: 'SearchTabCtrl'
            }
        }
    }).state('tabs.navstack', {
        url: "/navstack",
        views: {
            'search-tab': {
                templateUrl: "templates/nav-stack.html"
            }
        }
    }).state('tabs.my', {
        url: "/my",
        cache:false, // 每次进入该页面时强制刷新。或者在使用 state.go时传入参数 state.go(url, {}, {reload:true})
        views: {
            'my-tab': {
                templateUrl: "templates/my.html",
                controller: 'MyTabCtrl'
            }
        }
    }).state('login', {
        url:"/login",
        cache:false,
        templateUrl: "templates/login.html",
        controller: 'LoginCtrl'
    }).state('regist', {
        url:"/regist",
        cache:false,
        templateUrl: "templates/regist.html",
        controller: 'RegistCtrl'
    }).state('orders', {
        url:"/orders",
        cache:false,
        templateUrl: "templates/orders.html",
        controller: 'OrdersCtrl'
    });

    $urlRouterProvider.otherwise("/tab/home");
});


// 首页控制器
app.controller('HomeTabCtrl', function($scope, $http, http_service) {
    
    
    $scope.super_fanli = [];
    $scope.hot_selled = [];
    $scope.super_coupon = [];

    loadData();

    // 加载数据
    function loadData(){
        $scope.load_finish = false;
        // 超级券
        var url = base_url + 'api/' + version + '/goods?order=couponed_desc&page=1&page_size=4';

        http_service.get(url, {}, {}, function(data){
            $scope.super_coupon = data['items'];
        });

        // 热销
        var url = base_url + 'api/' + version + '/goods?order=selled_desc&page=1&page_size=4';

        http_service.get(url, {}, {}, function(data){
            $scope.hot_selled = data['items'];
        });

    }

});

/**
 * 查询页面controller
 */
app.controller('SearchTabCtrl', function($scope, $ionicLoading, $http, locals, http_service) {
    
    $scope.list = [];
    $scope.cls = [];
    $scope.orders = [];
    $scope.url_args = {};

    $scope.page = 1;
    $scope.pages = 1;
    $scope.has_next = true;
    $scope.kwd = '';
    $scope.cate = '';
    $scope.order = '';
    $scope.load_finish = true;
    $scope.search_page_title = '搜索';

    // 加载数据
    loadData();
    loadGoodsClassData();
    loadGoodsOrderData();

    // 上拉加载数据
    $scope.loadMore = function(){
        if(!$scope.load_finish){
            return;
        }
        
        $scope.page += 1;
        loadData();
        $scope.$broadcast("scroll.infiniteScrollComplete");
    }

    // 查询
    $scope.search = function(kwd){
        
        
        $scope.kwd = kwd;
        $scope.cate = '';
        $scope.page = 1;
        $scope.order = '';
        loadData();
        
    }

    // 点击分类
    $scope.cls_click = function(code){
        if(String(code).length == 1){
            code = '0' + code;
        }
        
        $scope.cate = code;
        $scope.page = 1;
        $scope.order = '';
        loadData();
    }

    // 点击排序
    $scope.order_click = function(order){
        
        var next = 'asc';
        if($scope.order.indexOf('asc') > 0){
            next = 'desc';
        }else{
            next = 'asc';
        }
        var orderBy = order['order'] + '_' + next;
        $scope.page = 1;
        $scope.order = orderBy;
       
        loadData();
    }


    // 调用服务加载数据
    function loadData(){

        $scope.load_finish = false;
        var url = base_url + 'api/' + version + '/goods?f=search';
        url += '&page=' + $scope.page;
        url += '&kwd=' + $scope.kwd;
        url += '&cate=' + $scope.cate;
        url += '&order=' + $scope.order;

        http_service.get(url, {}, {}, function(data){
            if($scope.page == 1){
                $scope.list = [];   
            }
            
            $scope.list = $scope.list.concat(data['items']); // 产品列表

            $scope.pages = data['page'].pages;
            $scope.has_next = data['page'].has_next;

            setSearchPageTitle(); // 设置页面标题
            $scope.load_finish = true;
        }, function(response){
            $scope.load_finish = true;
        });

    }

    // 加载分类
    function loadGoodsClassData(){
        // 如果有不重复查询
        if($scope.cls.length != 0){
            return;
        }

        // 判断本地是否保存
        var cls = locals.getObject('GOODS_CLASS');
        if(cls){
            $scope.cls = cls;
            return;
        }

        // 从服务器查询
        var goodsclassurl = base_url + 'api/' + version + '/goodsclass';

        http_service.get(goodsclassurl, {}, {}, function(data){
            $scope.cls = data;
            data.unshift({'cls_code':'', 'cls_name':'全部', 'cls_order':0});
            locals.setObject('GOODS_CLASS', data);
        });
        
    }

    // 加载排序
    function loadGoodsOrderData(){
        // 如果有不重复查询
        if($scope.orders.length != 0){
            return;
        }

        // 判断本地是否保存
        var orders = locals.getObject('GOODS_ORDERS');
        if(orders){
            $scope.orders = orders;
            return;
        }

        // 从服务器查询
        var goodsorderurl = base_url + 'api/' + version + '/goodsorder';

        http_service.get(goodsorderurl, {}, {}, function(data){
            $scope.orders = data;
            locals.setObject('GOODS_ORDERS', data);
        }, function(response){

        });
        
    }

    // 设置标题
    function setSearchPageTitle(){
        var title = '搜索';
        if($scope.kwd.length > 0){
            title += '[' + $scope.kwd + ']';
        }
        $scope.search_page_title = title;
    }
});

/**
 * 明细页面controller
 */
app.controller('DetailCtrl', function($scope, $state, $stateParams, $ionicPopup, $ionicPopover, http_service, msg) {
    $scope.goods = {};
    $scope.link_goods = [];

    var id = $stateParams.id;
    if(id && id > 0){
        loadData(id);
    }

    // 显示明细页面后，触发改事件，保存上一页面name，返回时调用。
    $scope.$on("$stateChangeSuccess",  function(event, toState, toParams, fromState, fromParams) {
        
        $scope.previousState_name = fromState.name;
        $scope.previousState_params = fromParams;  
    });

    // 返回上一页面
    $scope.back = function(){
        $state.go($scope.previousState_name);
    }

    $scope.get_tkl = function(id){
        var url = base_url + 'api/' + version + '/taokouling/' + id;

        http_service.get(url, {}, {}, function(data){
            showTkl(data);
        });
       
    }

    function showTkl(tkl) {
        var confirmPopup = $ionicPopup.show({
            template: '<textarea style="height: 140px;" readonly="readonly">' + tkl + '</textarea>',
            title: '淘口令已生成',
            subTitle: '复制下面消息, 打开手机淘宝, 即可领券购买',
            scope: $scope,
            buttons: [
                { text: '关闭' }
            ]
        });

        confirmPopup.then(function(res) {
            if(res) {
                
            } else {
                
            }
        });
    }

    function loadData(id){
        var url = base_url + 'api/' + version + '/goods/' + id;

        http_service.get(url, {}, {}, function(data){
            $scope.goods = data;
            //$scope.link_goods = data['link_goods'];
            $scope.$broadcast("scroll.infiniteScrollComplete");
        });
        
    }

});

/**
 * 我的页面controller
 */
app.controller('MyTabCtrl', function($scope, $state, $http, $ionicLoading, msg, locals, http_service){
    $scope.user = {}; // 用户信息
    $scope.orders = {
        mall_orders_id : ''  // 关联订单
    };
    $scope.wallet = {};


    // 校验是否登陆
    var token = locals.get('TOKEN', null);
    if(!token){
        // 弹出登录
        $state.go("login");
    }

    // 获取用户信息
    var base = new Base64();
    var encodeStr = base.encode(token + ':' + '');
    
    var url = base_url + 'api/' + version + '/user';

    // 通过token获取用户信息
    http_service.get(url, {}, {'Authorization' : 'Basic ' + encodeStr}, function(data){
        $scope.user = data;
    });

    // 获取钱包信息
    var wallet_url = base_url + 'api/' + version + '/wallet';
    http_service.get(wallet_url, {}, {'Authorization' : 'Basic ' + encodeStr}, function(data){
        $scope.wallet = data;
    });

    $scope.logout = function(){
        locals.set('TOKEN', null);
        $state.go("login");
    }

    // 关联订单
    $scope.addOrders = function(){
        if($scope.orders.mall_orders_id.length == 0){
            return;
        }
        var url = base_url + 'api/' + version + '/userorders/' + $scope.orders.mall_orders_id;
        http_service.post(url, {}, {'Authorization' : 'Basic ' + encodeStr}, function(data){
            $scope.orders.mall_orders_id = '';
            msg.success('关联成功');
        });
       
    }
});

/**
 * 订单列表
 */
app.controller('OrdersCtrl', function($scope, $state, $rootScope, $http, $ionicLoading, locals, http_service){
    $scope.orders = [];

    // 校验是否登陆
    var token = locals.get('TOKEN', null);
    if(!token){
        // 弹出登录
        $state.go("login");
    }

    // 获取用户信息
    var base = new Base64();
    var encodeStr = base.encode(token + ':' + '');

    // 订单列表，触发改事件，保存上一页面name，返回时调用。
    $scope.$on("$stateChangeSuccess",  function(event, toState, toParams, fromState, fromParams) {
        
        $scope.previousState_name = fromState.name;
        $scope.previousState_params = fromParams;
    });

    // 返回上一页面
    $scope.back = function(){
        $state.go($scope.previousState_name);
    }


    // 获取订单列表
    var url = base_url + 'api/' + version + '/userorders';
    http_service.get(url, {}, {'Authorization' : 'Basic ' + encodeStr}, function(data){
        $scope.orders = data;
    });
});


/**
 * 登陆页面
 */
app.controller('LoginCtrl', function($scope, $state, $http, locals, http_service, msg){
    $scope.login = function(username, password){
        var url = base_url + 'api/' + version + '/token';
        var base = new Base64();
        var encodeStr = base.encode(username + ':' + password);

        http_service.get(url, {}, {'Authorization' : 'Basic ' + encodeStr}, function(data){
            console.log(data);
            // 登陆成功，保存token，并跳转到我的页面
            locals.set('TOKEN', data);
            $state.go("tabs.my");
        }, function(data){
            // 登陆失败
            console.log(data);
            msg.fail(data.error);
        });
    }

});

/**
 * 注册页面controller
 */
app.controller('RegistCtrl', function($scope, $state, $http, $ionicPopup, http_service, msg){
    $scope.user = {}

    // 注册
    $scope.regist = function(isValid){
        if(!isValid){
            msg.fail('请检查输入');
        }

        var url = base_url + 'api/' + version + '/user/regist';

        http_service.post(url, $scope.user, {}, function(data){
            msg.success('注册成功, 立即登陆', function(res){
                $state.go('login');
            });
        }, function(data){
           msg.fail('注册失败:' + data.error);
        });
       
    }
});


// android需要单独设置该属性，否则ion-nav-bar会在顶部
app.config(["$ionicConfigProvider", function($ionicConfigProvider) {
    $ionicConfigProvider.tabs.position('bottom');
}]);

// 自定义指令。产品列表模板
app.directive('goodsListItem', function(){
    return{
        scope:{
            items:'='
        },
        templateUrl:'templates/goods_list_item.html'
    }
});

// http访问服务。
app.service('http_service', function($http, $ionicLoading, $state, msg){
    
    this.get = function(url, data, headers, success, fail){
        this.http(
            {
                method:'GET',
                url:url,
                data:data,
                headers : headers
            },
            success,
            fail
        );
    }

    this.post = function(url, data, headers, success, fail){
        this.http(
            {
                method:'POST',
                url:url,
                data:data,
                headers : headers
            },
            success,
            fail
        );
    }

    this.http = function(config, success, fail){
        $ionicLoading.show({
            template: '加载中...'
        });

        
        $http(config).then(function(response) {
            
            if(success){
                success(response.data);
            }

            $ionicLoading.hide();
        }, function(response) {
            
            if(fail){
                fail(response.data);
            }else{
                if(response.status == 403){
                    $state.go("login");
                }else if(response.status == 500){
                    msg.fail(response.data.error);
                }
            }

            $ionicLoading.hide();
        });
        
    }
});

// 弹出提醒服务
app.service('msg', function($ionicPopup){
    this.success = function(msg, ok_func){
        $ionicPopup.alert({
            title: '成功',
            template: msg
        }).then(function(res){
            if(ok_func){
                ok_func();
            }
        });
    }

    this.fail = function(msg, ok_func){
        $ionicPopup.alert({
            title: '错误',
            template: msg
        }).then(function(res){
            if(ok_func){
                ok_func();
            }
        });
    }
});

// 自定义指令。用户名输入限制
app.directive('checkUsername', function(){
    return{
        require: 'ngModel',
        link: function(scope, ele, attrs, c){
            scope.$watch(attrs.ngModel, function(n){
                if(!n || n == '') return;
                c.$setValidity('checkUsername', /^[0-9a-zA-Z]+$/.test(n));
            });
        }
    }
});