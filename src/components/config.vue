<template>
<el-dialog title='配置选项' :visible.sync="visible">
  <el-col :span="22" :offset="1" style="margin-top: 3%;margin-bottom: 3%;">
    <el-form :model="config" label-width="86.7%" id="config">
      <el-form-item
        v-for="(ipSeg, index) in config.ipList"
        :label="ipSeg.start + ' - ' + ipSeg.end"
      >
        <el-col :span="24" style="float: right;"><el-button @click.prevent="removeItem(config.ipList, index)">删除</el-button></el-col>
      </el-form-item>
      <el-form-item
        v-for="(query, index) in config.zoomQueries"
        :label="'ZoomEye查询字串: ' + query"
      >
        <el-col :span="24" style="float: right;"><el-button @click.prevent="removeItem(config.zoomQueries, index)">删除</el-button></el-col>
      </el-form-item>
    </el-form>
    <el-form :model="configEdit" :rules="validateConfigEdit" ref="configEdit" label-width="20%">
      <el-form-item
        label="ip地址："
        prop="ipSeg"
      >
        <el-col :span="7" :offset="2"><el-input v-model="configEdit.ipSeg.start"></el-input></el-col>
        <el-col :span="2">-</el-col>
        <el-col :span="7"><el-input v-model="configEdit.ipSeg.end"></el-input></el-col>
        <el-col :span="4" :offset="2"><el-button @click.prevent="addIpSeg()">增加</el-button></el-col>
      </el-form-item>
      <el-form-item
        label="ZoomEye查询字串："
        prop="zoomQuery"
      >
        <el-col :span="16" :offset="2"><el-input v-model="configEdit.zoomQuery"></el-input></el-col>
        <el-col :span="4" :offset="2"><el-button @click.prevent="addZoomQuery()">增加</el-button></el-col>
      </el-form-item>
      <el-form-item label="poc名称：">
        <el-col :span="16" :offset="2">
          <el-select style="width:100%;" v-model="config.selectedPoc" placeholder="请选择Poc内容">
            <el-option
              v-for="poc in pocs"
              :label="poc.name"
              :value="poc.name">
              <span style="float: left">{{ poc.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ poc.devtype }}</span>
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
        if (!value.start || !value.end) {
          callback(new Error('ip不能为空'))
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
          ipList: [],
          zoomQueries: [],
          selectedPoc: ''
        },
        configEdit: {
          ipSeg: {
            start: '',
            end: ''
          },
          zoomQuery: ''
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
            axios.get(`${this.$store.state.host}/config?fields=ipList,zoomQueries,selectedPoc`).then((res) => {
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
        axios.put(`${this.$store.state.host}/config`, this.config).then(
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
        if (valid) {
          this.config.ipList.push({
            start: this.configEdit.ipSeg.start,
            end: this.configEdit.ipSeg.end
          })
          this.configEdit.ipSeg.start = ''
          this.configEdit.ipSeg.end = ''
        }
      },
      addZoomQuery () {
        let valid = true
        console.log('watch')
        console.log(this)
        console.log(this.config)
        this.$refs['configEdit'].validateField('zoomQuery', function (pa) {
          valid = false
        })
        if (valid) {
          this.config.zoomQueries.push(this.configEdit.zoomQuery)
          this.configEdit.zoomQuery = ''
        }
      },
      removeItem (l, index) {
        if (index !== -1 && this.config.zoomQueries.length + this.config.ipList.length > 1) {
          l.splice(index, 1)
        }
      }
    }
  }
</script>
