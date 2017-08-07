
import Vue from 'vue'
import Vuex from 'vuex'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-default/index.css'
import 'font-awesome/css/font-awesome.min.css'
import App from './App'
import router from './router'
import store from './store'
import map from './components/map'
import report from './components/report'
import config from './components/config'
import websocket from './components/websocket'

Vue.use(Vuex)
Vue.use(ElementUI)

Vue.component('echart-map', map)
Vue.component('report', report)
Vue.component('config', config)
Vue.component('websocket', websocket)

// Vue.prototype.$websocket = websocket
// Vue.config.productionTip = false
/* eslint-disable no-new */
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
