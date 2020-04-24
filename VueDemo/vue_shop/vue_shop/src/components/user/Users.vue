<template>
  <div>
    <!-- 面包屑导航   -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>用户管理</el-breadcrumb-item>
      <el-breadcrumb-item>用户列表</el-breadcrumb-item>
    </el-breadcrumb>

    <!--  卡片区域    -->
    <el-card class="box-card">
      <!-- 搜索与添加区域 -->
      <el-row :gutter="20">
        <el-col :span="8">
          <!--  搜索栏        -->
          <el-input placeholder="请输入内容" v-model="queryInfo.query" clearable @clear="getUserList">
            <el-button slot="append" icon="el-icon-search" @click="getUserList"></el-button>
          </el-input>
        </el-col>
        <!--  添加用户按钮      -->
        <el-col :span="4">
          <el-button type="primary" @click="addDialogVisible = true">添加用户</el-button>
        </el-col>
      </el-row>
      <!-- 用户列表区域 -->
      <el-table
        style="width: 100%" :data="userlist" border stripe>
        <!--   border  是否带有纵向边框   -->
        <!--   stripe 是否为斑马纹 table    -->
        <el-table-column type="index"></el-table-column>
        <el-table-column prop="username" label="姓名"></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
        <el-table-column prop="mobile" label="电话"></el-table-column>
        <el-table-column prop="role_name" label="角色"></el-table-column>
        <el-table-column label="状态">
          <!--  状态开关        -->
          <template v-slot="switchState">
            <el-switch v-model="switchState.row.mg_state" @change="userStateChanged(switchState.row)"></el-switch>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180px">
          <!--  修改状态区域      -->
          <template v-slot="scopeChange">
            <!--   修改按钮         -->
            <el-button type="primary" icon="el-icon-edit" size="mini"
                       @click="showEditDialog(scopeChange.row.id)"></el-button>
            <!--  删除按钮          -->
            <el-button type="danger" icon="el-icon-delete" size="mini"></el-button>
            <!--   分配角色         -->
            <el-button type="warning" icon="el-icon-setting" size="mini"></el-button>
          </template>
        </el-table-column>
      </el-table>

    </el-card>

    <!--  添加用户对话框    -->
    <el-dialog
      title="添加用户" :visible.sync="addDialogVisible" width="50%" @close="addDialogClosed">
      <el-form :model="addForm" status-icon :rules="addFormRules" ref="addFormRef" label-width="70px">
        <!--  表单主体内容      -->
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="addForm.password"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model.number="addForm.email"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model.number="addForm.mobile"></el-input>
        </el-form-item>
        <!-- 提交重置按钮       -->
        <el-form-item>
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addUser">确定</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <!--  修改用户对话框    -->
    <!--  分配角色    -->
  </div>
</template>

<script>
  export default {
    name: "Users",
    data() {
      return {
        // 获取用户列表参数对象
        queryInfo: {
          query: '', // 查询参数
          pagenum: 1,  // 当前页码
          pagesize: 2, // 每页显示条数
        },
        // 用户数据列表
        userlist: [],
        // 总的数据条数
        total: 0,
        // 控制修改用户对话框的显示与隐藏
        editDialogVisible: false,
        // 查询到的用户信息对象
        editForm: {},

        // 添加表单对话框显示与关闭
        addDialogVisible: false,
        // 提交修改表单数据
        addForm: {
          username: '',
          password: '',
          email: '',
          mobile: '',
        },
        // 添加表单的验证规则对象
        addFormRules: {
          username: [{required: true, message: '请输入用户名', trigger: 'blur'},
            {min: 3, max: 10, message: '长度在3到10个字符', trigger: 'blur'}],
          password: [{required: true, message: '请输入密码', trigger: 'blur'},
            {min: 6, max: 15, message: '长度在6到15个字符', trigger: 'blur'}],
          email: [{required: true, message: '请输入邮箱', trigger: 'blur'}],
          mobile: [{required: true, message: '请输入手机号', trigger: 'blur'}],
        }

      }

    },
    created() {
      this.getUserList();
    },
    methods: {
      async getUserList() {
        const {data: res} = await this.$http.get('users', {params: this.queryInfo});
        console.log(res);
        if (res.meta.status !== 200) return this.$message.error('获取用户列表失败');
        this.userlist = res.data.users;
        this.total = res.data.total;

      },
      async userStateChanged(userinfo) {
        console.log(userinfo);
        const {data: res} = await this.$http.put(`users/${userinfo.id}/state/${userinfo.mg_state}`);
        if (res.meta.status !== 200) {
          userinfo.mg_state = !userinfo.mg_state;
          return this.$message.error('更新状态失败！');
        }
        this.$message.success('更新用户状态成功！')

      },
      // 展示编辑对话框
      async showEditDialog(id) {
        // 查询用户信息
        console.log(id);
        const {data: res} = await this.$http.get('users/' + id);
        if (res.meta.status !== 200) return this.$message.error('未查询到用户信息');
        this.editForm = res.data;
        this.editDialogVisible = true;
      },
      // 添加用户对话框关闭事件
      addDialogClosed() {
        // 校验提交信息

        this.$refs.addFormRef.resetFields();
      },
      // 添加用户信息表单提交
      addUser() {
        this.$refs.addFormRef.validate(async valid => {
          if (!valid) return;
          const {data: res} = await this.$http.post('users', this.addForm);
          if (res.meta.status !== 201) return this.$message.error(res.meta.msg);
          this.$message.success(res.meta.msg);
          // 隐藏添加用户对话框
          this.addDialogVisible = false;
          // 刷新列表
          this.getUserList();

        });

      }

    }
  }
</script>

<style scoped>

</style>
