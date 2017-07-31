import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)
export default new Vuex.Store({
  state: {
    devices: [],
    runStatus: 'Stopped',
    isConnected: false,
    total: 1000
  },
  mutations: {
    addDev (state, point) {
      console.log(point)
      state.devices.unshift(JSON.parse(point))
    },
    startScan (state) {
      if (state.isConnected) {
        state.runStatus = 'Running'
        Vue.prototype.$message.success('已开始扫描！')
        return true
      } else {
        Vue.prototype.$message.error('连接断开，无法开始扫描！')
        return false
      }
    },
    pauseScan (state) {
      if (state.isConnected) {
        state.runStatus = 'Paused'
        Vue.prototype.$message.success('已暂停扫描！')
        return true
      } else {
        Vue.prototype.$message.error('连接断开，无法暂停扫描！')
        return false
      }
    },
    stopScan (state) {
      if (state.isConnected) {
        state.runStatus = 'Stopped'
        Vue.prototype.$message.success('已停止扫描！')
        return true
      } else {
        Vue.prototype.$message.error('连接断开，无法停止扫描！')
        return false
      }
    },
    finishScan (state) {
      state.runStatus = 'Finished'
      Vue.prototype.$message.success('扫描已结束！')
    },
    connectSuccess (state) {
      state.isConnected = true
    },
    connectFail (state) {
      state.isConnected = false
    }
  }
})
