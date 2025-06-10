export interface MeResponse {
    id: string;
    telegram_id?: number;
    telegram_username?: string;
    role: "moderator" | "admin";
    created_at: string;
    updated_at: string;
}
