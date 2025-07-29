import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    name: '用户',
    avatar: ''
  }),
  
  actions: {
    setUserInfo(name, avatar = '') {
      this.name = name
      this.avatar = avatar
    }
  }
}) 