
import Vue from 'vue'
import Vuex from 'vuex'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-default/index.css'
import 'font-awesome/css/font-awesome.min.css'
import App from './App'
import router from './router'
import store from './store'
import map from './components/map'
import control from './components/control'
import pie from './components/pie'
import websocket from './components/websocket'

Vue.use(Vuex)
Vue.use(ElementUI)

Vue.component('echart-map', map)
Vue.component('echart-pie', pie)
Vue.component('control-panel', control)
Vue.component('websocket', websocket)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  // el: '#app',
  router,
  store,
  // template: '<App/>',
  // components: { App }
  render: h => h(App)
}).$mount('#app')
