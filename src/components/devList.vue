<template>
  <section>
    <el-table :data="devs" highlight-current-row v-loading="listLoading" style="margin-top: 2%;">
      <el-table-column v-for="(chs, eng) in cols" :label="chs" :prop="eng" sortable></el-table-column>
    </el-table>
    <el-col :span="24" class="toolbar">
      <!--<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>-->
      <el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :total="total" style="float:right;">
      </el-pagination>
    </el-col>
    <p>注：表格由数据项自适应宽度，表头通过translate的json数据翻译，如无翻译则显示英文</p>
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
      axios.get(`${this.$store.state.host}/style?fields=translate`).then((res) => {
        this.translate = (res.data.translate || this.translate)
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
        axios.get(`${this.$store.state.host}/devices?page=${this.page}`).then((res) => {
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
          this.listLoading = false
        }).catch((err) => {
          this.$message.error('获取设备信息失败！')
          this.listLoading = false
          console.log(err)
        })
      }
    }
  }
</script>
