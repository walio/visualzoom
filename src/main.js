
import Vue from 'vue'
import Vuex from 'vuex'
import {Row, Button, Icon, Message, MessageBox, Dialog} from 'element-ui'
import App from './App'
import router from './router'
import store from './store'
import map from './components/map'
import control from './components/control'
import pie from './components/pie'
import websocket from './components/websocket'

Vue.use(Vuex)
Vue.use(Row)
Vue.use(Button)
Vue.use(Icon)
Vue.use(Dialog)

Vue.prototype.$confirm = MessageBox.confirm
Vue.prototype.$message = Message

Vue.component('echart-map', map)
Vue.component('echart-pie', pie)
Vue.component('control-panel', control)
Vue.component('websocket', websocket)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App/>',
  components: { App }
})
