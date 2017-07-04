import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)
export default new Vuex.Store({
  state: {
    devices: [],
    runStatus: 'Stopped',
    isConnected: false,
    message: '',
    isRestoring: false,
    stat: {}
  },
  mutations: {
    addDev (state, point) {
      state.devices.unshift(point)
    },
    startScan (state) {
      if (state.isConnected) {
        state.runStatus = 'Running'
        return true
      } else {
        Vue.prototype.$message.error('连接断开，无法开始扫描！')
        return false
      }
    },
    pauseScan (state) {
      state.runStatus = 'Paused'
    },
    stopScan (state) {
      state.runStatus = 'Stopped'
    },
    finishScan (state) {
      state.runStatus = 'Finished'
    },
    connectSuccess (state) {
      state.isConnected = true
    },
    connectFail (state) {
      state.isConnected = false
      state.runStatus = 'Paused'
      state.isRestoring = false
    },
    emit (state, message) {
      state.message = message
    },
    startRestore (state) {
      state.isRestoring = true
    },
    finishRestore (state) {
      state.isRestoring = false
    },
    setStat (state, stat) {
      state.stat = stat
    }
  }
})
