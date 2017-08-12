import Vue from 'vue'
import Router from 'vue-router'
import home from '@/components/home'
import admin from '@/components/admin'
import managePoc from '@/components/managePoc'
import mapColor from '@/components/mapColor'
import devList from '@/components/devList'
import ipinput from '@/components/ipinput'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: home
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
    },
    {
      path: '/admin',
      component: admin,
      name: '',
      admin: true,
      iconCls: 'fa fa-map-marker',
      leaf: true, // 只有一个节点
      children: [
        { path: '/admin/mapColor', component: mapColor, name: '设置' }
      ]
    },
    {
      path: '/admin',
      component: admin,
      name: '',
      admin: true,
      iconCls: 'fa fa-list',
      leaf: true, // 只有一个节点
      children: [
        { path: '/admin/devList', component: devList, name: '设备列表' }
      ]
    },
    {
      path: '/admin',
      component: admin,
      name: '',
      iconCls: 'fa fa-list',
      leaf: true, // 只有一个节点
      children: [
        { path: '/admin/ipinput', component: ipinput, name: 'ip输入组件' }
      ]
    }
  ]
})
