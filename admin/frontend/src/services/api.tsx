import {apiClient, getWithRetry} from "./apiClient";
import type {MeResponse} from "../types/MeResponse";
import type {UserRole} from "../types/UserRole";

export interface Emoji {
    id: string;
    name: string;
    img_url: string;
    custom_emoji_id: string;
    format: "static" | "video" | "lottie"
}

export interface User {
    id: string;
    telegram_username: string;
    role: UserRole
    is_banned: boolean;
}

export interface ChatItem {
    id: string;
    name: string;
    responsible_manager_id: string;
    chat_type_id: string;
}

export interface Post {
    id: string;
    name: string;
    text: string;
    responsible_manager_id: string;
    image_path: string | null;
    html?: string | null;
    entities?: MessageEntityDTO[];
    is_template: boolean;
}

export interface PostToPublish {
    id: string;
    post_id: string;
    responsible_manager_id: string;
    creator_id: string;
    scheduled_type: "everyday" | "single";
    scheduled_date: string | null;
    scheduled_time: string;
    status: string;
    chats: { id: string; chat_id: string; name: string, chat_type_id: string, responsible_manager_id: string }[];  // если сервер отдаёт объекты
    post: Post;
    created_at: string;
    updated_at: string;
}

export interface CreatePostToPublishDTO {
    post_id: string;
    // бэкенд ожидает ScheduledType ("everyday" | "single")
    scheduled_type: "everyday" | "single";
    // формат YYYY-MM-DD, для daily — null/не указывать
    scheduled_date?: string | null;
    // формат HH:mm:ss
    scheduled_time: string;
    // бэкенд ожидает chat_ids: UUID[]
    chat_ids?: string[];
    // бэкенд также использует status/responsible_manager_id/creator_id внутри сервиса
    responsible_manager_id?: string;
    status?: string;
}

export interface UpdateUserDTO {
    role?: UserRole;
    is_banned?: boolean;
}

// export interface Chat {
//     id: string;
//     name: string;
//     chat_id: string;
//     invite_link: string;
// }

/** Сущность для обновления записи «пост в расписании» */
export interface UpdatePostToPublishDTO {
    /** ID сущности «пост в расписании», берётся из записи, а не из тела запроса */
    post_id: string;
    manager_id?: string;
    scheduled_type?: "single" | "everyday";
    /** формат YYYY-MM-DD */
    scheduled_date?: string | null;
    /** формат HH:mm:ss */
    scheduled_time?: string;
    chat_ids?: string[];
    status?: string;
}

/** Сущность для обновления самого поста */
export interface UpdatePostDTO {
    /** ID поста, берётся из записи и используется только для URL */
    post_id: string;
    name?: string;
    text?: string;
    is_template?: boolean;
    /** путь к изображению, если нужно заменить или убрать */
    image_path?: string | null;
    /** HTML версия текста (если используете rich editor) */
    html?: string | null;
    /** массив MessageEntityDTO, если есть эмодзи/разметка */
    entities?: MessageEntityDTO[];
}

/** Тип для сущности в тексте (копируйте из вашего MessageEntityDTO) */
export interface MessageEntityDTO {
    type:
        | "custom_emoji"
        | "bold"
        | "italic"
        | "underline"
        | "strikethrough"
        | "text_link"
        | "blockquote";
    offset: number;
    length: number;
    custom_emoji_id?: string;
    url?: string;
}


export interface Chat {
    id: string;
    name: string;
    chat_id: number;
    invite_link?: string;
    chat_type_id?: string | null;
}

export interface CreateChatDTO {
    invite_link: string;
    chat_type_id: string;
    responsible_manager_id: string;
}

export interface UpdateChatDTO {
    chat_type_id?: string | null;
    invite_link?: string;
}

export interface ChatType {
    id: string;
    name: string;
    description: string;
}

export interface CreateChatTypeDTO {
    name: string;
    description: string;
}

export interface UpdateChatTypeDTO {
    name?: string;
    description?: string;
}

export async function getChatTypes(): Promise<ChatType[]> {
    return (await apiClient.get<ChatType[]>(`/chat_type`)).data;
}

export async function createChatType(
    payload: CreateChatTypeDTO
): Promise<void> {
    await apiClient.post(`/chat_type`, payload);
}

export async function updateChatType(
    id: string,
    payload: UpdateChatTypeDTO
): Promise<void> {
    await apiClient.patch(`/chat_type/${id}`, payload);
}

export async function deleteChatType(
    id: string
): Promise<void> {
    await apiClient.delete(`/chat_type/${id}`);
}


export async function getChatsByType(
    typeId: string
): Promise<Chat[]> {
    return (
        await apiClient.get<Chat[]>(`/chat/type/${typeId}`)
    ).data;
}

export async function createChat(
    payload: CreateChatDTO
): Promise<Chat> {
    const {data} = await apiClient.post<Chat>(`/chat`, payload);
    return data;
}

export async function updateChat(
    id: string,
    payload: UpdateChatDTO
): Promise<void> {
    await apiClient.patch(`/chat/${id}`, payload);
}

