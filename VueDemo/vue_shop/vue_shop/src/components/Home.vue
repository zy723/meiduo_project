<template>
  <el-container class="home-container">
    <!--    头部区域-->
    <el-header>
      <div>
        <img src="../assets/heima.png" alt="">
        <span>后台管理系统</span>
      </div>
      <el-button type="info" @click="logout">退出</el-button>
    </el-header>
    <!--  页面主体区域  -->
    <el-container>
      <!--   侧边栏   -->
      <el-aside :width="isCollapsed ? '64px':'200px'">
        <!--  放置折叠按钮      -->
        <div class="toggle-button" @click="toggleCollapse">|||</div>
        <!--     侧边栏导航区域   -->
        <el-menu
          background-color="#333744"
          text-color="#fff"
          active-text-color="#409EFF" unique-opened :collapse="isCollapsed" :collapse-transition="false" :router="true"
          :default-active="activePath">
          <!--   unique-opened 是否只保持一个子菜单的展开       -->
          <!--   collapse-transition 是否开启折叠动画       -->
          <!--   default-active 当前激活菜单的 index       -->
          <!--      一级菜单    -->
          <el-submenu :index="item.id + ''" v-for="item in menulist" :key="item.id">
            <!--   一级菜单模板区域         -->
            <template slot="title">
              <!--    图标          -->
              <i :class="iconsObj[item.id]"></i>
              <!--    文本          -->
              <span>{{ item.authName}}</span>
            </template>
            <!--   二级菜单         -->
            <el-menu-item :index="'/' + subItem.path" v-for="subItem in item.children" :key="subItem.id"
                          @click="saveNavState('/' + subItem.path)">
              <template slot="title">
                <!--    图标          -->
                <i class="el-icon-menu"></i>
                <!--    文本          -->
                <span>{{ subItem.authName}}</span>
              </template>
            </el-menu-item>
          </el-submenu>
        </el-menu>

      </el-aside>
      <!--   右侧内容主体   -->
      <el-main>
        <!--   路由占位符     -->
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>

</template>

<script>
  export default {
    name: "Home",
    created() {
      this.getMenuList();
      this.activePath = window.sessionStorage.getItem('activePath');
    },

    data() {
      return {
        // 左侧菜单
        menulist: [],
        // 一级图标
        iconsObj: {
          '125': 'iconfont icon-user',
          '103': 'iconfont icon-tijikongjian',
          '101': 'iconfont icon-shangpin',
          '102': 'iconfont icon-danju',
          '145': 'iconfont icon-baobiao'
        },
        // 是否被折叠
        isCollapsed: false,
        // 当前被激活的菜单项
        activePath: '',
      }
    },
    methods: {
      // 退出登陆
      logout() {
        window.sessionStorage.clear();
        this.$router.push('/login');
      },
      // 左侧菜单权限
      async getMenuList() {
        let {data: res} = await this.$http.get('menus');
        console.log(res);
        if (res.meta.status !== 200) return this.$message.error(res.meta.msg);
        this.menulist = res.data;
      },
      // 点击按钮，切换菜单的折叠与展开
      toggleCollapse() {
        this.isCollapsed = !this.isCollapsed;
      },
      // 保存当前被展开的激活状态
      saveNavState(activePath) {
        window.sessionStorage.setItem('activePath', activePath);
        this.activePath = activePath;
      },
    }
  }
</script>

<style scoped>
  .home-container {
    height: 100%;
  }

  .el-header {
    background-color: #373d41;
    display: flex;
    justify-content: space-between;
    padding-left: 0;
    align-items: center;
    color: #fff;
    font-size: 20px;
  }

  .el-header div {
    display: flex;
    align-items: center;
  }

  .el-header div span {
    margin-left: 15px;
  }


  .el-aside {
    background-color: #333744;
  }

  .el-aside .el-menu {
    border-right: none;
  }

  .el-main {
    background-color: #EAEDF1;
  }

  .iconfont {
    margin-right: 10px;
  }

  .toggle-button {
    background-color: #4A5064;
    font-size: 10px;
    line-height: 24px;
    color: #fff;
    text-align: center;
    letter-spacing: 0.2em;
    cursor: pointer;
  }
</style>
