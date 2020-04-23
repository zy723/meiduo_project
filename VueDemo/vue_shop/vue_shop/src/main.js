import Vue from 'vue'
import App from './App.vue'
import router from './router'
import './plugins/element.js'
// 导入字体图标
import './assets/fonts/iconfont.css'
// 导入全局样式
import './assets/css/global.css'
import axios from 'axios'

axios.defaults.baseURL = 'https://www.liulongbin.top:8888/api/private/v1/';

Vue.config.productionTip = false;
// 注册全局http
Vue.prototype.$http = axios;



new Vue({
  router,
  render: h => h(App)
}).$mount('#app');
