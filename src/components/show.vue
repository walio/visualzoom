<template>
  <div id="app">
    <el-row>
      <echart-map></echart-map>
    </el-row>
    <control-panel></control-panel>
    <el-dialog title='检测报告' :visible.sync="pieChartVisible">
      <echart-pie></echart-pie>
    </el-dialog>
    <websocket></websocket>
    <router-view></router-view>
  </div>
</template>

<script>
  export default {
    name: 'app',
    data () {
      return {
        pieChartVisible: false
      }
    },
    watch: {
      '$store.state.stat': {
        handler (data) {
          this.pieChartVisible = true
        },
        deep: true
      }
    }
  }
</script>

<style>
  html,body{
    height: 100%;
  }
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    height: 100%;
  }
  .el-row:first-child {
    height: 85%;
    margin-bottom: 2%;
  }
  .chart{
    width: 100%;
    height: 100%;
  }
  .el-dialog{
    height: 70%;
  }
  .el-dialog__body{
    height: 70%;
    clear: all;
  }
  .full-height{
    height: 100%;
  }
</style>
