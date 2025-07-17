import FileUploader from "../components/FileUploader";

import {useCallback, useEffect, useMemo, useRef, useState} from "react";
import {useLocation, useNavigate} from "react-router-dom";
import {FiChevronDown, FiChevronUp} from "react-icons/fi";
import {on} from "@telegram-apps/sdk";
import {
    createPost,
    createPostToPublish,
    deletePostToPublish,
    type Emoji,
    getChats,
    getChatTypes,
    getManagers,
    getPost,
    getPostsToPublish
} from "../services/api";
import {useAuth} from "../contexts/auth";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import type {RichEditorHandle} from "../components/RichEditor";
import {RichEditor} from "../components/RichEditor";
import type {UserRole} from "../types/UserRole";
import {EmojiPicker} from "../components/EmojiPicker";

/* ───────── Типы ───────── */
type EventItem = {
    id: string;
    postId: string;
    title: string;
    time: string;
    scheduledType: "single" | "everyday";
};

export interface Post {
    id: string;
    name: string;
    responsible_manager_id: string;
    text: string;
    image_path: string | null;
    html?: string | null;
    entities?: MessageEntityDTO[];
}

interface ChatItem {
    id: string;
    name: string;
}

export interface CreatePostToPublishDTO {
    post_id: string;
    scheduled_type: "everyday" | "single";
    responsible_manager_id: string;
    scheduled_date?: string | null;
    scheduled_time: string;
    chat_ids?: string[];
    manager_id: string;
    status: string;
}

export interface MessageEntityDTO {
    type: "custom_emoji" | "bold" | "italic" | "underline";
    offset: number;
    length: number;
    custom_emoji_id?: string;
}

export interface User {
    id: string;
    telegram_username: string;
    role: UserRole;
}

type ChatTypeItem = { id: string; name: string };

interface PostsControlPageProps {
    emojis: Emoji[];
}

