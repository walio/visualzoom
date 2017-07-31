import Vue from 'vue'
import Router from 'vue-router'
import home from '@/components/home'
import admin from '@/components/admin'
import managePoc from '@/components/managePoc'
import ipInput from '@/components/ipInput'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: home
    },
    {
      path: '/ip',
      name: 'sss',
      component: ipInput,
      hidden: true
    },
    {
      path: '/admin',
      component: admin,
      name: '',
      admin: true,
      iconCls: 'fa fa-folder',
      leaf: true, // 只有一个节点
      children: [
        { path: '/admin/viewPoc', component: managePoc, name: '脚本管理' }
      ]
    }
  ]
})
