;(function ($, window, document, undefined) {  //避免全局依赖,避免第三方破坏

  /*opt 配置参数可以使用第三方的API，因为是继承第三方的插件，还是自定义配置参数*/
  /*默认配置参数*/
  $.BDGrid = function (opt) {
    var me = this;
    var title = '';// top.tabs && top.tabs.getCurrentTab().label;
    opt = $.extend({}, {
      alternatingRow: true, //奇偶行效果
      rownumbers: false, //是否显示行序号
      allowHideColumn: false, //是否显示'切换列层'按钮
      pageParmName: 'start', //页索引参数名，(提交给服务器)
      pagesizeParmName: 'length', //页记录数参数名，(提交给服务器)
      root: 'data', //数据源字段名
      record: 'recordsTotal', //数据源记录数字段名
      pageSize: 20, //每页默认的结果数
      pageSizeOptions: [5, 10, 20, 30, 40, 50],  //可选择设定的每页结果数
      heightDiff: -5, //高度补差,当设置height:100%时，可能会有高度的误差，可以通过这个属性调整
      width: '99.8%', height: '99%',
      frozenCheckbox: false, //复选框按钮是否在固定列中
      columnDefs: [],
      title: title,
      checkbox: true,
      showSitting: true,//是否需要操作列
      showEdit: true,
      showView: true,
      showDel: true,
      showShare: false, //是否显示分享按钮
      showCopy: false, //是否显示复制按钮
      showDownload: false, //是否显示复制按钮
      isSelectR: true,//复选按钮是否选中
      TableISelect: false
    }, opt);

    //console.log(me.prototype);

    var parentEl = opt.el || 'body', sHtml = '', title = opt.title || '';
    sHtml = '<div class=\"seaBox\"><h1 class="title">' + title + '</h1><div class=\"other\"></div><div class=\"listBtn btn_box\"><div class="btn_list"></div></div></div>'

    $(parentEl).append('<div class="g_div_table" position="center">' + sHtml + '<div class="ligerGrid list"></div></div>');
    var el = $('.ligerGrid');
    me.el = el;
    if (opt.ajax) {
      opt.url = opt.ajax.url;
      opt.parms = opt.ajax.parms;
    }

    if (!opt.url && !opt.sColumnsUrl) {
      alert("请配置表格信息请求地址");
      return false;
    }
    var getData = function (data) {

    };
    //是否显示增、删、改按钮
    if (!opt.showSitting) {
      $(".listBtn").hide();
    }
    //修改IndexListData.json文件的TableISelect值，实现翻页选中
    if (opt.checkbox) {
      $(parentEl).on('click', 'tr.l-grid-row', function () {
        var row = $(this);
        var uncheck = row.hasClass("l-selected");
        var n = row.find("a.hideId").attr("rowid");
        $.ajaxSettings.async = false;
        $.getJSON(opt.url, function (data) {

          $.each(data.data, function (i, item) {
            if (!uncheck) {
              data.data[n].TableISelect = true;
            } else {
              data.data[n].TableISelect = false;
            }
          });
          isSelectR = data.data[n].TableISelect;
        });
        $.post(opt.url, function (data) {
          data.data[n].TableISelect = isSelectR;
        }, 'json');
      });
    }
    //解锁与锁定的切换
    /*el.on('click', 'input.qt',function(event){
     event.stopPropagation();
     var yes = $(this).hasClass("bt_qyan");
     var n = $(this).parent().parent().siblings("td.l-grid-row-cell-last").find("a.list-btn").attr("rowid");
     var t=0;
     if(yes){
     $(this).removeClass("bt_qyan").addClass("bt_tyan");
     t=2;
     }else{
     $(this).removeClass("bt_tyan").addClass("bt_qyan");
     t=1;
     }
     $.post(opt.url,function(data) {
     data.data[n].serverSelect = t;//给JSON参数赋值 1为启用或解锁，2为停用或锁定
     },'json');
     });*/
    //增删改A标签
    $(parentEl).on('click', 'a', function () {
      var aClass = $(this);
      var data = me.grid.getRow($(this).attr('rowid'));
      if (aClass.hasClass("bt_edit")) {
        el.trigger('edit', [me, me.grid, [data]]);
      }
      ;
      if (aClass.hasClass("bt_view")) {
        el.trigger('view', [me, me.grid, [data]]);
      }
      ;
      if (aClass.hasClass("bt_share")) {
        el.trigger('share', [me, me.grid, [data]]);
      }
      ;
      if (aClass.hasClass("bt_copy")) {
        el.trigger('copy', [me, me.grid, [data]]);
      }
      ;
      if (aClass.hasClass("bt_download")) {
        el.trigger('download', [me, me.grid, [data]]);
      }
      ;
      if (aClass.hasClass("bt_del")) {
        el.trigger('del', [me, me.grid, [data]]);
      }

    });
    //增删改INPUT按钮
    $(parentEl).on('click', 'input', function () {
      var eClass = $(this);
      if (eClass.hasClass("btnAdd")) {
        el.trigger('add', [me, me.grid]);
      }
      ;
      if (eClass.hasClass("btnEdit")) {
        el.trigger('edit', [me, me.grid, me.grid.getSelectedRows()]);
      }
      ;
      if (eClass.hasClass("btnView")) {
        el.trigger('view', [me, me.grid, me.grid.getSelectedRows()]);
      }
      ;
      if (eClass.hasClass("btnDel")) {
        el.trigger('del', [me, me.grid, me.grid.getSelectedRows()]);
      }
      ;
      if (eClass.hasClass("accurate_search")) {
        el.trigger('accurate_search', [me, me.grid]);
      }
      ;
    });

    if (opt.sColumnsUrl) {
      $.ajax({
        url: opt.sColumnsUrl,
        type: 'POST',
        dataType: 'json',
        data: {_dc: new Date()}
      }).done(function (data) {
        if (opt.columnDefs) {
          $.each(opt.columnDefs, function (key, item) {
            $.each(data,
              function (i, v) {
                if (typeof item != "undefined" && v.sClass == item.targets) {
                  data[i].render = item.render;
                }
              }
            )

          });

        }
        ;
        //是否增加锁定操作
        if (opt.showLock) {
          data.push({
            display: '状态', name: 'lock', minWidth: 100, type: 'int',
            render: function (item) {
              if (parseInt(item.serverSelect) == 1) return "<input type='button' class='qt bt_qyan' title='解锁'/>";
              if (parseInt(item.serverSelect) == 2) return "<input type='button' class='qt bt_tyan' title='锁定'/>";
              if (parseInt(item.serverSelect) == 3) return "&nbsp;";
            }
          });
        }

        //是否启用
        if (opt.showUseed) {
          data.push({
            display: '状态', name: 'useing', minWidth: 100, type: 'int',
            render: function (item) {
              if (parseInt(item.serverSelect) == 1) return "<font class='green'>启用</font>";
              if (parseInt(item.serverSelect) == 2) return "<font class='gray'>停用</font>";
              if (parseInt(item.serverSelect) == 3) return "<font class='red'>未启用</font>";
            }
          });
        }

        //是否增加服务器状态
        if (opt.showComputer) {
          data.push({
            display: '内存利用率(%)', name: 'sFrameCP', minWidth: 50,
            render: function (item) {
              if (parseInt(item.sFrameCP) <= 40) return "<font class='green'>" + item.sFrameCP + "</font>";
              if (parseInt(item.sFrameCP) > 40 && parseInt(item.sFrameCP) < 80) return "<font class='yellow'>" + item.sFrameCP + "</font>";
              if (parseInt(item.sFrameCP) >= 80) return "<font class='red'>" + item.sFrameCP + "</font>";

            }
          });
          data.push({
            display: 'CPU利用率(%)', name: 'sFrameJx', minWidth: 50,
            render: function (item) {
              if (parseInt(item.sFrameJx) <= 40) return "<font class='green'>" + item.sFrameJx + "</font>";
              if (parseInt(item.sFrameJx) > 40 && parseInt(item.sFrameJx) < 80) return "<font class='yellow'>" + item.sFrameJx + "</font>";
              if (parseInt(item.sFrameJx) >= 80) return "<font class='red'>" + item.sFrameJx + "</font>";

            }
          });
          data.push({
            display: '磁盘状态', name: 'sFrameLl', minWidth: 50,
            render: function (item) {
              if (parseInt(item.sFrameLl) <= 40) return "<font class='green'>" + item.sFrameLl + "</font>";
              if (parseInt(item.sFrameLl) > 40 && parseInt(item.sFrameLl) < 80) return "<font class='yellow'>" + item.sFrameLl + "</font>";
              if (parseInt(item.sFrameLl) >= 80) return "<font class='red'>" + item.sFrameLl + "</font>";

            }
          });
          data.push({
            display: '通信口状态', name: 'sFrameZj', minWidth: 50,
            render: function (item) {
              if (parseInt(item.sFrameZj) == 1) return "<font class='green'>正常</font>";
              if (parseInt(item.sFrameZj) == 2) return "<font class='gray'>离线</font>";
              if (parseInt(item.sFrameZj) == 3) return "<font class='red'>异常</font>";

            }
          });
        }
        ;
        //是否增加状态
        if (opt.showRuning) {
          data.push({
            display: '状态', name: 'sFrameRun', minWidth: 50,
            render: function (item) {
              if (parseInt(item.sFrameRun) == 1) return "<font class='green'>正常</font>";
              if (parseInt(item.sFrameRun) == 2) return "<font class='gray'>离线</font>";

            }
          });
        }
        ;

        //是否增加进度条
        if (opt.showProgress) {
          data.push({
            display: '进度', name: 'sFrameProgress',
            render: function (item) {
              return "<div class='cbar' title='" + item.sFrameProgress + "'><div class='cbarnum' style='width: " + item.sFrameProgress + "'></div><div class='cbartext'>" + item.sFrameProgress + "</div></div>";
            }
          });
        }
        ;
        //是否增加进度条
        if (opt.showProgress01) {
          for(var ioo = 0; ioo<data.length; ioo++){
            if(data[ioo].columns){
              for(var ipp = 0; ipp<data[ioo].columns.length; ipp++){
                if(data[ioo].columns[ipp].name == 'sFrameProgress01'){
                  data[ioo].columns[ipp].render = function (item) {
                    return "<div class='cbar' title='" + item.sFrameProgress01 + "'><div class='cbarnum' style='width: " + item.sFrameProgress01 + "'></div><div class='cbartext'>" + item.sFrameProgress01 + "</div></div>";
                  }
                }
              }
            }
          }
        }
        ;//是否增加进度条
        if (opt.showProgress02) {
          for(var ioo = 0; ioo<data.length; ioo++){
            if(data[ioo].columns){
              for(var ipp = 0; ipp<data[ioo].columns.length; ipp++){
                if(data[ioo].columns[ipp].name == 'sFrameProgress02'){
                  data[ioo].columns[ipp].render = function (item) {
                    return "<div class='cbar' title='" + item.sFrameProgress02 + "'><div class='cbarnum' style='width: " + item.sFrameProgress02 + "'></div><div class='cbartext'>" + item.sFrameProgress02 + "</div></div>";
                  }
                }
              }
            }
          }
        }
        ;//是否增加进度条
        if (opt.showProgress03) {
          for(var ioo = 0; ioo<data.length; ioo++){
            if(data[ioo].columns){
              for(var ipp = 0; ipp<data[ioo].columns.length; ipp++){
                if(data[ioo].columns[ipp].name == 'sFrameProgress03'){
                  data[ioo].columns[ipp].render = function (item) {
                    return "<div class='cbar' title='" + item.sFrameProgress03 + "'><div class='cbarnum' style='width: " + item.sFrameProgress03 + "'></div><div class='cbartext'>" + item.sFrameProgress03 + "</div></div>";
                  }
                }
              }
            }
          }
        }
        ;
        //是否增加状态（图标）
        if (opt.showState) {
          data.push({
            display: '状态', name: 'sFrameState', minWidth: 50,
            render: function (item) {
              if (parseInt(item.sFrameState) == 1) return "<input class='list-btn bt_qy' title='完成'/>";
              if (parseInt(item.sFrameState) == 0) return "<input class='list-btn bt_ty' title='未完成'/>";
              if (parseInt(item.sFrameState) == 2) return "<input class='list-btn bt_py' title='进行中'/>";
            }
          });
        }
        ;
        //是否增加处理结果（按钮）
        if (opt.showResult) {
          data.push({
            display: '处理结果', name: 'sFrameResult', minWidth: 50,
            render: function (item) {
              if (parseInt(item.sFrameResult) == 1) return "<font class='green'>已解除</font>";
              if (parseInt(item.sFrameResult) == 0) return "<input type='button' class='btn btn_result' value='未解除'>";

            }
          });
        }
        ;
        //是否增加当前流量
        if (opt.showNumb) {
          data.push({
            display: '当前流量(MB)', name: 'sFrameliu', minWidth: 150,
            render: function (item) {
              var h = [];
              if (parseInt(item.sFrameZj) < 1000) {
                h.push("<font class='green'>上行:" + item.sFrameZj + "</font>");
              } else {
                h.push("<font class='red'>上行:" + item.sFrameZj + "</font>");
              }

              if (parseInt(item.sFrameZx) < 1000) {
                h.push(" <font class='green'>下行:" + item.sFrameZx + "</font>");

              } else {
                h.push(" <font class='red'>下行:" + item.sFrameZx + "</font>");
              }
              return h;
            }
          });
        }
        ;
        if (opt.checkbox) {
          data.push({
            name: 'hideId', display: '', width: 1, isAllowHide: false,
            render: function (record, rowindex, value, column) {
              var html = [];
              html.push("<a href='javascript:;' class='hideId' style='display:none' rowid='" + rowindex + "'></a>");
              return html;
            }
          });
        }
        $.each(data, function (i, v) {
            switch (v.sClass) {
              case 'btn_del':
                $('<input type=\"button\" class=\"btn btnDel c_o btn_del\" value="删除">').appendTo('.g_div_table div.btn_list');
                //opt.checkbox = true;
                opt.del = opt.showDel;

                break;
              case 'btn_view':
                $('<input type=\"button\" class=\"btn btnView c_o btn_view\" value="查看">').appendTo('.g_div_table div.btn_list');
                //opt.checkbox = true;
                opt.view = opt.showView;
                break;
              case 'btn_edit':
                if (v.sType == 1) {
                  $('<input type=\"button\" class=\"btn btnAdd c_g btn_add\" value="新增">').appendTo('.g_div_table div.btn_list');
                } else if (v.sType == 2) {
                  $('<input type=\"button\" class=\"btn btnEdit c_b btn_edit\" value="编辑">').appendTo('.g_div_table div.btn_list');
                  opt.edit = opt.showEdit;
                } else {
                  $('<input type=\"button\" class=\"btn btnAdd c_g btn_add\" value="新增">').appendTo('.g_div_table div.btn_list');
                  $('<input type=\"button\" class=\"btn btnEdit c_b btn_edit\" value="编辑">').appendTo('.g_div_table div.btn_list');
                  opt.edit = opt.showEdit;
                }
                //opt.checkbox = false;
                break;
              case 'btn_share':
                $('<input type=\"button\" class=\"btn btnShare c_o btn_view\" value="分享">').appendTo('.g_div_table div.btn_list');
                //opt.checkbox = true;
                opt.share = opt.showShare;
                break;
              case 'btn_copy':
                $('<input type=\"button\" class=\"btn btnCopy c_o btn_view\" value="复制">').appendTo('.g_div_table div.btn_list');
                //opt.checkbox = true;
                opt.copy = opt.showCopy;
                break;
              case 'btn_download':
                $('<input type=\"button\" class=\"btn btnDownload c_o btn_view\" value="下载">').appendTo('.g_div_table div.btn_list');
                //opt.checkbox = true;
                opt.download = opt.showDownload;
                break;
            }

            if (data[i].bVisible != false) {
            } else {
              data[i].hide = true;
              data[i].width = -1;
            }
            if (data[i].data) {
              data[i].name = data[i].data;
            }
            if (data[i].sTitle) {
              data[i].display = data[i].sTitle;
            }
          }
        );
        if (opt.del == true || opt.view == true || opt.edit == true || opt.showhf == true || opt.share == true || opt.copy == true || opt.download == true) {
          data.push({
            name: 'id', display: '操作', width: 125, isAllowHide: false,
            render: function (record, rowindex, value, column) {
              var html = [];
              if (opt.edit == true) {
                html.push("<a href='javascript:;' title='编辑' class='bt_edit bt_bj list-btn' rowid='" + rowindex + "'></a>");
              }
              if (opt.view == true) {
                html.push("<a href='javascript:;' title='查看' class='bt_view bt_ck list-btn' rowid='" + rowindex + "'></a>");
              }
              if (opt.share == true) {
                html.push("<a  href='javascript:;' title='分享' class='bt_share bt_sc list-btn' rowid='" + rowindex + "'></a>");
              }
              if (opt.copy == true) {
                html.push("<a  href='javascript:;' title='复制' class='bt_copy bt_sc list-btn' rowid='" + rowindex + "'></a>");
              }
              if (opt.download == true) {
                html.push("<a  href='javascript:;' title='下载' class='bt_download bt_sc list-btn' rowid='" + rowindex + "'></a>");
              }
              if (opt.showhf == true) {
                html.push("<a  href='javascript:;' title='恢复' class='bt_hf bt_sc list-btn' rowid='" + rowindex + "'></a>");
              }
              if (opt.del == true) {
                html.push("<a  href='javascript:;' title='删除' class='bt_del bt_sc list-btn' rowid='" + rowindex + "'></a>");
              }
              return html.join('&nbsp;');
            }
          });

        }
        ;
        opt.columns = data;

        var d = $(parentEl + ' .ligerGrid').ligerGrid(opt);
        me.grid = d;
        //console.log(d);
        me.el.trigger('beforerender', [d]);

        var fit = opt.fit || true;
        if (fit) {
          $('.ligerGrid .l-grid-body').css('overflow-x', 'hidden');
        }
      }).fail(function () {
      });
    } else {
      var d = $(parentEl + ' .ligerGrid').ligerGrid(opt);
      me.grid = d;
      me.el.trigger('beforerender', [d]);
    }
    return me.el;


    /*function __init__(data){
     return me.each(function() {//因为对象化可能有0个以上的实例
     $this = $(this); //转化为jQuery对象
     var grid = $this.ligerGrid($.extend({}, {
     columns:data, pageSize: 10,
     width: '100%', height: '100%'
     },opt
     ));
     $.extend(grid,{
     getData : getData
     });

     $this.trigger('afterrender',[grid,$this]);
     });
     }
     if(opt.columns){
     __init__({});
     }else{
     $.getJSON(opt.url,opt.sColumnsUrl||{},function(data){
     return __init__(data);
     },"json");
     }*/


  };

  $(function () {
    $(".l-grid-row:odd").css("background-color", "#f9f9f9");//列表间隔行

    $(".btn_sea,.keyword_box .close").click(function () {//解决点击精确查询导致列表分页看不到的问题，刷新列表

      var traget = document.getElementById('keyword_box');

      $.grid.reload()

      if (traget.style.display == "none") {

        traget.style.display = "";
      } else {
        traget.style.display = "none";
      }
    })

  })


})(jQuery, window, document)


