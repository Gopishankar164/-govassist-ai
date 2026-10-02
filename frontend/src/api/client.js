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
export const chatStream = async (query, conversation_id, onMetadata, onChunk, onDone, onError, signal) => {
    const url = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001') + '/api/chat';
    const token = localStorage.getItem('govassist-access-token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify({ query, conversation_id }),
            signal
        });
        
        if (!response.ok) {
            let errMsg = 'Streaming failed';
            try {
                const err = await response.json();
                errMsg = err.detail || errMsg;
            } catch (e) {}
            throw new Error(errMsg);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split('\n\n');
            buffer = parts.pop();
            
            for (const part of parts) {
                if (part.startsWith('data: ')) {
                    const dataStr = part.replace('data: ', '');
                    try {
                        const parsed = JSON.parse(dataStr);
                        if (parsed.type === 'metadata') {
                            onMetadata(parsed.content);
                        } else if (parsed.type === 'chunk') {
                            onChunk(parsed.content);
                        } else if (parsed.type === 'done') {
                            onDone();
                        }
                    } catch (e) {
                        console.error("Failed to parse chunk", e);
                    }
                }
            }
        }
    } catch (e) {
        onError(e);
    }
}
export default client
