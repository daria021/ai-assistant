import {TelegramGameProxy} from "@telegram-apps/sdk";
import {EmojiEntity} from "./components/RichEditor";

declare global {
    interface Window {
        Telegram: {
            WebApp: {
                initData?: string;
                initDataUnsafe?: {
                    query_id?: string;
                    user?: {
                        id: number;
                        first_name?: string;
                        last_name?: string;
                        username?: string;
                        photo_url?: string;
                        language_code?: string;
                    };
                    auth_date?: number;
                    hash?: string;
                };
                expand: () => void;
                close: () => void;
                onEvent: (event_type: str, event_handler: (data: {
                    text: string
                    entities: EmojiEntity[]
                }) => void) => () => never;
            };
        };
        TelegramGameProxy: TelegramGameProxy,
    }
}

export {};
