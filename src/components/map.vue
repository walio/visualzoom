<template>
  <div class="chart"></div>
</template>
<script>
  import echarts from 'echarts/lib/echarts'
  import 'echarts/map/js/world'
  import 'echarts/extension/bmap/bmap'

  const defaultOptions = {
    bmap: {
      center: [104.114129, 37.550339],
      zoom: 1,
      roam: true,
      // 百度地图的自定义样式，见 http://developer.baidu.com/map/jsdevelop-11.htm
      mapStyle: {
        styleJson: [{
          'featureType': 'water',
          'elementType': 'all',
          'stylers': {
            'color': '#d1d1d1'
          }
        }, {
          'featureType': 'land',
          'elementType': 'all',
          'stylers': {
            'color': '#f3f3f3'
          }
        }, {
          'featureType': 'railway',
          'elementType': 'all',
          'stylers': {
            'visibility': 'off'
          }
        }, {
          'featureType': 'highway',
          'elementType': 'all',
          'stylers': {
            'color': '#fdfdfd'
          }
        }, {
          'featureType': 'highway',
          'elementType': 'labels',
          'stylers': {
            'visibility': 'off'
          }
        }, {
          'featureType': 'arterial',
          'elementType': 'geometry',
          'stylers': {
            'color': '#fefefe'
          }
        }, {
          'featureType': 'arterial',
          'elementType': 'geometry.fill',
          'stylers': {
            'color': '#fefefe'
          }
        }, {
          'featureType': 'poi',
          'elementType': 'all',
          'stylers': {
            'visibility': 'off'
          }
        }, {
          'featureType': 'green',
          'elementType': 'all',
          'stylers': {
            'visibility': 'off'
          }
        }, {
          'featureType': 'subway',
          'elementType': 'all',
          'stylers': {
            'visibility': 'off'
          }
        }, {
          'featureType': 'manmade',
          'elementType': 'all',
          'stylers': {
            'color': '#d1d1d1'
          }
        }, {
          'featureType': 'local',
          'elementType': 'all',
          'stylers': {
            'color': '#d1d1d1'
          }
        }, {
          'featureType': 'arterial',
          'elementType': 'labels',
          'stylers': {
            'visibility': 'off'
          }
        }, {
          'featureType': 'boundary',
          'elementType': 'all',
          'stylers': {
            'color': '#fefefe'
          }
        }, {
          'featureType': 'building',
          'elementType': 'all',
          'stylers': {
            'color': '#d1d1d1'
          }
        }, {
          'featureType': 'label',
          'elementType': 'labels.text.fill',
          'stylers': {
            'color': '#999999'
          }
        }]
      }
    },
    backgroundColor: '#404a59',
    title: {
      text: '网络摄像头大规模扫描地图',
      left: 'center',
      textStyle: {
        color: '#fff'
      }
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      y: 'bottom',
      x: 'right',
      data: ['脆弱主机'],
      textStyle: {
        color: '#fff'
      }
    },
    series: [{
      name: '脆弱主机',
      type: 'effectScatter',
      coordinateSystem: 'bmap',
      data: [],
      symbolSize: function (val) {
        return val[2] * 5
      },
      label: {
        normal: {
          formatter: '{b}',
          position: 'right',
          show: false
        },
        emphasis: {
          show: true
        }
      },
      itemStyle: {
        normal: {
          color: 'red'
        }
      }
    }]
  }
  export default {
    data () {
      return {
        options: defaultOptions
      }
    },
    mounted () {
      let chart = echarts.init(this.$el)
      chart.setOption(this.options)
      window.addEventListener('resize', function () {
        chart.resize()
      })
      this.chart = chart
    },
    watch: {
      '$store.state.devices': {
        handler (dev) {
          let options = this.chart.getOption()
          // todo: insert into pie chart
          options.series[0].data.push({
            name: dev[0].addr,
            value: [dev[0].lon, dev[0].lat, 1]
          })
          this.options = options
          this.chart.setOption(options)
        },
        deep: true
      }
    }
  }
</script>
