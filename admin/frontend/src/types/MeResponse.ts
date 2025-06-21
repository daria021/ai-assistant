import type {UserRole} from "./UserRole";

export interface MeResponse {
    id: string;
    telegram_id?: number;
    telegram_username?: string;
    role: UserRole;
    is_banned: boolean;
    created_at: string;
    updated_at: string;
}
