var xjglChart = echarts.init(document.getElementById('虚机管理'));
var VCPUChart = echarts.init(document.getElementById('VCPUChart'));
var cpuChart = echarts.init(document.getElementById('cpuChart'));
var ipChart = echarts.init(document.getElementById('ipChart'));
var aqzChart = echarts.init(document.getElementById('aqzChart'));
var juanChart = echarts.init(document.getElementById('juanChart'));
var yypccChart = echarts.init(document.getElementById('yypccChart'));

//虚机管理			
option_xjgl = {
    tooltip : {
        formatter: "{a} <br/>{b} : {c}%"
    },
    
    series : [
        {
            name:'虚机管理',
            type:'gauge',
			radius :[0,'100%'],
            detail : {formatter:'{value}%'},
            data:[{value: 10.0, name: '222'}],
			axisLine:{show: true,
   				 lineStyle: {
       				 color: [
							[0.2, '#228b22'],
							[0.8, '#48b'],
							[1, '#ff4500']
        				], 
       				 width: 13
   				 }
			},
			axisTick :{
				show: true, 
				splitNumber: 5, 
				length :3, 
				lineStyle: {
					color: '#ececec',
					width: 1,
					type: 'solid'
				}
			} ,
			axisLabel :{
				show: true,
				formatter: null,
				textStyle: {
					color: 'auto',
					fontFamily:'Arial'
							
					}				
			},
			splitLine:{
				show: true,
				length :7, 
				lineStyle: { 
					color: '#ececec',
					width: 1,
					type: 'solid'
				}

			},
			pointer :{
				length : '75%',
				width : 4,
				color : 'auto'

			
			},
			title :{
				show : true,
				offsetCenter: [0, '-30%'],
				textStyle: {
				color: '#999'
				}
			},		
				detail : {
                formatter:'{value}%',
                textStyle: {       
                    color: 'auto',
					fontSize:16
                }
            }			     
        }
    ]
  };

//VCPU数量			
option_VCPU = {
    tooltip : {
        formatter: "{a} <br/>{b} : {c}%"
    },    
    series : [
        {
            name:'VCPU数量',
            type:'gauge',
			radius :[0,'100%'],
            detail : {formatter:'{value}%'},
            data:[{value: 50, name: 'VCPU数量'}],
			axisLine:{show: true,
   				 lineStyle: {
       				 color: [
							[0.2, '#228b22'],
							[0.8, '#48b'],
							[1, '#ff4500']
        				], 
       				 width: 13
   				 }
			},
			axisTick :{
				show: true, 
				splitNumber: 5, 
				length :3, 
				lineStyle: {
					color: '#ececec',
					width: 1,
					type: 'solid'
				}
			} ,
			axisLabel :{
				show: true,
				formatter: null,
				textStyle: {
					color: 'auto',
					fontFamily:'Arial'	
							
					}				
			},
			splitLine:{
				show: true,
				length :7, 
				lineStyle: { 
					color: '#ececec',
					width: 1,
					type: 'solid'
				}

			},
			pointer :{
				length : '75%',
				width : 4,
				color : 'auto'

			
			},
			title :{
				 show : true,
				offsetCenter: [0, '-30%'],
				textStyle: {
					color: '#999'
				}
		   },
			detail : {
                formatter:'{value}%',
                textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                    color: 'auto',
					fontSize:16
                }
            }			     
        }
    ]
};

//内存                
option_cpu = {
    tooltip : {
        formatter: "{a} <br/>{b} : {c}%"
    },    
    series : [
        {
            name:'内存',
            type:'gauge',
            radius :[0,'100%'],
            detail : {formatter:'{value}%'},
            data:[{value: 50, name: '内存'}],
            axisLine:{show: true,
                 lineStyle: {
                     color: [
                            [0.2, 'rgb(131,175,155)'],
                            [0.8, 'rgb(135,206,250)'],
                            [1, 'rgb(252,157,154)']
                        ], 
                     width: 13
                 }
            },
            axisTick :{
                show: true, 
                splitNumber: 5, 
                length :3, 
                lineStyle: {
                    color: '#ececec',
                    width: 1,
                    type: 'solid'
                }
            } ,
            axisLabel :{
                show: true,
                formatter: null,
                textStyle: {
                    color: 'auto',
                    fontFamily:'Arial'  
                            
                    }               
            },
            splitLine:{
                show: true,
                length :7, 
                lineStyle: { 
                    color: '#ececec',
                    width: 1,
                    type: 'solid'
                }

            },
            pointer :{
                length : '75%',
                width : 4,
                color : 'auto'

            
            },
            title :{
                 show : true,
                offsetCenter: [0, '-30%'],
                textStyle: {
                    color: '#999'
                }
           },
            detail : {
                formatter:'{value}%',
                textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                    color: 'auto',
                    fontSize:16
                }
            }
        }
    ]
};

