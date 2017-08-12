<template>
<el-dialog title='配置选项' :visible.sync="visible">
  <el-col style="margin-top: 3%;margin-bottom: 3%;text-align: center;">
    <el-form :model="config" label-width="25%" id="config">
      <el-form-item
        v-for="(ipSeg, index) in config.ip_ranges"
        label="ip地址段"
      >
        <el-col :span="12">{{ `${ipSeg.start} - ${ipSeg.end} : ${ipSeg.port}` }}</el-col>
        <el-col :span="4" style="float: right;"><el-button @click.prevent="removeItem(config.ip_ranges, index)">删除</el-button></el-col>
      </el-form-item>
      <el-form-item
        v-for="(query, index) in config.zoomeye_queries"
        label="ZoomEye查询字符串"
      >
        <el-col :span="12">{{ query }}</el-col>
        <el-col :span="4" style="float: right;"><el-button @click.prevent="removeItem(config.zoomeye_queries, index)">删除</el-button></el-col>
      </el-form-item>
    </el-form>
    <el-form :model="configEdit" :rules="validateConfigEdit" ref="configEdit" label-width="10%">
      <el-form-item
        label="ip地址"
        prop="ipSeg"
      >
        <el-col :span="8"><ip-input :ip="configEdit.ipSeg.start" :on-change="changeIp('start')"></ip-input></el-col>
        <el-col :span="1">-</el-col>
        <el-col :span="8"><ip-input :ip="configEdit.ipSeg.end" :on-change="changeIp('end')"></ip-input></el-col>
        <el-col :span="1">:</el-col>
        <el-col :span="2"><el-input v-model="configEdit.ipSeg.port"></el-input></el-col>
        <el-col :span="3" :offset="1"><el-button @click.prevent="addIpSeg()">增加</el-button></el-col>
      </el-form-item>
      <el-form-item
        label="查询串"
        prop="zoomQuery"
      >
        <el-col :span="17"><el-input v-model="configEdit.zoomQuery"></el-input></el-col>
        <el-col :span="3" :offset="4"><el-button @click.prevent="addZoomQuery()">增加</el-button></el-col>
      </el-form-item>
      <el-form-item label="poc：">
        <el-col :span="17">
          <el-select style="width:100%;" v-model="config.selected_poc" placeholder="请选择Poc内容">
            <el-option
              v-for="poc in pocs"
              :label="poc.name"
              :value="poc.name">
              <span style="float: left">{{ poc.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ poc.device_type }}</span>
            </el-option>
          </el-select>
        </el-col>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm()">提交</el-button>
        <el-button @click="resetForm()">重置</el-button>
      </el-form-item>
    </el-form>
  </el-col>
</el-dialog>
</template>
<style>
</style>
<script>
  import axios from 'axios'
  export default{
    data () {
      let validateAddIp = (rule, value, callback) => {
        // todo: validate ip
        if (!value.start && !value.end) {
          callback(new Error('ip不能为空'))
        }
        if (isNaN(parseInt(value.port))) {
          callback(new Error('端口号必须为数字'))
        }
        if (parseInt(value.port) < 0 || parseInt(value.port) > 65536) {
          callback(new Error('端口号必须在0-65536范围内'))
        }
      }
      let validateAddZoom = (rule, value, callback) => {
        if (!value) {
          callback(new Error('查询字串不能为空'))
        }
      }
      return {
        visible: false,
        pocs: [
        ],
        config: {
          ip_ranges: [],
          zoomeye_queries: [],
          selected_poc: ''
        },
        configEdit: {
          ipSeg: {
            start: '127.0.0.1',
            end: '127.0.0.2',
            port: '80'
          },
          zoomQuery: 'axis'
        },
        validateConfigEdit: {
          ipSeg: [
            {validator: validateAddIp, trigger: 'blur'}
          ],
          zoomQuery: [
            {validator: validateAddZoom, trigger: 'blur'}
          ]
        }
      }
    },
    watch: {
      '$store.state.isConnected': {
        handler (isConnected) {
          if (isConnected) {
            axios.get(`${this.$store.state.host}/poc`).then((res) => {
              this.pocs = res.data.pocs
            })
            axios.get(`${this.$store.state.host}/config?fields=ip_ranges,zoomeye_queries,selected_poc`).then((res) => {
              this.config = res.data
            })
          }
        }
      }
    },
    methods: {
      open () {
        this.visible = true
      },
      submitForm () {
        axios.post(`${this.$store.state.host}/config`, this.config).then(
          this.$message.success('配置成功!'),
          this.visible = false
        ).catch(() => {
          this.$message.error('配置失败！')
        })
      },
      resetForm () {
        this.$refs['configEdit'].resetFields()
      },
      addIpSeg () {
        let valid = true
        this.$refs['configEdit'].validateField('ipSeg', () => {
          valid = false
        })
        console.log(this.configEdit.ipSeg)
        if (valid) {
          this.configEdit.ipSeg.start = (this.configEdit.ipSeg.start || this.configEdit.ipSeg.end)
          this.configEdit.ipSeg.end = (this.configEdit.ipSeg.end || this.configEdit.ipSeg.start)
          this.config.ip_ranges.push({
            start: this.configEdit.ipSeg.start.split('.').map((val) => { return val || 0 }).join('.'),
            end: this.configEdit.ipSeg.end.split('.').map((val) => { return val || 0 }).join('.'),
            port: parseInt(this.configEdit.ipSeg.port)
          })
          this.configEdit.ipSeg.start = '...'
          this.configEdit.ipSeg.end = '...'
          this.configEdit.ipSeg.port = ''
        }
      },
      addZoomQuery () {
        let valid = true
        this.$refs['configEdit'].validateField('zoomQuery', function (pa) {
          valid = false
        })
        if (valid) {
          this.config.zoomeye_queries.push(this.configEdit.zoomQuery)
          this.configEdit.zoomQuery = ''
        }
      },
      removeItem (l, index) {
        if (index !== -1 && this.config.zoomeye_queries.length + this.config.ip_ranges.length > 1) {
          l.splice(index, 1)
        }
      },
      changeIp (mark) {
        return (value) => {
          this.configEdit.ipSeg[mark] = value
        }
      }
    }
  }
</script>
