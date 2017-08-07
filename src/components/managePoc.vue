<template>
	<section>
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<!--<el-form-item>-->
					<!--<el-input v-model="filters.name" placeholder="姓名"></el-input>-->
				<!--</el-form-item>-->
				<!--<el-form-item>-->
					<!--<el-button type="primary" v-on:click="getUsers">查询</el-button>-->
				<!--</el-form-item>-->
				<el-form-item>
					<el-button type="primary" @click="addFormVisible = true">新增</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="users" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" :span="2">
			</el-table-column>
			<el-table-column type="index" :span="3">
			</el-table-column>
			<el-table-column prop="name" label="脚本名称" :span="3" sortable>
			</el-table-column>
			<el-table-column prop="device_type" label="设备类型" :span="3" sortable>
			</el-table-column>
      <el-table-column prop="zoomeye_query" label="ZoomEye查询字符串" :span="3">
      </el-table-column>
			<el-table-column label="操作" :span="3">
				<template scope="scope">
					<el-button size="small" @click="handleEdit(scope.$name, scope.row)">编辑</el-button>
					<el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<!--<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>-->
			<el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :total="total" style="float:right;">
			</el-pagination>
		</el-col>

		<!--编辑界面-->
		<el-dialog title="编辑" ref="editForm" v-model="editFormVisible" :close-on-click-modal="false">
			<el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm">
				<el-form-item label="脚本名称" prop="name" :disabled="true">
					<el-input v-model="editForm.name" auto-complete="off"></el-input>
				</el-form-item>
        <el-form-item label="设备类型" prop="device_type">
          <el-input v-model="editForm.device_type" auto-complete="off" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="ZoomEye查询字符串" prop="zoomeye_query">
          <el-input v-model="editForm.zoomeye_query" auto-complete="off" :disabled="true"></el-input>
        </el-form-item>
				<el-form-item label="Poc内容" prop="content">
					<el-input type="textarea" v-model="editForm.content" autosize></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="editFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
			</div>
		</el-dialog>

		<!--新增界面-->
		<el-dialog title="新增" ref="addForm" v-model="addFormVisible" :close-on-click-modal="false">
			<el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
        <el-form-item label="脚本名称" prop="name">
          <el-input  v-model="addForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="设备类型" prop="device_type">
          <el-input  v-model="addForm.device_type" auto-complete="off" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="ZoomEye查询字符串" prop="zoomeye_query" :disabled="true">
          <el-input v-model="addForm.zoomeye_query" auto-complete="off" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="Poc内容" prop="content">
          <el-input v-model="addForm.content" type="textarea" placeholder="请勿输入中文" autosize></el-input>
        </el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="addFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
			</div>
		</el-dialog>
	</section>
</template>

<script>
  import axios from 'axios'

  export default {
    data () {
      return {
        filters: {
          name: ''
        },
        users: [],
        total: 0,
        page: 1,
        listLoading: false,
        sels: [],  // 列表选中列

        editFormVisible: false, // 编辑界面是否显示
        editLoading: false,
        editFormRules: {
          name: [
            { required: true, message: '请输入脚本名称', trigger: 'blur' }
          ]
        },
        // 编辑界面数据
        editForm: {
          id: 0,
          name: '',
          device_type: '',
          zoomeye_query: '',
          content: ''
        },

        addFormVisible: false,  // 新增界面是否显示
        addLoading: false,
        addFormRules: {
          name: [
            { required: true, message: '请输入脚本名称', trigger: 'blur' }
          ]
        },
        // 新增界面数据
        addForm: {
          id: 0,
          name: '',
          device_type: '',
          zoomeye_query: '',
          content: ''
        }
      }
    },
    methods: {
      handleCurrentChange (val) {
        this.page = val
        this.getUsers()
      },
      getUsers () {
        let para = {
          page: this.page,
          name: this.filters.name
        }
        this.listLoading = true
        axios.get(`${this.$store.state.host}/poc`, { params: para }).then((res) => {
          this.total = res.data.total
          this.users = res.data.pocs
          this.listLoading = false
          console.log(this.users)
        }).catch(() => {
          this.$message.error('获取Poc内容失败！')
          this.listLoading = false
        })
      },
      handleDel (index, row) {
        this.$confirm('确认删除该Poc吗?', '提示', {
          type: 'warning'
        }).then(() => {
          this.listLoading = true
          axios.delete(`${this.$store.state.host}/poc/${row.name}`).then((res) => {
            this.listLoading = false
            this.$message.success('删除成功')
            this.getUsers()
          })
        }).catch((err) => {
          if (err.response.status === 404 && err.response.statusText === 'Poc File Not Found') {
            this.$message.error('删除失败，未找到Poc文件！')
          } else {
            this.$message.error('删除失败！')
          }
        })
      },
      // 显示编辑界面
      handleEdit: function (index, row) {
        this.editFormVisible = true
        this.editForm = Object.assign({}, row)
      },
      // 编辑
      editSubmit: function () {
        this.$refs.editForm.validate((valid) => {
          if (valid) {
            this.$confirm('确认提交吗？', '提示', {}).then(() => {
              this.editLoading = true
              axios.put(`${this.$store.state.host}/poc/${this.editForm.name}`, this.editForm.content).then((res) => {
                this.editLoading = false
                this.$message.success('提交成功')
                this.$refs['editForm'].resetFields()
                this.editFormVisible = false
                this.getUsers()
              }).catch((err) => {
                if (err.response.status === 404 && err.response.statusText === 'Poc File Not Found') {
                  this.$message.error('修改失败，Poc文件不存在！')
                } else {
                  this.$message.error('修改失败！')
                }
              })
            })
          }
        })
      },
      // 新增
      addSubmit: function () {
        this.$refs.addForm.validate((valid) => {
          if (valid) {
            this.$confirm('确认提交吗？', '提示', {}).then(() => {
              axios.post(`${this.$store.state.host}/poc/${this.addForm.name}`, this.addForm.content).then((res) => {
                this.addLoading = false
                this.$message.success('提交成功')
                this.$refs['addForm'].resetFields()
                this.addFormVisible = false
                this.getUsers()
              }).catch((err) => {
                if (err.response.status === 409 && err.response.statusText === 'Conflict') {
                  this.addLoading = false
                  this.$message.error('Poc已存在，不允许重名')
                  this.$refs['addForm'].resetFields()
                  this.addFormVisible = false
                  this.getUsers()
                } else {
                  this.$message.error('新增Poc文件失败！')
                }
              })
            })
          }
        })
      },
      selsChange: function (sels) {
        this.sels = sels
      }
      // 批量删除
//      batchRemove: function () {
//        let ids = this.sels.map(item => item.id).toString()
//        this.$confirm('确认删除选中记录吗？', '提示', {
//          type: 'warning'
//        }).then(() => {
//          this.listLoading = true
//          // NProgress.start();
//          let para = { ids: ids }
//          batchRemoveUser(para).then((res) => {
//            this.listLoading = false
//            // NProgress.done();
//            this.$message({
//              message: '删除成功',
//              type: 'success'
//            })
//            this.getUsers()
//          })
//        }).catch(() => {
//        })
//      }
    },
    mounted () {
      this.getUsers()
    }
  }

</script>

<style scoped>

</style>
