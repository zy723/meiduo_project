// 创建Vue对象 vm
let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        // v-model
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        image_code_url: '', // 图片地址
        // v-show
        error_username: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        // error_message
        error_name_message: '',
        error_mobile_message: ''
    },
    mounted() {
        this.generate_image_code();
    },
    methods: {
        // 方法对象
        // 生成图片验证码
        generate_image_code() {
            // 从common.js 导入uuid
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/' + this.uuid + '/'
        },

        // 检验用户名
        check_username() {
            let re = /^[a-zA-Z0-9_-]{5,20}$/
            if (re.test(this.username)) {
                this.error_username = false;
            } else {
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_username = true;
            }
            if (this.error_username == false) {
                let url = '/usernames/' + this.username + '/count/';
                axios.get(url, {
                    responseType: 'json'
                }).then(response => {
                    if (response.data.count == 1) {
                        this.error_name_message = '用户名已存在';
                        this.error_username = true;
                    } else {
                        this.error_username = false;
                    }
                }).catch(error => {
                    console.log(error.response)
                })
            }

        },
        // 检查密码
        check_password() {
            let re = /^[0-9A-Za-z@_]{8,20}$/
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // 再次确认密码
        check_password2() {
            if (this.password2 != '' && this.password == this.password2) {
                this.error_password2 = false;
            } else {
                this.error_password2 = true;
            }
        },
        // 检验手机号
        check_mobile() {
            let re = /^1[3-9]\d{9}$/
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机格式不正确';
                this.error_mobile = true;
            }
            if (this.error_mobile == false) {
                let url = '/mobiles/' + this.mobile + '/count/'
                axios.get(url, {
                    responseType: 'json'
                }).then(response => {
                    if (response.data.count == 1) {
                        this.error_mobile_message = '手机号已存在';
                        this.error_mobile = true;
                    } else {
                        this.error_mobile = false;
                    }
                }).catch(error => {
                    console.log(error.response)
                    this.error_mobile = true;
                })
            }

        },
        // 检验是否勾选表单
        check_allow() {
            if (this.allow) {
                this.error_allow = false;
            } else {
                this.error_allow = true;
            }
        },
        // 表单提交
        on_submit() {
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();
            if (this.error_username == true || this.error_password == true ||
                this.error_password2 == true || this.error_mobile == true ||
                this.error_allow == true
            ) {
                window.event.returnValue = false;
            }

        },

    }

});