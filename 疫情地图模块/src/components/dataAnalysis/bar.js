import React, { Component } from "react";
import { StyleSheet, View } from "react-native";
import { ECharts } from "react-native-echarts-wrapper";
import {axios} from './App.js'
import dateTansfer,{year} from './date.js';

var t=new Date();
var today=dateTansfer(t);
//获取现存确诊人数最多的五个国家
export var countries=[];

//获取前十国家新增确诊人数
var num=[];

export default class WorldBar extends Component {
  option = {
    title: {
        text: '',
		top:'8%',
		left:'center'
    },
    tooltip: {
        trigger: 'axis'
    },
    grid: {
        left: '3%',
        right: '5%',
        bottom: '5%',
		top: '18%',
        containLabel: true
    },
    toolbox: {
        feature: {
            saveAsImage: {}
        }
    },
    xAxis: {
        type: 'category',
        axisLabel: {
		  interval:0,
          rotate:50  
        },		
        data: countries
    },
    yAxis: {
		type: 'value'
    },
    series: [
        {
            type: 'bar',
            data: num
        }]
  };
 
  render() {
    var t=new Date();
    var today=dateTansfer(t);
	//console.log(today);
	axios
         .post("http://192.168.1.7:8081/request/map/foreignMap/select",{"Return":"topTen","Data":today})
         .then((res)=>{
            var data=res.data.message;
    		console.log(data);
    		for(var i=0;i<data.length;i++){
				countries[i]=data[i].country;
				num[i]=data[i].confirmedNumber;
			}
			console.log(num);
			console.log(countries);
        });
	
	return (
      <View style={styles.chartContainer}>
        <ECharts option={this.option} />
      </View>
    );
  }
}
 
const styles = StyleSheet.create({
  chartContainer: {
    height:250
  }
});