//浮动IP
var labelTop = {
    normal : {
        label : {
            show : true,
            position : 'center',
            formatter : '{b}',
            //rotate:'90',
            textStyle: {
                baseline : 'bottom'
            }
        },
        labelLine : {
            show : false
        }
    }
};
var labelFromatter = {
    normal : {
        label : {
            //formatter : function (a,b,c){return  100-c + '%'},
            formatter : function (params){
                return 100 - params.value + '%'
            },            
            textStyle: {
                baseline : 'top',
                fontSize:14
            }
        }
    }
}
var labelBottom = {
    normal : {
        color: '#ccc',
        label : {
            show : true,
            position : 'center'
        },
        labelLine : {
            show : false
        }
    },
    emphasis: {
        color: 'rgba(0,0,0,0)'
    }
};
var radius = [45, 65];//半径，默认为MIN(width,height)/2-50,传数组实现环形图，[内半径，外半径]                
option_ip = {
    series : [
        {
            type : 'pie',
            center : ['50%', '50%'],
            radius :  [45, 65],
            itemStyle : labelFromatter ,
            textStyle: {
                baseline : 'middle'
            },
            data : [
                {value:63, name: '',itemStyle : labelBottom},
                {value: 37, name: '浮动IP', itemStyle : labelTop}
            ]
        }
    ], 
    color: ['rgb(131,175,155)']
};

//安全组         
option_aqz = {
    series : [
        {
            type : 'pie',
            center : ['50%', '50%'],
            radius :  [45, 65],
            itemStyle : labelFromatter ,
            textStyle: {
                baseline : 'middle'
            },
            data : [
                {value:63, name: '',itemStyle : labelBottom},
                {value: 37, name: '安全组', itemStyle : labelTop}
            ]
        }
    ]
};

//卷                
option_juan = {
    series : [
        {
            type : 'pie',
            center : ['50%', '50%'],
            radius :  [45, 65],
            itemStyle : labelFromatter ,
            textStyle: {
                baseline : 'middle'
            },
            data : [
                {value:63, name: '',itemStyle : labelBottom},
                {value: 37, name: '卷', itemStyle : labelTop}
            ]
        }
    ],
    color: ['rgb(252,157,154)']
};

//云硬盘存储            
option_yypcc = {
    tooltip : {
        formatter: "{a} <br/>{b} : {c}%"
    },    
    series : [
        {
            name:'云硬盘存储',
            type:'gauge',
            radius :[0,'100%'],
            detail : {formatter:'{value}%'},
            data:[{value: 50, name: '云硬盘存储'}],
            axisLine:{show: true,
                 lineStyle: {
                     color: [
                            [0.2, '#228b22'],
                            [0.8, '#48b'],
                            [1, '#ff4500']
                        ], 
                     width: 13
                 }
            },
            axisTick :{
                show: true, 
                splitNumber: 5, 
                length :3, 
                lineStyle: {
                    color: '#ececec',
                    width: 1,
                    type: 'solid'
                }
            } ,
            axisLabel :{
                show: true,
                formatter: null,
                textStyle: {
                    color: 'auto',
                    fontFamily:'Arial'  
                            
                    }               
            },
            splitLine:{
                show: true,
                length :7, 
                lineStyle: { 
                    color: '#ececec',
                    width: 1,
                    type: 'solid'
                }

            },
            pointer :{
                length : '75%',
                width : 4,
                color : 'auto'

            
            },
            title :{
                 show : true,
                offsetCenter: [0, '-30%'],
                textStyle: {
                    color: '#999'
                }
           },
            detail : {
                formatter:'{value}%',
                textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                    color: 'auto',
                    fontSize:16
                }
            }                
        }
    ]
};

clearInterval(timeTicket);
var timeTicket = setInterval(function (){
    option_xjgl.series[0].data[0].value = (Math.random()*100).toFixed(2) - 0;
    xjglChart.setOption(option_xjgl, true);

    option_VCPU.series[0].data[0].value = (Math.random()*100).toFixed(2) - 0;
    VCPUChart.setOption(option_VCPU, true);	
},2000);

																													
xjglChart.setOption(option_xjgl);
VCPUChart.setOption(option_VCPU);
cpuChart.setOption(option_cpu);
ipChart.setOption(option_ip);
aqzChart.setOption(option_aqz);
juanChart.setOption(option_juan);
yypccChart.setOption(option_yypcc);

window.addEventListener("resize", function () {
    xjglChart.resize();
    VCPUChart.resize();
    cpuChart.resize();
    ipChart.resize();
    aqzChart.resize();
    juanChart.resize();
    yypccChart.resize();
});	
		
		
