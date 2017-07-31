<template>
	<section>
		<!--&lt;!&ndash;工具条&ndash;&gt;-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.name" placeholder="姓名"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getUsers">查询</el-button>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleAdd">新增</el-button>
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
			<el-table-column prop="devtype" label="设备类型" :span="3" sortable>
			</el-table-column>
      <el-table-column prop="zoomQuery" label="ZoomEye查询字符串" :span="3">
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
		<el-dialog title="编辑" v-model="editFormVisible" :close-on-click-modal="false">
			<el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm">
				<el-form-item label="脚本名称" prop="name">
					<el-input v-model="editForm.name" auto-complete="off"></el-input>
				</el-form-item>
        <el-form-item label="设备类型" prop="devtype">
          <el-input v-model="editForm.devtype" auto-complete="off" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="ZoomEye查询字符串" prop="zoomQuery">
          <el-input v-model="editForm.zoomQuery" auto-complete="off" :disabled="true"></el-input>
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
		<el-dialog title="新增" v-model="addFormVisible" :close-on-click-modal="false">
			<el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
        <el-form-item label="脚本名称" prop="name">
          <el-input  v-model="addForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="设备类型" prop="devtype">
          <el-input  v-model="addForm.devtype" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="ZoomEye查询字符串" prop="zoomQuery">
          <el-input v-model="addForm.zoomQuery" auto-complete="off"></el-input>
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

  let base = 'http://localhost'

  const getPocListPage = params => { return axios.get(`${base}/list`, { params: params }) }

  const removeUser = params => { return axios.delete(`${base}/poc/${params}`) }

//  const batchRemoveUser = params => { return axios.get(`${base}/user/batchremove`, { params: params }) }

  const editUser = (name, params) => { return axios.put(`${base}/poc/${name}`, params) }

  const addUser = (name, params) => { return axios.post(`${base}/poc/${name}`, params) }
  // import NProgress from 'nprogress'

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
          devtype: '',
          zoomQuery: '',
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
          devtype: '',
          zoomQuery: '',
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
        getPocListPage(para).then((res) => {
          this.total = res.data.total
          this.users = res.data.pocs
          this.listLoading = false
        }).catch((err) => {
          console.log(err)
          this.$message.error('获取Poc内容失败！')
          this.listLoading = false
        })
      },
      handleDel: function (index, row) {
        this.$confirm('确认删除该记录吗?', '提示', {
          type: 'warning'
        }).then(() => {
          this.listLoading = true
          removeUser(row.name).then((res) => {
            this.listLoading = false
            this.$message.success('删除成功')
            this.getUsers()
          })
        }).catch(() => {
        })
      },
      // 显示编辑界面
      handleEdit: function (index, row) {
        this.editFormVisible = true
        this.editForm = Object.assign({}, row)
      },
      // 显示新增界面
      handleAdd: function () {
        this.addFormVisible = true
      },
      // 编辑
      editSubmit: function () {
        this.$refs.editForm.validate((valid) => {
          if (valid) {
            this.$confirm('确认提交吗？', '提示', {}).then(() => {
              this.editLoading = true
              let para = Object.assign({}, this.editForm)
              editUser(para.name, para).then((res) => {
                this.editLoading = false
                this.$message({
                  message: '提交成功',
                  type: 'success'
                })
                this.$refs['editForm'].resetFields()
                this.editFormVisible = false
                this.getUsers()
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
              // NProgress.start();
              let para = Object.assign({}, this.addForm)
              addUser(para.name, para).then((resp) => {
                this.addLoading = false
                // NProgress.done();
                this.$message({
                  message: '提交成功',
                  type: 'success'
                })
                this.$refs['addForm'].resetFields()
                this.addFormVisible = false
                this.getUsers()
              }).catch((err) => {
                console.log(err.response)
                if (err.response.status === 409 && err.response.statusText === 'Conflict') {
                  console.log(123)
                  this.addLoading = false
                  // NProgress.done();
                  this.$message({
                    message: 'Poc已存在，不允许重名',
                    type: 'error'
                  })
                  this.$refs['addForm'].resetFields()
                  this.addFormVisible = false
                  this.getUsers()
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