/** 1) Создать сущность Post (multipart/form-data) */
export async function createPost(
    name: string,
    text: string,
    is_template: boolean,
    html: string,
    entities: MessageEntityDTO[],
    imageFile?: File,
): Promise<string> {
    const form = new FormData();
    form.append("name", name);
    form.append("text", text);
    form.append("is_template", String(is_template));   // "true" | "false"
    form.append("html", html);
    form.append("entities", JSON.stringify(entities));
    if (imageFile) form.append("image", imageFile);

    console.log('API_OUT', JSON.stringify(text), entities);
    console.group('%cupdatePost FormData', 'color: purple; font-weight: bold;');
    for (const [key, value] of Array.from(form.entries())) {
        console.log(key, value);
    }
    console.groupEnd();

    // Вернёт UUID созданного поста
    const response = await apiClient.post<string>("post", form, {
        headers: {"Content-Type": "multipart/form-data"},
    });
    return response.data;
}


export async function updatePost(
    postId: string,
    title?: string | null,
    is_template?: boolean,
    editorText?: string | null,
    editorHtml?: string | null,
    editorEntities?: MessageEntityDTO[] | null,
    photoFile?: File | null
) {
    const form = new FormData()
    if (title) form.append("name", title);
    if (editorText) form.append("text", editorText);
    if (is_template !== undefined) form.append("is_template", String(is_template));
    if (editorHtml) form.append("html", editorHtml);
    if (editorEntities) form.append('entities', JSON.stringify(editorEntities));
    if (photoFile) form.append('image', photoFile);
    return apiClient.patch(`/post/${postId}`, form, {
        headers: {"Content-Type": "multipart/form-data"},
    });
}

export async function deleteChat(
    id: string
): Promise<void> {
    await apiClient.delete(`/chat/${id}`);
}

/** 2) Создать запись поста для публикации */
export async function createPostToPublish(dto: CreatePostToPublishDTO): Promise<string> {
    // Вернёт UUID записи в post-to-publish
    const response = await apiClient.post<string>("post-to-publish", dto);
    return response.data;
}

export async function updatePostToPublish(id: string, payload: UpdatePostToPublishDTO): Promise<void> {
    await apiClient.patch(`/post-to-publish/${id}`, payload);
}

export async function deletePostToPublish(postToPublishId: string) {
    await apiClient.delete("/post-to-publish", {
        params: {post_to_publish_id: postToPublishId},
    });
}

export async function getMe(): Promise<MeResponse> {
    return (await apiClient.get<MeResponse>(`users/me`)).data;
}

export async function getUsers(): Promise<User[]> {
    return (await apiClient.get(`users/all`)).data;
}

export async function updateUser(
    id: string,
    payload: UpdateUserDTO
): Promise<User> {
    const {data} = await apiClient.patch<User>(`/users/${id}`, payload);
    return data;
}

export async function getManagers(): Promise<User[]> {
    return (await apiClient.get(`users/managers`)).data;
}

export async function deleteUser(userId: string) {
    // формируем URL с query-параметром user_id
    return (await apiClient.delete(`/users`, {
        params: {user_id: userId}
    })).data;
}

export async function getPostsToPublish(): Promise<PostToPublish[]> {
    // с ретраями для проблемной сети/телеги/интернета
    return await getWithRetry<PostToPublish[]>("/post-to-publish/all");
}

export async function getPost(postId: string): Promise<Post> {
    return await getWithRetry<Post>("post", {params: {post_id: postId}});
}

export async function getPosts(): Promise<Post[]> {
    return await getWithRetry<Post[]>("post/all");
}

export async function getChats(): Promise<ChatItem[]> {
    return await getWithRetry<ChatItem[]>("chat");
}

export type CreateChatByLinkDTO = {
    invite_link: string;
    manager_id: string;
    chat_type_id?: string;
}

export async function createChatByLink(dto: CreateChatByLinkDTO): Promise<ChatItem> {
    const response = await apiClient.post<ChatItem>(
        "chat",
        dto,
    );
    return response.data;
}

export async function getAuthCode(phone: string): Promise<void> {
    await apiClient.get("/users/code", {
        params: {
            phone,
        }
    });
}

export async function sendAuthCode(phone: string, code: string, password?: string): Promise<void> {
    await apiClient.post("/users/code",
        {
            phone,
            code,
            password,
        }
    );
}

export async function listEmojis(): Promise<Emoji[]> {
    const res = (await apiClient.get<Emoji[]>('emoji')).data
    console.log("emojis!!", res);
    return res;
}


/** Получить одну запись «PostToPublish» по её ID */
export async function getPostToPublish(
    postToPublishId: string
): Promise<PostToPublish> {
    // backend: @router.get('') async def get_post_to_publish(post_to_publish_id: UUID)
    // обычно это GET /post-to-publish?post_to_publish_id=...
    return (
        await apiClient.get<PostToPublish>("/post-to-publish", {
            params: {post_to_publish_id: postToPublishId},
        })
    ).data;
}


