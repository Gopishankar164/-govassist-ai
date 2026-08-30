import axios from 'axios'
const client = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001', headers: { 'Content-Type': 'application/json' } })
client.interceptors.request.use(config => { const token = localStorage.getItem('govassist-access-token'); if (token) config.headers.Authorization = `Bearer ${token}`; return config })
export const recommend = (query) => client.post('/api/recommend', { query }).then(({ data }) => data)
export const chat = (query, conversation_id = null) => client.post('/api/chat', { query, conversation_id }).then(({ data }) => data)
export const getProfile = (query) => client.post('/api/profile', { query }).then(({ data }) => data)
export const register = (payload) => client.post('/api/auth/register', payload).then(({ data }) => data)
export const login = (payload) => client.post('/api/auth/login', payload).then(({ data }) => data)
export const currentUser = () => client.get('/api/auth/me').then(({ data }) => data.user)
export const logout = () => client.post('/api/auth/logout')
export const getUserProfile = () => client.get('/api/user/profile').then(({ data }) => data)
export const saveUserProfile = (profile) => client.put('/api/user/profile', profile).then(({ data }) => data)
export default client
