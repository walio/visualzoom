import Vue from 'vue'
import Router from 'vue-router'
import map from '@/components/map'
import control from '@/components/control'
import websocket from '@/components/websocket'
import pie from '@/components/pie'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Hello',
      component: {map, control, websocket, pie}
    }
  ]
})
