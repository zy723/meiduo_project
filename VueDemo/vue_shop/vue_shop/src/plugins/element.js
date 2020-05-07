import Vue from 'vue'
import {
  Button,
  Form,
  FormItem,
  Input,
  Message,
  Container,
  Header,
  Aside,
  Main,
  Menu,
  Submenu,
  MenuItemGroup,
  MenuItem,
  Breadcrumb,
  BreadcrumbItem,
  Table,
  TableColumn,
  Card,
  Switch,
  Dialog,
  Row,
  Col,
  Pagination,
  MessageBox,
  Select,
  Option,
  Tag,
} from 'element-ui'

Vue.use(Button)
Vue.use(Form)
Vue.use(FormItem)
Vue.use(Container)
Vue.use(Header)
Vue.use(Aside)
Vue.use(Input)
Vue.use(Main)
Vue.use(Menu)
Vue.use(Submenu)
Vue.use(MenuItemGroup)
Vue.use(MenuItem)
Vue.use(Breadcrumb)
Vue.use(BreadcrumbItem)
Vue.use(Table)
Vue.use(TableColumn)
Vue.use(Card)
Vue.use(Switch)
Vue.use(Dialog)
Vue.use(Row)
Vue.use(Col)
Vue.use(Pagination)
Vue.use(Select)
Vue.use(Option)
Vue.use(Tag)
Vue.prototype.$message = Message
Vue.prototype.$confirm = MessageBox.confirm
