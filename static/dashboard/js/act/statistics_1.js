
;(function($){  //避免全局依赖,避免第三方破坏
	
    $(document).ready(function () {
        /*调用*/
		var GridTable = $.BDGrid({
            sColumnsUrl: '../js/act/data/GetHeaderTitle_AnomalyHost.json',
            ajax: {
                url: '../js/act/data/IndexListData_AnomalyHost.json',
                type: 'POST'
            },
			el:'#maingrid',
			dataAction:'local',
			showSitting:false,//是否需要操作列
			showEdit:false,
			showView:false,
			showDel:false,
			showLock:false,//是否需要解锁和锁定状态栏
			isSelectR:false,//复选按钮是否选中
  		showProgress01:true,
  		showProgress02:true,
  		showProgress03:true,
			width: '99.8%',
			height:'99%',
			pageSize: 20, 
			pageSizeOptions: [10, 20, 30, 40, 50, 100],
			checkbox: false,
			columnDefs: [
			  {
			    targets: 'sFrameProgress',
          		data: 'sFrameProgress',
          		render: function(row, bVisible, value) {
	             console.log(value);
	          }
			  }
			]
      });
        
    });
})(jQuery);