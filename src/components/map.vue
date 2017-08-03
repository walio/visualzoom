<template>
  <div class="chart"></div>
</template>
<style>
  .anchorBL{
    display:none;
  }
  .chart{
    height: 100%;
  }
</style>
<script>
  import echarts from 'echarts/lib/echarts'
  import 'echarts/map/js/world'
  import 'echarts/extension/bmap/bmap'

  import axios from 'axios'

  const translate = (dev, translateJson) => {
    let ret = {}
    for (let _ in translateJson) {
      if (dev[_]) {
        ret[translateJson[_]] = dev[_]
      }
    }
    return ret
  }
  export default {
    data () {
      let outer = this
      let defaultOptions = {
        bmap: {
          center: [104.114129, 37.550339],
          zoom: 5,
          roam: true
          // 百度地图的自定义样式，见 http://developer.baidu.com/map/jsdevelop-11.htm
        },
        graphic: [
          {
            type: 'group',
            left: 'center',
            bottom: 0,
            children: [
              {
                type: 'rect',
                z: 100,
                top: 'middle',
                cursor: 'default',
                shape: {
                  width: 600,
                  height: 90
                },
                style: {
                  fill: 'rgba(150,150,150,0.3)',
                  shadowBlur: 8,
                  shadowOffsetX: 3,
                  shadowOffsetY: 3,
                  shadowColor: 'rgba(0,0,0,0.3)'
                }
              },
              {
                type: 'text',
                id: 'log',
                z: 100,
                left: 20,
                top: 'middle',
                cursor: 'default',
                style: {
                  fill: '#333',
                  text: '扫描log信息',
                  font: '14px Microsoft YaHei'
                }
              }
            ]
          }
        ],
        toolbox: {
          right: '1%',
          feature: {
            // todo: custom svg icons(public icons do not describe function precisely)
            myConfig: {
              title: '配置参数',
              icon: 'path://M811.964 657.448c22.365-47.836 89.141-26.277 131.539-62.541 21.859-18.696 20.957-95.351 0-115.051-40.434-38.01-106.791-24.595-124.726-74.022-18.01-49.63 44.365-81.674 48.692-137.276 2.229-28.65-52.558-82.159-81.283-81.279-55.452 1.701-92.891 58.081-140.512 35.816-47.832-22.355-26.469-89.113-62.734-131.481-18.671-21.813-95.178-20.913-114.85 0-38.011 40.407-24.63 106.739-74.04 124.667-49.636 18.009-82.497-38.366-137.313-48.664-28.237-5.305-82.144 52.544-81.263 81.26 1.702 55.453 58.092 92.881 35.831 140.506-22.368 47.836-89.144 26.308-131.545 62.573-21.852 18.689-20.951 95.318 0 115.011 40.441 38.013 106.791 24.601 124.726 74.031 18.02 49.652-44.481 81.606-48.832 137.241-2.242 28.659 52.577 82.198 81.31 81.307 55.492-1.721 92.982-58.087 140.631-35.81 47.855 22.37 26.249 89.164 62.515 131.587 18.675 21.845 95.278 20.942 114.96 0 38.027-40.463 24.699-106.829 74.15-124.774 49.654-18.019 81.602 44.482 137.243 48.833 28.669 2.242 82.228-52.591 81.335-81.331-1.722-55.484-58.111-92.957-35.833-140.603zM511.631 726.657c-112.254 0-203.249-90.994-203.249-203.241s90.995-203.241 203.249-203.241c112.251 0 203.249 90.994 203.249 203.241s-90.998 203.241-203.249 203.241z',
              onclick () {
                outer.$emit('showConfig')
              }
            },
            myStart: {
              title: '开始扫描',
              icon: 'path://M1576 927l-1328 738q-23 13-39.5 3t-16.5-36v-1472q0-26 16.5-36t39.5 3l1328 738q23 13 23 31t-23 31z',
              onclick () {
                switch (outer.$store.state.runStatus) {
                  case 'Running':
                    outer.$store.commit('pauseScan')
                    break
                  case 'Paused':
                  case 'Finished':
                  case 'Stopped':
                    outer.$store.commit('startScan')
                    break
                }
              }
            },
            myStop: {
              title: '结束扫描',
              icon: 'path://M1664 192v1408q0 26-19 45t-45 19h-1408q-26 0-45-19t-19-45v-1408q0-26 19-45t45-19h1408q26 0 45 19t19 45z',
              onclick () {
                outer.$store.commit('stopScan')
              }
            },
            myRestore: {
              title: '从数据库中恢复',
              icon: 'path://M896 768q237 0 443-43t325-127v170q0 69-103 128t-280 93.5-385 34.5-385-34.5-280-93.5-103-128v-170q119 84 325 127t443 43zm0 768q237 0 443-43t325-127v170q0 69-103 128t-280 93.5-385 34.5-385-34.5-280-93.5-103-128v-170q119 84 325 127t443 43zm0-384q237 0 443-43t325-127v170q0 69-103 128t-280 93.5-385 34.5-385-34.5-280-93.5-103-128v-170q119 84 325 127t443 43zm0-1152q208 0 385 34.5t280 93.5 103 128v128q0 69-103 128t-280 93.5-385 34.5-385-34.5-280-93.5-103-128v-128q0-69 103-128t280-93.5 385-34.5z',
              onclick () {
                outer.$store.commit('restore')
              }
            },
            myLoad: {
              title: '读取json数据',
              icon: 'path://M276.864 129.984h85.12v44.8H237.632v253.248c0 46.976-73.088 85.12-120.064 85.12 46.976 0 120.064 38.144 120.064 85.12v252.8h124.352v45.248h-85.12c-45.568-11.52-85.12-38.336-85.12-85.12v-170.304a85.12 85.12 0 0 0-85.12-85.12H64V470.528h42.56a85.12 85.12 0 0 0 85.12-85.12V215.104c0-47.04 38.144-85.12 85.184-85.12z m468.032 0a85.12 85.12 0 0 1 85.12 85.12v170.304a85.12 85.12 0 0 0 85.12 85.12h42.624v85.184H915.2a85.12 85.12 0 0 0-85.12 85.12v170.304a85.12 85.12 0 0 1-85.184 85.12h-85.12v-46.208H787.2V598.272c0-22.528 8.96-44.16 24.96-60.16s65.536-24.96 88.064-24.96c-22.528 0-72.128-8.96-88.064-24.96a85.12 85.12 0 0 1-24.96-60.16V173.12h-127.552V129.92h85.12z m-244.608 510.912a32 32 0 1 1 0 64 32 32 0 0 1 0-64z m-106.24 0a32 32 0 1 1 0 64 32 32 0 0 1 0-64z m212.544 0a32 32 0 1 1 0 64 32 32 0 0 1 0-64z',
              onclick () {
                alert('under development')
              }
            },
            dataView: {
              title: '设备列表',
              lang: ['测试标题', '关闭', '刷新'],
              optionToContent () {
                alert('under development')
                return '设备列表'
              }
            }
          }
        },
        title: {
          text: '网络摄像头大规模扫描地图',
          left: 'center',
          textStyle: {
            fontFamily: 'Microsoft YaHei',
            color: '#fff',
            fontSize: 24
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: (params, ticket, callback) => {
            let tip = ''
            for (let attr in params.value[2]) {
              tip += (params.value[2][attr] ? attr + ':' + params.value[2][attr] + '<br />' : '')
            }
            return tip
          }
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
          symbolSize: 5,
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
      return {
        options: defaultOptions,
        data: []
      }
    },
    mounted () {
      let chart = echarts.init(this.$el)
      chart.setOption(this.options)
      axios.get(`${this.$store.state.host}/config?fields=styleJson`).then((res) => {
        chart.setOption({
          bmap: {
            mapStyle: {
              styleJson: res.data.styleJson
            }
          }
        })
      })
      window.addEventListener('resize', function () {
        chart.resize()
      })
      this.chart = chart
    },
    watch: {
      '$store.state.logInfo': {
        handler (log) {
          let _
          if (log.length < 4) {
            _ = log.join('\n')
          } else {
            _ = log.splice(log.length - 5).join('\n')
          }
          this.chart.setOption({
            graphic: {
              id: 'log',
              style: {
                text: _
              }
            }
          })
        },
        deep: true
      },
      '$store.state.devices': {
        handler (dev) {
          this.data.push({
            name: dev[0].city || dev[0].country || dev[0].continent,
            value: [dev[0].lon, dev[0].lat, translate(dev[0])]
          })
          this.chart.setOption({
            series: [{
              name: '脆弱主机',
              data: this.data
            }]
          })
        },
        deep: true
      }
    }
  }
</script>
