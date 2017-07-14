import Vue from 'vue'
import Router from 'vue-router'
import map from '@/components/show'
import home from '@/components/manage'
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
      component: home,
      name: '',
      iconCls: 'fa fa-folder',
      leaf: true, // 只有一个节点
      children: [
        { path: '/admin/viewPoc', component: viewPoc, name: '脚本管理' }
      ]
    }
  ]
})
