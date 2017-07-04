<template>
  <div class='full-height'>
    <div class='chart'></div>
    <el-button type='primary' @click='downloadReport'>下载报告</el-button>
  </div>
</template>
<script>
  import echarts from 'echarts/lib/echarts'
  import JsPDF from 'jspdf'

  const defaultOptions = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      x: 'left',
      data: ['安全设备', '信息泄露设备', '可攻破设备']
    },
    series: [
      {
        name: '访问来源',
        type: 'pie',
        selectedMode: 'single',
        radius: [0, '60%'],

        label: {
          normal: {
            position: 'inner'
          }
        },
        labelLine: {
          normal: {
            show: false
          }
        },
        data: []
      }
    ]
  }
  export default {
    data () {
      return {
        options: defaultOptions
      }
    },
    mounted () {
      let chart = echarts.init(this.$el.querySelector('.chart'))
      this.options.series[0].data = [
        {value: this.$store.state.devices.length, name: '脆弱主机'},
        {value: this.$store.state.total - this.$store.state.devices.length, name: '安全设备'}
      ]
      chart.setOption(this.options)
      window.addEventListener('resize', function () {
        chart.resize()
      })
      this.chart = chart
    },
    methods: {
      downloadReport () {
        let doc = new JsPDF()
        doc.addImage(this.chart.getDataURL(), 'PNG', 20, 60, 600, 330)
        doc.save()
      }
    },
    watch: {
      '$store.state.stat': {
        handler (data) {
          let options = this.chart.getOption()
          console.log(options)
          options.series[0].data = [
            {value: this.$store.state.devices.length, name: '脆弱主机'},
            {value: this.$store.state.total - this.$store.state.devices.length, name: '安全设备'}
          ]
          this.options = options
          this.chart.setOption(options)
        },
        deep: true
      }
    }
  }

</script>
