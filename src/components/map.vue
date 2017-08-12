<template>
  <div id="map"></div>
</template>
<style>
  .anchorBL{
    display:none;
  }
</style>
<script>
  import echarts from 'echarts/lib/echarts'
  import 'echarts/map/js/world'
  import 'echarts/extension/bmap/bmap'
  import axios from 'axios'

  export default {
    data () {
      let outer = this
      let tPos = {
        left: 0,
        top: 0
      }

      let lastPoint = [0, 0]
      let counter = 0
      let defaultOptions = {
        bmap: {
          center: [104.114129, 37.550339],
          zoom: 5,
          roam: true
          // 百度地图的自定义样式，见 http://developer.baidu.com/map/jsdevelop-11.htm
        },
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
                axios.get(`${outer.$store.state.host}/devices`).then((res) => {
                  axios.get(`${outer.$store.state.host}/devices?size=${res.data.total}`).then((res) => {
                    outer.$store.commit('addDevs', res.data.devices)
                    outer.$message.success('恢复完毕')
                  })
                }).catch(() => {
                  outer.$message.error('恢复失败！')
                })
              }
            },
            dataView: {
              title: '设备列表',
              optionToContent (opt) {
                return '<table style="width:100%;text-align:center"><tbody><thead style="font: 25px bold;"><td>ip地址</td><td>地址</td></thead>' +
                  opt.series[0].data.map((dev) => {
                    return `<tr><td>${dev.value[2].ip}:${dev.value[2].port}</td><td> ${dev.name}</td></tr>`
                  }).join('') +
                  '</tbody></table>'
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
          enterable: true,
          hideDelay: 150,
          transitionDuration: 0,
          backgroundColor: 'rgba(255, 255, 255, 1)',
          textStyle: {
            color: '#7a8288',
            fontSize: 12
          },
          borderWidth: 1,
          borderColor: '#7a8288',
          padding: [15, 10],
          extraCssText: 'box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);cursor: default; text-align:left;line-height:1.8em',
          formatter: (params, ticket, callback) => {
            let tip = `<div style="border-bottom: 1px solid rgba(0, 0, 0, .3);  font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">${params.value[2]['ip']}</div>`
            if (params.value[2]['device_type']) {
              tip += `${outer.translate['device_type'] || 'device_type'} : ${params.value[2]['device_type']}<br />`
            }
            if (params.value[2]['port']) {
              tip += `${outer.translate['port'] || 'port'} : ${params.value[2]['port']}<br />`
            }
            for (let attr in params.value[2]) {
              let _ = params.value[2][attr]
              switch (attr) {
                case 'login_url':
                  _ = `<a href=${_} target="_blank">${_}</a>`
                  break
                case 'lat':
                case 'lon':
                case 'city':
                case 'country':
                case 'continent':
                case 'ip':
                case 'device_type':
                case 'port':
                  continue
              }
              attr = outer.translate[attr] || attr
              tip += (_ ? `${attr} : ${_}<br />` : '')
            }
            return tip
          },
          position (point, params, dom, rect, size) {
            // https://github.com/silverHugh/silverhugh.github.io/blob/master/_project/tower-map/tower_map.js
            /* In the leastArea, tPos won't be changed more than twice */
            let leastArea = 15
            /* Set the offset of tooltip */
            let mapSize = size.viewSize
            let tooltipSize = size.contentSize
            let margin = 50
            let offsetX = point[0] > (mapSize[0] - tooltipSize[0])
              ? -(tooltipSize[0] + margin) : margin
            let offsetY = -tooltipSize[1] / 2

            if (Math.abs(point[0] - lastPoint[0]) < leastArea &&
              Math.abs(point[1] - lastPoint[1]) < leastArea &&
              counter >= 2) {
              return tPos
            }
            if (Math.abs(point[0] - lastPoint[0]) >= leastArea ||
              Math.abs(point[1] - lastPoint[1]) >= leastArea) {
              counter = 0
            }
            counter += 1
            if (counter === 1) {
              tPos.left = point[0] + offsetX
              tPos.top = point[1] + offsetY
              lastPoint = [point[0], point[1]]
              dom.style.display = 'none'
            }
            if (counter === 2) {
              let realX = dom.offsetLeft
              let realY = dom.offsetTop
              tPos.left += point[0] - realX + offsetX
              tPos.top += point[1] - realY + offsetY
              dom.style.display = 'block'
            }
            return tPos
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
          type: 'scatter',
          coordinateSystem: 'bmap',
          symbol: 'path://M181.379879 223.676768l-114.064808 290.779798 507.715232 199.157656 187.909172-261.815596L181.379879 223.676768m645.306182 330.35507L768.753778 701.728323l95.968969 101.555717 101.38893-258.47208-139.425616 9.219878m-69.818182-46.028282l-118.574546 166.516363 101.541495 39.833859 72.422142-184.621253-55.389091-21.728969M139.142465 620.662949l66.963394 26.479192-26.296889 57.686627H57.888323v52.061091H214.065131v-1.700202l40.515233-88.877253 73.593535 29.101253 22.791758-57.633617-189.039192-74.749414-22.784 57.632323m142.911353-422.375434l532.067556 627.426263m0-627.426263L259.251717 825.713778',
          data: [],
          symbolSize: 20,
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
              color (para) {
                let _
                try {
                  _ = outer.deviceColor[para['value'][2].device_type]
                } catch (err) {
                  _ = 'red'
                }
                return _
              }
            }
          }
        }]
      }
      return {
        options: defaultOptions,
        translate: {},
        deviceColor: {}
      }
    },
    mounted () {
      this.$el.style.height = document.documentElement.clientHeight + 'px'
      let chart = echarts.init(this.$el, 'dark')
      chart.setOption(this.options)
      axios.get(`${this.$store.state.host}/style?fields=styleJson,translate,deviceColor`).then((res) => {
        chart.setOption({
          bmap: {
            mapStyle: {
              styleJson: res.data.styleJson
            }
          }
        })
        this.translate = (res.data.translate || this.translate)
        this.deviceColor = (res.data.deviceColor || this.deviceColor)
      })
      window.addEventListener('resize', function () {
        chart.resize()
      })
      this.chart = chart
    },
    watch: {
      '$store.state.devices': {
        handler (devices) {
          let data = devices.map((dev) => {
            return {
              name: dev.country,
              value: [dev.lon, dev.lat, dev]
            }
          })
          this.chart.setOption({
            series: [{
              name: '脆弱主机',
              data: data
            }]
          })
        },
        deep: true
      }
    },
    methods: {
      locate (lat, lon) {
        this.chart.setOption({
          bmap: {
            center: [parseFloat(lon), parseFloat(lat)],
            zoom: 14,
            roam: true
            // 百度地图的自定义样式，见 http://developer.baidu.com/map/jsdevelop-11.htm
          }
        })
      }
    }
  }
</script>
