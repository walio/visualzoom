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
      con: {}
    }
  },
  mounted () {
    let con = new Sock(this.$store.state.wshost)
    con.addListener('log', (ws, data) => {
      this.$store.commit('addLog', data)
    })
    con.addListener('dev', (ws, data) => {
      try {
        data && this.$store.commit('addDev', JSON.parse(data))
      } catch (err) {
        switch (data) {
          case 'scanFinished':
            this.$store.commit('finishScan')
            break
          case 'stopScanSuccess':
            this.$message.success('结束扫描成功')
            break
          case 'restoreFinished':
            this.$message.success('恢复完毕')
            break
        }
      }
    })
    this.con = con
  },
  methods: {
    emit (uri, message = null) {
      if (message) {
        this.con.sendMessage(uri, message)
      } else {
        this.con.sendMessage(uri, '')
      }
    },
    reconnect () {
      this.con.reconnect()
    }
  },
  watch: {
    'con.isConnected': {
      handler (isConnected) {
        if (isConnected) {
          this.$store.commit('connectSuccess')
        } else {
          this.$store.commit('connectFail')
        }
      }
    }
  }
}
</script>
