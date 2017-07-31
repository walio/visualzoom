<template>
  <el-row>
    <el-button type='primary' @click='$emit("showConfig")'>设置参数</el-button>
    <el-button type='primary' @click='changeScanState'>{{ buttonText }}</el-button>
    <el-button type='primary' @click='$store.commit("stopScan")'>结束扫描</el-button>
    <!--<el-button type='primary' @click='restoreScan'>从数据库恢复</el-button>-->
    <!--<el-button type='primary' @click='$emit("showReport")'>生成报告</el-button>-->
    <i :class='connectIcon' id='connection' @click='$emit("reconnect")' title="重新连接" style="cursor: pointer;"></i>
  </el-row>
</template>
<style>
  #connection{
    margin-left: 1%
  }
</style>
<script>
  export default {
    data () {
      return {
        connectIcon: 'el-icon-circle-close'
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
        switch (this.$store.state.runStatus) {
          case 'Running':
            this.$store.commit('pauseScan')
            break
          case 'Paused':
          case 'Finished':
          case 'Stopped':
            this.$store.commit('startScan')
            break
        }
      },
      restoreScan () {
        if (this.$store.state.isConnected) {
          this.$emit('restore')
        } else {
          this.$message.error('失败！连接断开')
        }
      }
    },
    watch: {
      '$store.state.isConnected': {
        handler (status) {
          this.connectIcon = status ? 'el-icon-circle-check' : 'el-icon-circle-close'
          status ? this.$message.success('连接成功') : this.$message.error('连接断开')
        }
      }
    }
  }
</script>
