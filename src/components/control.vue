<template>
  <el-row>
    <el-button type='primary' @click='changeScanState'>{{ buttonText }}</el-button>
    <el-button type='primary' @click='stopScan'>结束扫描</el-button>
    <!--<el-button type='primary' @click='restoreScan'>从数据库恢复</el-button>-->
    <!--<el-button type='primary' @click='generateReport'>生成报告</el-button>-->
    <i :class='connectStatus' id='connection'></i>
    <textarea v-model='logInfoText' id='logInfo' readonly></textarea>
  </el-row>
</template>
<style>
  #logInfo{
    border: 0;
    padding: 0;
    float: right;
    resize: none;
    width: 50%;
    outline: none
  }
  #connection{
    margin-left: 1%
  }
</style>
<script>

  export default {
    data () {
      return {
        connectStatus: 'el-icon-circle-close',
        logInfoText: '扫描状态'
      }
    },
    computed: {
      buttonText () {
        switch (this.$store.state.runStatus) {
          case 'Running':
            return '暂停'
          case 'Paused':
            return '继续'
          case 'Stopped':
            return '开始'
          case 'Finished':
            return '重新开始'
          default:
            return '开始'
        }
      }
    },
    methods: {
      changeScanState () {
        if (!this.$store.state.isConnected) {
          this.$message.error('失败！连接断开')
        } else {
          switch (this.$store.state.runStatus) {
            case 'Running':
              this.$store.commit('pauseScan')
              this.$message.success('扫描暂停！')
              break
            case 'Paused':
            case 'Finished':
            case 'Stopped':
              this.$store.commit('startScan')
              this.$message.success('扫描继续！')
              break
          }
        }
      },
      stopScan () {
        if (!this.$store.state.isConnected) {
          this.$message.error('失败！连接断开')
        } else {
          this.$store.commit('stopScan')
          this.$message.success('扫描已终止！')
        }
      },
      restoreScan () {
        this.$store.commit('emit', 'restore')
      },
      generateReport () {
        this.$store.commit('emit', 'getStat')
      }
    },
    watch: {
      '$store.state.isConnected': {
        handler (status) {
          this.connectStatus = status ? 'el-icon-circle-check' : 'el-icon-circle-close'
          status ? this.$message.success('连接成功') : this.$message.error('连接断开')
        }
      }
    }
  }
</script>
