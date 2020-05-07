<template>
  <div>
    <!-- 面包屑导航   -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>权限管理</el-breadcrumb-item>
      <el-breadcrumb-item>角色列表</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 卡片区域   -->
    <el-card>
      <!-- 添加角色按钮-->
      <el-row>
        <el-col>
          <el-button type="primary" size="mini">添加角色</el-button>
        </el-col>
      </el-row>

      <!-- 角色管理      -->
      <el-table :data="rolesList" :border="true" :stripe="true" row-key="id">
        <!--  展开列      -->
        <el-table-column type="expand">

        </el-table-column>
        <!--  索引列      -->
        <el-table-column type="index"></el-table-column>
        <el-table-column label="角色名称" prop="roleName"></el-table-column>
        <el-table-column label="角色描述" prop="roleDesc"></el-table-column>
        <el-table-column label="操作" width="300px">

        </el-table-column>

      </el-table>


    </el-card>

  </div>
</template>

<script>
  export default {
    name: "Roles",
    data() {
      return {
        // 所有角色列表
        rolesList: [],
      }
    },
    created() {
      this.getRolesList();
    },
    methods: {
      async getRolesList() {
        // 获取用户列表
        const {data: res} = await this.$http.get('roles');
        if (res.meta.status !== 200) return this.$message.error('获取角色失败')
        this.rolesList = res.data;
        console.log(this.rolesList);

      },

    }
  }
</script>

<style scoped>

</style>
