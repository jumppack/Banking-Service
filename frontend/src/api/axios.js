import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to attach the JWT dynamically
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to catch 401s globally (optional UX enhancement)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token likely expired or is invalid. 
            // The AuthContext handles the actual storage, but this acts as an ultimate fail-safe.
            localStorage.removeItem('token');
            // We avoid window.location.href here to let React Router handle navigation natively
        }
        return Promise.reject(error);
    }
);

export default api;
