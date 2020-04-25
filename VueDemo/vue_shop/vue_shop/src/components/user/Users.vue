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
            <el-button type="danger" icon="el-icon-delete" size="mini"
                       @click="removeUserById(scopeChange.row.id)"></el-button>
            <!--   分配角色         -->
            <el-button type="warning" icon="el-icon-setting" size="mini"
                       @click="setRole(scopeChange.row)"></el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 分页区域     -->
      <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
                     :current-page="queryInfo.pagenum"
                     :page-sizes="[1, 2, 5, 10]" :page-size="queryInfo.pagesize"
                     layout="total, sizes, prev, pager, next, jumper" :total="total">
      </el-pagination>

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
      </el-form>
      <!-- 提交重置按钮       -->
      <span slot="footer" class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addUser">确定</el-button>
      </span>
    </el-dialog>

    <!--  修改用户对话框    -->
    <el-dialog title="修改用户" :visible.sync="editDialogVisible" width="50%" @close="editDialogClosed">
      <el-form :model="editForm" status-icon :rules="editFormRules" ref="editFormRef" label-width="70px">
        <!--  表单主体内容      -->
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" :disabled="true"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model.number="editForm.email"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model.number="editForm.mobile"></el-input>
        </el-form-item>
      </el-form>
      <!--  提交数据    -->
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveRoleInfo">确 定</el-button>
      </span>
    </el-dialog>


    <!--  分配角色    -->
    <el-dialog title="分配角色" :visible.sync="setDialogVisible" width="50%" @close="setRoleDialogClosed">
      <div>
        <p>当前的用户:{{ userInfo.username }}</p>
        <p>当前的角色:{{ userInfo.role_name }}</p>
        <p>
          分配新的角色:
          <el-select v-model="selectedRoleId" placeholder="请选择">
            <el-option v-for="item in rolesList" :key="item.value" :label="item.roleName" :value="item.id">
            </el-option>
          </el-select>
        </p>
      </div>
      <!--  提交数据    -->
      <span slot="footer" class="dialog-footer">
        <el-button @click="setDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveRoleInfo">确 定</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>
  export default {
    name: "Users",
    data() {
      // 验证邮箱的正则表达式
      var checkEmail = (rule, value, cb) => {
        const regEmail = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-])+/;
        if (regEmail.test(value)) {
          return cb();
        }
        cb(new Error('请输入合法的邮箱'));
      };
      // 验证手机号的规则
      var cheackMobile = (rule, value, cb) => {
        const regMobile = /^(0|86|17951)?(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$/;
        if (regMobile.test(value)) {
          return cb()
        }
        return cb(new Error('请输入合法的手机号'))
      };


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


        // 添加表单对话框显示与关闭
        addDialogVisible: false,
        // 提交添加表单数据
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
          email: [{required: true, message: '请输入邮箱', trigger: 'blur'},
            {validator: checkEmail, trigger: 'blur'}],
          mobile: [{required: true, message: '请输入手机号', trigger: 'blur'},
            {validator: cheackMobile, trigger: 'blur'}],
        },
        // 控制修改用户对话框的显示与隐藏
        editDialogVisible: false,
        // 查询到的修改用户信息对象
        editForm: {},
        // 修改表单数据校验
        editFormRules: {
          email: [{required: true, message: '请输入邮箱', trigger: 'blur'},
            {validator: checkEmail, trigger: 'blur'}],
          mobile: [{required: true, message: '请输入手机号', trigger: 'blur'},
            {validator: cheackMobile, trigger: 'blur'}],
        },

        // 控制分配角色对话框显示与隐藏
        setDialogVisible: false,
        // 需要分配角色对话框的显示与隐藏
        userInfo: {},
        // 所有角色的数据表
        rolesList: [],
        // 已选中的角色Id值
        selectedRoleId: '',

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

      // 监听到pagesize发生变化
      handleSizeChange(newSize) {
        this.queryInfo.pagesize = newSize;
        this.getUserList();
      },
      // 监听到页码页数变化时
      handleCurrentChange(newPage) {
        this.queryInfo.pagenum = newPage;
        this.getUserList();
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
      },

      // 修改展示对话框
      async showEditDialog(id) {
        // 查询用户信息
        // console.log(id);
        const {data: res} = await this.$http.get('users/' + id);
        if (res.meta.status !== 200) return this.$message.error('未查询到用户信息');
        this.editForm = res.data;
        this.editDialogVisible = true;
      },
      // 修改对话框关闭时清空表单数据
      editDialogClosed() {
        this.$refs.editFormRef.resetFields();
      },
      // 修改表单提交
      editUserInfo() {
        this.$refs.editFormRef.validate(async validate => {
          if (!validate) return;
          // 校验成功发起修改请求
          const {data: res} = await this.$http.put('users/' + this.editForm.id, this.editForm);
          if (res.meta.status !== 200) return this.$message.error(res.meta.msg);
          this.editDialogVisible = false;
          // 刷新数据
          this.getUserList();
          this.$message.success(res.meta.msg);
        });
      },
      // 删除用户
      async removeUserById(id) {
        const confirmResult = await this.$confirm('此操作将永久删除该用户, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).catch(err => err);
        if (confirmResult !== 'confirm') {
          return this.$message.info('已取消删除')
        }
        const {data: res} = await this.$http.delete('users/' + id);
        if (res.meta.status !== 200) return this.$message.error('删除失败');
        this.$message.success('删除成功');
        this.getUserList();

      },
      // 设置角色对话框开启
      async setRole(userInfo) {
        this.userInfo = userInfo;
        // 获取所有角色列表
        const {data: res} = await this.$http.get('roles');
        if (res.meta.status !== 200) return this.$message.error('获取角色列表失败');
        this.rolesList = res.data;
        this.setDialogVisible = true;
      },
      // 设置角色关闭对话框
      setRoleDialogClosed() {
        this.selectedRoleId = '';
        this.userInfo = {};
      },
      // 保存角色信息
      async saveRoleInfo() {
        if (!this.selectedRoleId) return this.$message.error('请选择要分配的角色');
        const {data: res} = await this.$http.put(`users/${this.userInfo.id}/role`, {rid: this.selectedRoleId});
        if (res.meta.status !== 200) return this.$message.error('更新角色失败');
        this.$message.success('更新角色成功');
        this.getUserList();
        this.setDialogVisible = false;
      }


    }
  }
</script>

<style scoped>

</style>
