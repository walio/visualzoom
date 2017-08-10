<template>
  <el-col>
    <el-button @click="styleJsonVisible=true" type="primary" style="margin-top: 4%;">修改地图颜色</el-button><br/>
    <el-button @click="translateVisible=true" type="primary" style="margin-top: 4%;">修改翻译</el-button><br/>
    <el-button @click="deviceColorVisible=true" type="primary" style="margin-top: 4%;">修改设备颜色显示</el-button>
    <el-dialog :visible.sync="styleJsonVisible" title="百度地图配色设置">
      <p>颜色选项详见<a href="http://lbsyun.baidu.com/index.php?title=jspopular/guide/custom" target="_blank">http://lbsyun.baidu.com/index.php?title=jspopular/guide/custom</a></p>
      <el-form :rules="styleRules" :model="styleJson">
        <el-form-item prop="styleJson">
          <el-input type="textarea" placeholder="配色模板" v-model="styleJson.styleJson" autosize></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="confirm('styleJson')" :disabled="styleJson.disabled">确认</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <el-dialog :visible.sync="translateVisible" title="翻译设置">
      <el-form :rules="translateRules" :model="translate">
        <el-form-item prop="translate">
          <el-input type="textarea" placeholder="翻译设置" v-model="translate.translate" autosize></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="confirm('translate')" :disabled="translate.disabled">确认</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <el-dialog :visible.sync="deviceColorVisible" title="设备颜色设置">
      <p></p>
      <el-form :rules="deviceColorRules" :model="deviceColor">
        <el-form-item prop="deviceColor">
          <el-input type="textarea" placeholder="设备颜色设置" v-model="deviceColor.deviceColor" autosize></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="confirm('deviceColor')" :disabled="deviceColor.disabled">确认</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </el-col>

</template>
<script>
  import axios from 'axios'
  export default {
    data () {
      let checkJson = (rule, value, callback) => {
        try {
          JSON.parse(value.replace(/'/g, '"'))
          this[rule.field].disabled = false
          callback()
        } catch (err) {
          this[rule.field].disabled = true
          return callback(new Error('数据格式错误'))
        }
      }
      return {
        styleJsonVisible: false,
        styleJson: {
          styleJson: '',
          disabled: true
        },
        styleRules: {
          styleJson: [
            { validator: checkJson, trigger: 'change' },
            { validator: checkJson, trigger: 'blur' }
          ]
        },

        translateVisible: false,
        translate: {
          translate: '',
          disabled: true
        },
        translateRules: {
          translate: [
            { validator: checkJson, trigger: 'change' },
            { validator: checkJson, trigger: 'blur' }
          ]
        },
        deviceColorVisible: false,
        deviceColor: {
          deviceColor: '',
          disabled: true
        },
        deviceColorRules: {
          deviceColor: [
            { validator: checkJson, trigger: 'change' },
            { validator: checkJson, trigger: 'blur' }
          ]
        }
      }
    },
    mounted () {
      axios.get(`${this.$store.state.host}/style?fields=styleJson,translate,deviceColor`).then((res) => {
        this.styleJson.styleJson = JSON.stringify(res.data.styleJson, null, 2) || ''
        this.translate.translate = JSON.stringify(res.data.translate, null, 2) || ''
        this.deviceColor.deviceColor = JSON.stringify(res.data.deviceColor, null, 2) || ''
      })
    },
    methods: {
      confirm (item) {
        let _ = {}
        _[item] = JSON.parse(this[item][item].replace(/'/g, '"'))
        axios.post(`${this.$store.state.host}/style`, _).then(() => {
          this.$message.success('配置成功！')
          this[item + 'Visible'] = false
        }).catch(() => {
          this.$message.error('配置失败！')
        })
      }
    }
  }
</script>
