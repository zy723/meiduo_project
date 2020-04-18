let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        f1_tab: 1,  // 1F 标签页控制
        f2_tab: 1,  // 2F 标签页控制
        f3_tab: 1,  // 3F 标签页控制
        cart_total_count: 0, // 总的商品数量
        carts: '', // 总的商品数量
    },
    methods: {
        get_carts() {
            let url = '/carts/simple/';
            axios.get(url, {
                responseType: 'json',
            })
                .then(response => {
                    this.carts = response.data.cart_skus;
                    this.cart_total_count = 0;
                    for (let i = 0; i < this.carts.length; i++) {
                        if (this.carts[i].name.length > 25) {
                            this.carts[i].name = this.carts[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.carts[i].count;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    },
});