export default function PostsControlPage({emojis}: PostsControlPageProps) {
    /* ───────── Tabs ───────── */
    const [activeTab, setActiveTab] = useState<"schedule" | "create" | "templates">(
        "schedule"
    );

    /* ───────── Form ───────── */
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string | null>(null);
    const [title, setTitle] = useState("");
    const [scheduleType, setScheduleType] = useState<"once" | "daily">("once");

    /* ───────── Chats ───────── */
    const [chats, setChats] = useState<ChatItem[]>([]);
    const [selectedChats, setSelectedChats] = useState<string[]>([]);
    const [chatSearch, setChatSearch] = useState("");

    /* ───────── Filters ───────── */
    const [managerFilter, setManagerFilter] = useState<string>("");
    const [chatTypeFilter, setChatTypeFilter] = useState<string>("");
    const [chatFilter, setChatFilter] = useState<string>("");

    const [chatTypes, setChatTypes] = useState<ChatTypeItem[]>([]);

    /* ───────── Schedule list ───────── */
    const [schedule, setSchedule] = useState<Record<string, EventItem[]>>({});
    const [openDays, setOpenDays] = useState<Record<string, boolean>>({});
    const [scheduledAt, setScheduledAt] = useState<Date | null>(null);
    const [timeOnly, setTimeOnly] = useState<Date | null>(null);

    /* ───────── Rich-editor ───────── */
    const [editorHtml, setEditorHtml] = useState("");
    const [editorText, setEditorText] = useState("");
    const [editorEntities, setEditorEntities] = useState<MessageEntityDTO[]>([]);
    const [responsibleManagerId, setResponsibleManagerId] = useState("");

    const navigate = useNavigate();
    const {userId, role} = useAuth();

    const [managers, setManagers] = useState<User[]>([]);

    /* ───────── Initial fetch ───────── */
    useEffect(() => {
        getManagers().then(setManagers).catch(console.error);
        getChatTypes().then(setChatTypes).catch(console.error);
    }, []);


    const richEditorRef = useRef<RichEditorHandle>(null)
    const [pickerOpen, setPickerOpen] = useState(false)

    /* ───────── Template pre-fill ───────── */
    const location = useLocation();
    type LocationState = { template?: Post; openCreate?: true };
    const {template, openCreate} = (location.state as LocationState) || {};

    useEffect(() => {
        if (openCreate) setActiveTab("create");
    }, [openCreate]);

    useEffect(() => {
        if (template) {
            setTitle(template.name);
            setEditorText(template.text);
            setEditorHtml(template.html || "");
            setEditorEntities(template.entities || []);
            if (template.image_path) setPhotoPreview(template.image_path);
            setActiveTab("create");
        }
    }, [template]);

    /* ───────── Helpers ───────── */
    const filteredChats = useMemo(
        () =>
            chats.filter((c) =>
                c.name.toLowerCase().includes(chatSearch.trim().toLowerCase())
            ),
        [chatSearch, chats]
    );

    const handleChatToggle = (chatId: string) => {
        setSelectedChats((prev) =>
            prev.includes(chatId) ? prev.filter((c) => c !== chatId) : [...prev, chatId]
        );
    };

    /* ───────── Schedule fetch ───────── */
    const fetchSchedule = useCallback(async () => {
        try {
            const raw = await getPostsToPublish();

            /* --- фильтрация --- */
            const filtered = raw.filter((p) => {
                if (managerFilter && p.responsible_manager_id !== managerFilter) return false;
                if (
                    chatTypeFilter &&
                    !p.chats.some((c) => c.chat_type_id === chatTypeFilter)
                )
                    return false;
                if (chatFilter && !p.chats.some((c) => c.id === chatFilter)) return false;
                return true;
            });

            /* --- заголовки постов --- */
            const titlesCache = new Map<string, string>();
            await Promise.all(
                filtered.map(async (p) => {
                    if (!titlesCache.has(p.post_id)) {
                        const post = await getPost(p.post_id);
                        titlesCache.set(p.post_id, post.name);
                    }
                })
            );

            /* --- группировка по дням --- */
            const map: Record<string, EventItem[]> = {};
            const today = new Date();

            for (const p of filtered) {
                const item: EventItem = {
                    id: p.id,
                    postId: p.post_id,
                    title: titlesCache.get(p.post_id) ?? "Без названия",
                    time: p.scheduled_time.slice(0, 5),
                    scheduledType: p.scheduled_type
                };

                if (p.scheduled_type === "single" && p.scheduled_date) {
                    const d = new Date(p.scheduled_date);
                    const iso = d.toISOString().slice(0, 10);
                    map[iso] = (map[iso] || []).concat(item);
                } else {
                    for (let i = 0; i < 7; i++) {
                        const d = new Date(today);
                        d.setDate(d.getDate() + i);
                        const iso = d.toISOString().slice(0, 10);
                        map[iso] = (map[iso] || []).concat(item);
                    }
                }
            }

            Object.values(map).forEach((arr) =>
                arr.sort((a, b) => a.time.localeCompare(b.time))
            );
            setSchedule(map);
        } catch (err) {
            console.error("Не удалось загрузить расписание", err);
            alert("Ошибка при загрузке расписания");
        }
    }, [managerFilter, chatTypeFilter, chatFilter]);


    /* ───────── Chats fetch ───────── */
    const fetchChats = useCallback(async () => {
        try {
            const data = await getChats();
            setChats(data);
        } catch (err) {
            console.error("Не удалось загрузить список чатов", err);
        }
    }, []);

    /* ───────── run fetches ───────── */
    useEffect(() => {
        fetchChats();
    }, []);

    useEffect(() => {
        fetchSchedule();
    }, [fetchSchedule]);

    /* ───────── Back button ───────── */
    useEffect(() => {
        const remove = on("back_button_pressed", () => navigate(`/`));
        return () => remove();
    }, [navigate]);


    /* ───────── Save Post ───────── */
    const handleSave = async () => {
        if (!title.trim() || !editorText.trim()) {
            alert("Введите название и текст поста");
            return;
        }
        if (scheduleType === "once" && !scheduledAt) {
            alert("Выберите дату и время");
            return;
        }
        if (scheduleType === "daily" && !timeOnly) {
            alert("Выберите время для ежедневной рассылки");
            return;
        }
        if (!userId) {
            alert("Не удалось определить менеджера");
            return;
        }

        try {
            const postId = await createPost(
                title,
                editorText,
                editorHtml,
                editorEntities,
                photoFile ?? undefined
            );

            let scheduled_date: string | null = null;
            let scheduled_time: string;

            if (scheduleType === "once") {
                scheduled_date = scheduledAt!.toLocaleDateString("sv-SE");
                scheduled_time = scheduledAt!.toLocaleTimeString("ru-RU", {
                    hour: "2-digit",
                    minute: "2-digit"
                });
            } else {
                scheduled_time = timeOnly!.toLocaleTimeString("ru-RU", {
                    hour: "2-digit",
                    minute: "2-digit"
                });
            }

            const dto: CreatePostToPublishDTO = {
                post_id: postId,
                scheduled_type: scheduleType === "once" ? "single" : "everyday",
                responsible_manager_id: responsibleManagerId,
                scheduled_date,
                scheduled_time,
                chat_ids: selectedChats,
                manager_id: userId,
                status: "pending"
            };

            await createPostToPublish(dto);
            await fetchSchedule();

            /* reset */
            setPhotoFile(null);
            setPhotoPreview(null);
            setTitle("");
            setEditorText("");
            setEditorHtml("");
            setEditorEntities([]);
            setScheduledAt(null);
            setTimeOnly(null);
            setScheduleType("once");
            setSelectedChats([]);
            setChatSearch("");
            setActiveTab("schedule");
        } catch (err) {
            console.error("Ошибка при сохранении поста:", err);
            alert("Не удалось создать пост.");
        }
    };

    /* ───────── Delete Schedule Item ───────── */
    const handleDelete = async (day: string, ev: EventItem) => {
        if (!window.confirm(`Удалить пост «${ev.title}» из расписания?`)) return;
        try {
            await deletePostToPublish(ev.id);
            setSchedule((prev) => {
                const next = {...prev};
                next[day] = next[day].filter((i) => i.id !== ev.id);
                if (next[day].length === 0) delete next[day];
                return next;
            });
        } catch {
            alert("Ошибка при удалении.");
        }
    };

    const toggleDay = (d: string) =>
        setOpenDays((o) => ({...o, [d]: !o[d]}));

    /* ───────── UI ───────── */
    return (
        <div className="container mx-auto p-4 bg-brandlight min-h-screen">


            {/* ───────── Tabs ───────── */}
            <div className="flex space-x-8 mb-6">
                {(["schedule", "create", "templates"] as const).map((tab) => (
                    <button
                        key={tab}
                        onClick={() => {
                            if (tab === "templates") navigate("/posts/templates");
                            else setActiveTab(tab);
                        }}
                        className={`transition pb-1 ${
                            activeTab === tab
                                ? "text-2xl font-semibold text-brand border-b-2 border-brand"
                                : "text-xl text-gray-600"
                        }`}
                    >
                        {tab === "schedule" ? "Расписание" : tab === "create" ? "Создать пост" : "Шаблоны"}
                    </button>
                ))}
            </div>

            {/* ───────── Create tab ───────── */}
            {activeTab === "create" && (
                <div className="space-y-6 max-w-lg">
                    {/* Фото */}
                    <FileUploader
                        label="Фото поста"
                        file={photoFile}
                        preview={photoPreview}
                        onFileChange={(f) => {
                            setPhotoFile(f)
                            setPhotoPreview(f ? URL.createObjectURL(f) : null)
                        }}
                    />

                    {/* Название */}
                    <div>
                        <label className="block mb-2 font-medium">Название поста</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                    </div>

                    {/* Текст */}
                    <div>
                        <div className="relative">
                            <div className="flex items-center mb-2">
                                <label className="block mb-2 font-medium">Текст поста</label>
                                <button
                                    type="button"
                                    onClick={() => setPickerOpen((o) => !o)}
                                    className="ml-2 px-2 py-1 mb-2 rounded hover:bg-gray-200"
                                >
                                    😊
                                </button>
                            </div>
                        </div>
                        <RichEditor
                            ref={richEditorRef}
                            emojis={emojis}
                            initialContent={editorHtml}
                            onChange={({html, text, entities}) => {
                                setEditorHtml(html)
                                setEditorText(text)
                                setEditorEntities(entities)
                            }}
                        />
                        {pickerOpen && (

                            <EmojiPicker
                                emojis={emojis}
                                onSelect={(emoji) => {
                                    richEditorRef.current?.insertEmoji(emoji)
                                    setPickerOpen(false)
                                }}
                            />

                        )}
                    </div>

                    {/* Ответственный менеджер */}
                    <div>
                        <label className="block mb-2 font-medium">Ответственный менеджер</label>
                        <select
                            value={responsibleManagerId}
                            onChange={(e) => setResponsibleManagerId(e.target.value)}
                            className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        >
                            <option value="" disabled>
                                — выберите менеджера —
                            </option>
                            {managers.map((m) => (
                                <option key={m.id} value={m.id}>
                                    {m.telegram_username}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Тип рассылки */}
                    <div>
                        <label className="block mb-2 font-medium">Тип рассылки</label>
                        <div className="flex space-x-4">
                            <label className="flex items-center space-x-2">
                                <input
                                    type="radio"
                                    name="scheduleType"
                                    value="once"
                                    checked={scheduleType === "once"}
                                    onChange={() => setScheduleType("once")}
                                    className="form-radio h-4 w-4 text-brand"
                                />
                                <span>В указанный день</span>
                            </label>
                            <label className="flex items-center space-x-2">
                                <input
                                    type="radio"
                                    name="scheduleType"
                                    value="daily"
                                    checked={scheduleType === "daily"}
                                    onChange={() => setScheduleType("daily")}
                                    className="form-radio h-4 w-4 text-brand"
                                />
                                <span>Каждый день</span>
                            </label>
                        </div>
                    </div>

                    {/* Дата / Время */}
                    {scheduleType === "once" ? (
                        <div>
                            <label className="block mb-2 font-medium">Дата и время</label>
                            <DatePicker
                                selected={scheduledAt}
                                onChange={setScheduledAt}
                                showTimeSelect
                                timeFormat="HH:mm"
                                timeIntervals={15}
                                dateFormat="dd.MM.yyyy HH:mm"
                                placeholderText="Кликните для выбора"
                                className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                            />
                        </div>
                    ) : (
                        <div>
                            <label className="block mb-2 font-medium">Время</label>
                            <DatePicker
                                selected={timeOnly}
                                onChange={setTimeOnly}
                                showTimeSelect
                                showTimeSelectOnly
                                timeIntervals={15}
                                dateFormat="HH:mm"
                                placeholderText="Выберите время"
                                className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                            />
                        </div>
                    )}

                    {/* Чаты */}
                    <div>
                        <label className="block mb-2 font-medium">Чаты для отправки</label>
                        <input
                            type="text"
                            placeholder="Поиск чатов..."
                            value={chatSearch}
                            onChange={(e) => setChatSearch(e.target.value)}
                            className="w-full mb-2 border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                        <div className="max-h-60 overflow-y-auto space-y-2 border border-brand rounded p-2">
                            {filteredChats.map(({id, name}) => (
                                <label key={id} className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        checked={selectedChats.includes(id)}
                                        onChange={() => handleChatToggle(id)}
                                        className="form-checkbox h-5 w-5 text-brand focus:ring-brand"
                                    />
                                    <span>{name}</span>
                                </label>
                            ))}
                            {filteredChats.length === 0 && (
                                <div className="text-gray-500 italic">Чаты не найдены</div>
                            )}
                        </div>
                    </div>

                    {/* Сохранить */}
                    <button
                        onClick={handleSave}
                        className="w-full py-3 bg-brand text-white rounded-lg shadow hover:bg-brand2 transition"
                    >
                        Сохранить
                    </button>
                </div>
            )}


            {/* ───────── Schedule tab ───────── */}
            {activeTab === "schedule" && (

                <div className="space-y-4 text-brand">
                    <div className="flex flex-wrap gap-4 mb-6">
                        {/* manager */}
                        {role !== "manager" && (
                            <select
                                value={managerFilter}
                                onChange={(e) => setManagerFilter(e.target.value)}
                                className="border border-brand rounded p-2"
                            >
                                <option value="">— все менеджеры —</option>
                                {managers.map((m) => (
                                    <option key={m.id} value={m.id}>
                                        {m.telegram_username}
                                    </option>
                                ))}
                            </select>
                        )}
                        {/* chat-type */}
                        <select
                            value={chatTypeFilter}
                            onChange={(e) => setChatTypeFilter(e.target.value)}
                            className="border border-brand rounded p-2"
                        >
                            <option value="">— все группы чатов —</option>
                            {chatTypes.map((ct) => (
                                <option key={ct.id} value={ct.id}>
                                    {ct.name}
                                </option>
                            ))}
                        </select>

                        {/* chat */}
                        <select
                            value={chatFilter}
                            onChange={(e) => setChatFilter(e.target.value)}
                            className="border border-brand rounded p-2"
                        >
                            <option value="">— все чаты —</option>
                            {chats.map((c) => (
                                <option key={c.id} value={c.id}>
                                    {c.name}
                                </option>
                            ))}
                        </select>

                        {(managerFilter || chatTypeFilter || chatFilter) && (
                            <button
                                onClick={() => {
                                    setManagerFilter("");
                                    setChatTypeFilter("");
                                    setChatFilter("");
                                }}
                                className="px-4 py-2 bg-brand text-white rounded"
                            >
                                Сбросить
                            </button>
                        )}
                    </div>
                    {Object.keys(schedule)
                        .sort()
                        .map((iso) => {
                            const label = new Date(iso).toLocaleDateString("ru-RU", {
                                day: "2-digit",
                                month: "long",
                                year: "numeric"
                            });
                            return (
                                <div key={iso} className="bg-brand-pink p-4 rounded-lg shadow">
                                    <div
                                        className="flex justify-between items-center cursor-pointer"
                                        onClick={() => toggleDay(iso)}
                                    >
                                        <h2 className="text-xl font-semibold">{label}</h2>
                                        {openDays[iso] ? <FiChevronUp/> : <FiChevronDown/>}
                                    </div>

                                    {openDays[iso] && (
                                        <ul className="mt-4 space-y-2">
                                            {schedule[iso].map((ev) => (
                                                <li
                                                    key={ev.id}
                                                    className="flex items-center justify-between p-2 hover:bg-gray-100 rounded cursor-pointer"
                                                    onClick={() => navigate(`/post-details/${ev.id}`)}
                                                >
                          <span>
                            <span className="font-medium">{ev.time}</span> — {ev.title}
                          </span>
                                                    <img
                                                        src="/icons/trash.png"
                                                        alt="Удалить"
                                                        className="h-5 w-5 opacity-60 hover:opacity-100"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleDelete(iso, ev);
                                                        }}
                                                    />
                                                </li>
                                            ))}
                                        </ul>
                                    )}
                                </div>
                            );
                        })}
                </div>
            )}
        </div>
    );
}
