import axios, { AxiosError } from "axios";
import type { AxiosInstance } from "axios";
import createAuthRefreshInterceptor from "axios-auth-refresh";

const BASE_URL = import.meta.env.VITE_API_BASE || "";

export const apiClient: AxiosInstance = axios.create({
    baseURL: BASE_URL,
    headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": true
    },
});

interface RefreshedTokens {
    access_token: string;
    refresh_token: string;
}

function getAccessToken(): string | null {
    return localStorage.getItem("authToken");
}

function getRefreshToken(): string | null {
    return localStorage.getItem("refreshToken");
}

const refreshAuthLogic = async (failedRequest: AxiosError) => {
    try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) throw new Error("No refresh token found");

        const response = await apiClient.post<RefreshedTokens>("/auth/refresh", {}, {
            headers: {
                "X-Refresh-Token": refreshToken,
            },
        });

        localStorage.setItem("authToken", response.data.access_token);
        localStorage.setItem("refreshToken", response.data.refresh_token);

        failedRequest.response!.config.headers["Authorization"] = `Bearer ${response.data.access_token}`;
        return Promise.resolve();
    } catch (error) {
        console.error("Failed to refresh token", error);
        localStorage.removeItem("authToken");
        localStorage.removeItem("refreshToken");
        return Promise.reject(error);
    }
};

createAuthRefreshInterceptor(apiClient, refreshAuthLogic, {
    pauseInstanceWhileRefreshing: true,
});

apiClient.interceptors.request.use(
    (config) => {
        const token = getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);
