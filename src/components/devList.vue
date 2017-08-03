<template>
  <section>
    <el-table :data="devs" highlight-current-row v-loading="listLoading" style="margin-top: 2%;">
      <el-table-column v-for="(chs, eng) in cols" :label="chs" :prop="eng"></el-table-column>
    </el-table>
    <el-col :span="24" class="toolbar">
      <!--<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>-->
      <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :total="total" style="float:right;">
      </el-pagination>
    </el-col>
    <p>注：表格宽度自动设置为内容项最多的设备的项数，表头名称通过translate翻译，如无法翻译显示英文名称</p>
  </section>
</template>
<script>
  import axios from 'axios'
  export default {
    data () {
      return {
        page: 1,
        total: 0,
        listLoading: false,
        devs: [],
        cols: {},
        translate: {}
      }
    },
    mounted () {
      this.listLoading = true
      axios.get(`${this.$store.state.host}/config?fields=translate`).then((res) => {
        this.translate = res.data.translate
        this.getDevices()
      }).catch(() => {
        this.$message.error('获取翻译信息失败！')
      })
    },
    methods: {
      handleCurrentChange (page) {
        this.page = page
        this.getDevices()
      },
      getDevices () {
        axios.get(`${this.$store.state.host}/device?page=${this.page}`).then((res) => {
          let cols = {}
          res.data.devices.map((dev) => {
            for (let _ in dev) {
              if (!cols[_]) {
                cols[_] = this.translate[_] || _
              }
            }
          })
          this.devs = res.data.devices
          this.total = res.data.total
          this.cols = cols
          console.log(cols)
          console.log(this.cols)
          this.listLoading = false
        }).catch(() => {
          this.$message.error('获取设备信息失败！')
          this.listLoading = false
        })
      }
    }
  }
</script>
