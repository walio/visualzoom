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
    ws.send(message)
  },
  reconnect () {
    let outer = this
    this.client = this.uri.map(function (uri) {
      let ws = new WebSocket(outer.host + uri)
      ws.onopen = () => {
        outer.isConnected = true
      }
      ws.onclose = () => {
        outer.isConnected = false
      }
      return ws
    })
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
    let con = new Sock('ws://localhost/')
    con.addListener('logInfo', (ws, data) => {
      this.logInfoText += data
      let logInfo = document.getElementById('logInfo')
      logInfo.value = this.logInfoText
      logInfo.scrollTop = logInfo.scrollHeight
    })
    con.addListener('scanDev', (ws, data) => {
      if (data === 'Scanfinished') {
        this.$store.commit('finishScan')
      } else {
        data && this.$store.commit('addDev', data)
      }
    })
    con.addListener('restore', (ws, data) => {
      if (data === 'restoreFinished') {
        this.$message.success('数据恢复成功')
      } else {
        this.$store.commit('addDev', data)
      }
    })
    this.con = con
  },
  methods: {
    emit (uri, message = null) {
      if (uri === 'reconnect') {
        this.con.reconnect()
      } else if (message) {
        this.con.sendMessage(uri, message)
      } else {
        this.sendMessage(uri, '')
      }
    }
  },
  watch: {
    '$store.state.runStatus': {
      handler (status) {
        switch (status) {
          case 'Running':
            this.con.sendMessage('scanDev', 'start')
            break
          case 'Paused' :
            this.con.sendMessage('scanDev', 'pause')
            break
          case 'Stopped':
            this.con.sendMessage('scanDev', 'stop')
            break
        }
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
