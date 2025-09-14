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

// ─────────────────────────────────────────────────────────────────────────────
// Простые ретраи для GET с экспоненциальной паузой
// ─────────────────────────────────────────────────────────────────────────────

function sleep(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

type RetryOptions = {
    retries?: number;
    baseDelayMs?: number;
    factor?: number;
    jitterMs?: number;
    retryOnStatus?: number[];
};

async function getWithRetry<T>(
    url: string,
    config?: Parameters<AxiosInstance["get"]>[1],
    opts: RetryOptions = {}
): Promise<T> {
    const {
        retries = 3,
        baseDelayMs = 300,
        factor = 2,
        jitterMs = 120,
        retryOnStatus = [408, 429, 500, 502, 503, 504],
    } = opts;

    let attempt = 0;
    // eslint-disable-next-line no-constant-condition
    while (true) {
        try {
            const res = await apiClient.get<T>(url, config);
            return res.data;
        } catch (e) {
            attempt += 1;
            // если исчерпали попытки — пробрасываем ошибку
            if (attempt > retries) throw e;

            // определяем, стоит ли ретраить
            if (axios.isAxiosError(e)) {
                const status = e.response?.status;
                const networkLike = !e.response; // таймаут/сеть/прерывание
                const shouldRetry = networkLike || (status ? retryOnStatus.includes(status) : false);
                if (!shouldRetry) throw e;
            }

            // backoff с небольшим джиттером
            const delay = baseDelayMs * Math.pow(factor, attempt - 1) + Math.random() * jitterMs;
            await sleep(delay);
        }
    }
}

export { getWithRetry };
