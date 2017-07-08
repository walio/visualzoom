<template>
  <div></div>
</template>
<script>
function Sock (host) {
  this.host = host
  this.client = []
  this.uri = []
  this.isConnected = false
}
Sock.prototype = {
  addListener (uri, handler) {
    let index = this.uri.indexOf(uri)
    let ws
    if (index === -1) {
      ws = new WebSocket(this.host + uri)
      this.client.push(ws)
      this.uri.push(uri)
    } else {
      ws = this.client[index]
    }
    ws.onopen = () => {
      this.isConnected = true
    }
    ws.onclose = () => {
      this.isConnected = false
      // todo: reconnect
    }
    ws.onmessage = (e) => { handler(ws, e.data) }
  },
  sendMessage (uri, message) {
    let index = this.uri.indexOf(uri)
    let ws
    if (index === -1) {
      ws = new WebSocket(this.host + uri)
      this.client.push(ws)
      this.uri.push(uri)
    } else {
      ws = this.client[index]
    }
    console.log(this)
    ws.send(message)
  }

}

export default {
  data () {
    return {
      logInfoText: '此处为扫描日志',
      con: {}
    }
  },
  mounted () {
    // todo: set init option, like attack/verify mode, device choose
    let con = new Sock('ws://localhost/')
    con.addListener('logInfo', (ws, data) => {
      this.logInfoText += data
      let logInfo = document.getElementById('logInfo')
      logInfo.value = this.logInfoText
      logInfo.scrollTop = logInfo.scrollHeight
    })
    con.addListener('scanDev', (ws, data) => {
      if (data === 'finishScan') {
        this.$store.commit('finishScan')
        this.$message.info('扫描结束')
      } else {
        console.log(data)
        data && this.$store.commit('addDev', data)
        this.$store.state.runStatus === 'Running' && this.con.sendMessage('scanDev', 'scanNext')
      }
    })
    con.addListener('restore', (ws, data) => {
      if (data === 'restoreFinish') {
        this.$message.success('数据恢复成功')
      } else {
        this.$store.commit('addDev', data)
      }
    })
    con.addListener('getStat', (ws, data) => {
      console.log('report stat')
      console.log(data)
      this.$store.commit('setStat', data)
    })
    this.con = con
  },
  watch: {
    '$store.state.runStatus': {
      handler (status) {
        switch (status) {
          case 'Running':
            this.con.sendMessage('scanDev', 'scanNext')
            break
          case 'Stopped':
            this.con.sendMessage('clear')
            break
        }
      }
    },
    '$store.state.message': {
      handler (message) {
        this.con.sendMessage(message, 'trigger')
      }
    },
    'con.isConnected': {
      handler (isConnected) {
        if (isConnected) {
          this.$store.commit('connectSuccess')
          this.$message.success('连接成功')
        } else {
          this.$store.commit('connectFail')
          this.$message.error('连接断开')
        }
      }
    }
  }
}
</script>
