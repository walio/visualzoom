<template>
  <div></div>
</template>
<script>
import io from 'socket.io-client'
export default {
  data () {
    return {
      logInfoText: '此处为扫描日志'
    }
  },
  mounted () {
    let socket = io('http://47.93.218.135:8080')
    // todo: set init option, like attack/verify mode, device choose
    socket.emit('init', '123')

    socket.on('connect', () => {
      this.$store.commit('connectSuccess')
    })
    socket.on('connect_error', () => {
      this.$store.commit('connectFail')
    })
    socket.on('disconnect', () => {
      this.$confirm('与后台连接已断开，是否重新连接？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(() => {
        socket.socket.connect()
        this.$store.commit('startScan') && this.$message.success('扫描继续！')
      }).catch(() => {
        this.$message.warning('已断开连接')
        socket.disconnect()
        this.$store.commit('connectFail')
      })
    })
    socket.on('reportNext', (data) => {
      data && this.$store.commit('addDev', data)
      this.$store.state.runStatus === 'Running' && socket.emit('scanNext')
    })
    socket.on('scanFinish', () => {
      this.$store.commit('finishScan')
    })
    socket.on('reportNextRestore', (data) => {
      this.$store.commit('addDev', data)
      socket.emit('restoreNext')
    })
    socket.on('restoreFinish', () => {
      this.$message.success('数据恢复成功')
    })
    socket.on('reportStat', (data) => {
      console.log('report stat')
      console.log(data)
      this.$store.commit('setStat', data)
    })
    socket.on('logInfo', (data) => {
      this.logInfoText += data
      let logInfo = document.getElementById('logInfo')
      logInfo.value = this.logInfoText
      logInfo.scrollTop = logInfo.scrollHeight
    })
    this.socket = socket
  },
  watch: {
    '$store.state.runStatus': {
      handler (status) {
        switch (status) {
          case 'Running':
            this.socket.emit('scanNext')
            break
          case 'Stopped':
            this.socket.emit('clear')
            break
        }
      }
    },
    '$store.state.message': {
      handler (message) {
        this.socket.emit(message)
      }
    }
  }
}
</script>
