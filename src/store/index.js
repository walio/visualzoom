import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
Vue.use(Vuex)
export default new Vuex.Store({
  state: {
    devices: [],
    logInfo: [],
    runStatus: 'Stopped',
    isConnected: false,
    total: 1000,
    host: 'http://localhost',
    wshost: 'ws://localhost/'
  },
  mutations: {
    addDev (state, dev) {
      state.devices.unshift(dev)
    },
    addLog (state, log) {
      state.logInfo.unshift(log)
    },
    startScan (state) {
      if (state.isConnected) {
        axios.get(`${state.host}/action/start`)
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
        axios.get(`${state.host}/action/pause`)
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
        axios.get(`${state.host}/action/stop`)
        state.runStatus = 'Stopped'
        Vue.prototype.$message.success('已停止扫描！')
        return true
      } else {
        Vue.prototype.$message.error('连接断开，无法停止扫描！')
        return false
      }
    },
    restore (state) {
      if (state.isConnected) {
        axios.get(`${state.host}/action/restore`)
        return true
      } else {
        Vue.prototype.$message.error('连接断开，无法回复数据！')
        return false
      }
    },
    finishScan (state) {
      state.runStatus = 'Finished'
      Vue.prototype.$message.success('扫描已结束！')
    },
    connectSuccess (state) {
      state.isConnected = true
      Vue.prototype.$message.success('已连接！')
    },
    connectFail (state) {
      state.isConnected = false
      Vue.prototype.$message.error('连接断开！')
    }
  }
})
