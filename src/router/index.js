import Vue from 'vue'
import Router from 'vue-router'
import map from '@/components/show'
import home from '@/components/manage'
import addPoc from '@/components/addPoc'
import viewPoc from '@/components/viewPoc'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'show',
      component: map,
      hidden: true
    },
    {
      path: '/admin',
      name: '添加脚本',
      component: home,
      children: [
        { path: '/form', component: addPoc, name: '脚本' },
        { path: '/table', component: viewPoc, name: '已添加脚本' }
      ]
    }
  ]
})
