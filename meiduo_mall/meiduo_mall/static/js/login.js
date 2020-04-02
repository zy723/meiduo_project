let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: '',
        password: '',

        error_username: false,
        error_password: false,
        remembered: false,
        error_pwd: true,
    },
    methods: {
        // 检查账号
        check_username() {
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            this.error_pwd = false;
            if (re.test(this.username)) {
                this.error_username = false;
            } else {
                this.error_username = true;
            }
        },
        // 检查密码
        check_password() {
            let re = /^[a-zA-Z0-9]{8,20}$/
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // 提交表单
        on_submit() {
            // 检查账号与密码
            this.check_username();
            this.check_password();
            if (this.error_username == true || this.error_password == true) {
                window.event.returnValue = false;
            }

        },

        // qq 登录
        qq_login() {
            let next = get_query_string('next') || '/';
            let url = '/qq/login/?next=' + next;

            axios.get(url, {responseType: 'json'})
                .then(response => {
                    if (response.data.code == '0') {
                        location.href = response.data.login_url;
                    }
                })
                .catch(error => {
                    console.log(error.response)
                });
        },

    }


});