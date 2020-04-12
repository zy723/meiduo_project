let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        f1_tab: 1,  // 1F 标签页控制
        f2_tab: 1,  // 2F 标签页控制
        f3_tab: 1,  // 3F 标签页控制
    },
    methods: {},
});