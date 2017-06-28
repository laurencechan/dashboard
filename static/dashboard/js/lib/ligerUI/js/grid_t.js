;(function($){  //避免全局依赖,避免第三方破坏
    /*采用对象化进行封接*/
    $.fn.BDGrid = function(opt){
        var option = $.extend({}, $.fn.BDGrid.defaults,opt),me=this;
        if(!option.sHeaderUrl && !option.columns){
            alert("请配置表格头部信息请求地址");
            return false;
        }
       var getData  = function(data,hParams){
		  // var grid = this;
        };
		if(option.showLock){
			opt.columns.push({
				 display: '状态', name: 'lock',minWidth: 100, type:'int',
				  render: function (record, rowindex, value, column)
					{
						if (parseInt(record.lock) == 1) return "<input type='button' class='qt bt_qyan' title='解锁'/>";
						if (parseInt(record.lock) == 0) return "<input type='button' class='qt bt_tyan' title='锁定'/>";
						
					}
			});
		}
		if(option.showSitting){
			opt.columns.push({
				name: 'id', display: '操作',minWidth:150,  isAllowHide: false,
				render: function (record, rowindex, value, column) {
					var h = "";
					if (!record._editing)
					{
						h += "<input type='button' class='list-btn bt_bj'/>";
						h += "<input type='button' class='list-btn bt_ck'/>"; 
						h += "<input type='button' class='list-btn bt_sc'/>"; 
					}
					return h;
				}
			});
		}
        function __init__(data){
            return me.each(function() {//因为对象化可能有0个以上的实例
                $this = $(this); //转化为jQuery对象
                var grid = $this.ligerGrid($.extend({}, {
                        columns:data, pageSize: 10,
                        width: '100%', height: '100%'
                    },option
                ));
				//alert(option.width);
                /*扩展方法*/
                $.extend(grid,{
                    getData : getData
                });
                /*注册事件*/
                $this.trigger('afterrender',[grid,$this]);
            });
        }
        if(opt.columns){
            __init__({});
        }else{
            $.getJSON(option.sHeaderUrl,option.hHeaderParams||{},function(data){
                return __init__(data);
            },"json");
        }
    };
    /*opt 配置参数可以使用第三方的API，因为是继承第三方的插件，还是自定义配置参数*/
    /*默认配置参数*/
    $.fn.BDGrid.defaults = {
        /*对组件统一配置*/
		pageSize:5,
		pageSizeOptions: [5, 10, 20, 30, 40, 50, 100],
		columns: [],
		loading:true
    };

})(jQuery);

