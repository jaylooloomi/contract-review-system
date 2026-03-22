import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from '../views/UploadPage.vue'
import AnnotationPage from '../views/AnnotationPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: UploadPage },
    { path: '/annotation', component: AnnotationPage },
  ],
})

export default router
