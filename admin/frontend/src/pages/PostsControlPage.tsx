import FileUploader from "../components/FileUploader";

import {useCallback, useEffect, useMemo, useState} from "react";
import {useNavigate} from "react-router-dom";
import {FiChevronDown, FiChevronUp} from "react-icons/fi";
import {on} from "@telegram-apps/sdk";
import {
    createChatByLink,
    createPost,
    createPostToPublish,
    deletePostToPublish,
    type Emoji,
    getChats,
    getPost,
    getPostsToPublish,
} from "../services/api";
import {useAuth} from "../contexts/auth";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import {RichEditor} from "../components/RichEditor";

/* ────────────────────────────────────────────────────────────────────────── */
/*  Types                                                                   */
/* ────────────────────────────────────────────────────────────────────────── */
type EventItem = {
    id: string;
    postId: string;
    title: string;
    time: string;
    scheduledType: "single" | "everyday";
};

interface ChatItem {
    id: string;
    name: string;
}

export interface CreatePostToPublishDTO {
    post_id: string;
    scheduled_type: "everyday" | "single";
    scheduled_date?: string | null;
    scheduled_time: string;
    chat_ids?: string[]; // массив chat.id
    manager_id: string;
    status: string;
}


export interface MessageEntityDTO {
    /** всегда "custom_emoji" для наших эмоджи */
    type: 'custom_emoji' | 'bold' | 'italic' | 'underline';
    /** позиция в тексте */
    offset: number;
    /** длина (для эмоджи всегда 1) */
    length: number;
    /** custom_emoji_id из Telegram */
    custom_emoji_id?: string;
}


interface PostsControlPageProps {
    emojis: Emoji[]
}

/* ────────────────────────────────────────────────────────────────────────── */
/*  Component                                                               */
/* ────────────────────────────────────────────────────────────────────────── */
export default function PostsControlPage({emojis}: PostsControlPageProps) {
    // теперь emojis доступен и его можно использовать
    console.log('доступные эмоджи', emojis)

    /* ───────── State ───────── */
    const [activeTab, setActiveTab] = useState<"schedule" | "create">("schedule");

    // ── Form
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string | null>(null);
    const [title, setTitle] = useState("");
    const [scheduleType, setScheduleType] = useState<"once" | "daily">("once");

    // ── Chats
    const [chats, setChats] = useState<ChatItem[]>([]);
    const [selectedChats, setSelectedChats] = useState<string[]>([]);
    const [chatSearch, setChatSearch] = useState("");

    // modal for adding chat link
    const [showAddChatModal, setShowAddChatModal] = useState(false);
    const [newChatLink, setNewChatLink] = useState("");

    // ── Schedule list
    const [schedule, setSchedule] = useState<Record<string, EventItem[]>>({});
    const [openDays, setOpenDays] = useState<Record<string, boolean>>({});
    const [scheduledAt, setScheduledAt] = useState<Date | null>(null);
    const [timeOnly, setTimeOnly] = useState<Date | null>(null);

// внутри PostsControlPage в секции State
    const [editorHtml, setEditorHtml] = useState<string>('');
    const [editorText, setEditorText] = useState<string>('');
    const [editorEntities, setEditorEntities] = useState<MessageEntityDTO[]>([]);

    const navigate = useNavigate();

    const {userId} = useAuth();

    /* ───────── Data fetching ───────── */
    // Поиск по названию чата
    const filteredChats = useMemo(
        () =>
            chats.filter(c =>
                c.name.toLowerCase().includes(chatSearch.trim().toLowerCase())
            ),
        [chatSearch, chats]
    );

    // Тоггл выбора чата по id
    const handleChatToggle = (chatId: string) => {
        setSelectedChats(prev =>
            prev.includes(chatId) ? prev.filter(c => c !== chatId) : [...prev, chatId]
        );
    };

    const fetchSchedule = useCallback(async () => {
        try {
            const raw = await getPostsToPublish();

            // pull post titles in parallel
            const titlesCache = new Map<string, string>();
            await Promise.all(
                raw.map(async (p) => {
                    if (!titlesCache.has(p.post_id)) {
                        const post = await getPost(p.post_id);
                        titlesCache.set(p.post_id, post.name);
                    }
                }),
            );

            // group by day
            const map: Record<string, EventItem[]> = {};
            const today = new Date();

            for (const p of raw) {
                const item: EventItem = {
                    id: p.id,
                    postId: p.post_id,
                    title: titlesCache.get(p.post_id) ?? "Без названия",
                    time: p.scheduled_time.slice(0, 5), // HH:MM
                    scheduledType: p.scheduled_type,
                };

                if (p.scheduled_type === "single" && p.scheduled_date) {
                    const d = new Date(p.scheduled_date);
                    const isoKey = d.toISOString().slice(0, 10);           // "YYYY-MM-DD"
                    map[isoKey] = (map[isoKey] || []).concat(item);
                } else {
                    for (let i = 0; i < 7; i++) {
                        const d = new Date(today);
                        d.setDate(d.getDate() + i);
                        const isoKey = d.toISOString().slice(0, 10);
                        map[isoKey] = (map[isoKey] || []).concat(item);
                    }
                }


            }

            // sort inside each day
            Object.values(map).forEach((arr) => arr.sort((a, b) => a.time.localeCompare(b.time)));
            setSchedule(map);
        } catch (err) {
            console.error("Не удалось загрузить расписание", err);
            alert("Ошибка при загрузке расписания");
        }
    }, []);

    // Загрузка существующих чатов с сервера
    const fetchChats = useCallback(async () => {
        try {
            const data: ChatItem[] = await getChats();
            setChats(data);
        } catch (err) {
            console.error("Не удалось загрузить список чатов", err);
            alert("Ошибка при загрузке чатов");
        }
    }, []);


    useEffect(() => {
        fetchChats();
        fetchSchedule();
    }, [fetchChats, fetchSchedule]);

    /* back button hook */
    useEffect(() => {
        const removeBack = on("back_button_pressed", () => navigate(-1));
        return () => removeBack();

    }, [navigate]);

    const handleAddChat = async () => {
        const link = newChatLink.trim();
        if (!link) return;

        try {
            const chat: ChatItem = await createChatByLink(link);

            setChats(prev =>
                prev.some(c => c.id === chat.id) ? prev : [...prev, chat]
            );
            setNewChatLink("");
            setShowAddChatModal(false);
        } catch (err) {
            console.error(err);
            alert("Не удалось добавить чат. Проверьте ссылку.");
        }
    };


    const handleFileChange = (file: File | null) => {
        setPhotoFile(file);
        setPhotoPreview(file ? URL.createObjectURL(file) : null);
    };


    const handleSave = async () => {
        // 1. Валидация
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
            // 2. Создаём сам пост
            const postId = await createPost(title, editorText, editorHtml, editorEntities, photoFile ?? undefined);

            let scheduled_date: string | null = null;
            let scheduled_time: string;

            // если «в указанный день»
            if (scheduleType === "once") {
                if (!scheduledAt) {
                    alert("Выберите дату и время");
                    return;
                }
                // дата в формате YYYY-MM-DD
                scheduled_date = scheduledAt.toLocaleDateString('sv-SE');
                // локальное время, например "15:30"
                scheduled_time = scheduledAt.toLocaleTimeString('ru-RU', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } else {
                // ежедневная рассылка
                if (!timeOnly) {
                    alert("Выберите время для ежедневной рассылки");
                    return;
                }
                // не меняем дату, только время
                scheduled_time = timeOnly.toLocaleTimeString('ru-RU', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            }

            // дальше формируем DTO с использованием именно этой переменной
            const dto: CreatePostToPublishDTO = {
                post_id: postId,
                scheduled_type: scheduleType === "once" ? "single" : "everyday",
                scheduled_date,     // либо "2025-06-11", либо null
                scheduled_time,     // например "15:30"
                chat_ids: selectedChats,
                manager_id: userId,
                status: "pending",
            };

            // 5. Отправляем на бэкенд
            await createPostToPublish(dto);

            // 6. Обновляем локальное расписание
            await fetchSchedule();

            // 7. Сбрасываем форму
            setPhotoFile(null);
            setPhotoPreview(null);
            setTitle("");
            // setEditorHtml("");
            setEditorText("");
            setEditorEntities([]);
            setScheduledAt(null);
            setTimeOnly(null);
            setScheduleType("once");
            setSelectedChats([]);
            setChatSearch("");
            setActiveTab("schedule");

        } catch (err) {
            console.error("Ошибка при сохранении поста:", err);
            alert("Не удалось создать пост. Попробуйте ещё раз.");
        }
    };


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
        } catch (err) {
            console.error("Не получилось удалить запись", err);
            alert("Ошибка при удалении. Попробуйте ещё раз.");
        }
    };

    const toggleDay = (day: string) =>
        setOpenDays((o) => ({
            ...o,
            [day]: !o[day],
        }));


    /* ───────── Render ───────── */
    return (
        <div className="container mx-auto p-4 bg-brandlight min-h-screen">
            {/* ───────── Tabs ───────── */}
            <div className="flex space-x-8 mb-6">
                {(["schedule", "create"] as const).map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`transition pb-1 ${
                            activeTab === tab
                                ? "text-2xl font-semibold text-brand border-b-2 border-brand"
                                : "text-xl text-gray-600"
                        }`}
                    >
                        {tab === "schedule" ? "Расписание" : "Создать пост"}
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
                        onFileChange={handleFileChange}
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
                        <label className="block mb-2 font-medium">Текст поста</label>
                        <RichEditor
                            emojis={emojis}
                            onChange={({html, text, entities}) => {
                                setEditorHtml(html);
                                setEditorText(text);
                                setEditorEntities(entities);
                                console.log(html);
                                console.log(text);
                                console.log(entities);
                            }}
                        />
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
                    {/* Дата + время */}
                    {scheduleType === "once" ? (
                        <div>
                            <label className="block mb-2 font-medium">Дата и время</label>
                            <DatePicker
                                selected={scheduledAt}
                                onChange={(d) => setScheduledAt(d)}
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
                                onChange={(d) => setTimeOnly(d)}
                                showTimeSelect
                                showTimeSelectOnly
                                timeIntervals={15}
                                dateFormat="HH:mm"
                                placeholderText="Выберите время"
                                className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                            />
                        </div>
                    )}


                    {/* ── Чаты ── */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block font-medium">Чаты для отправки</label>
                            <button
                                onClick={() => setShowAddChatModal(true)}
                                className="text-2xl font-bold text-brand"
                                title="Добавить чат"
                            >
                                +
                            </button>
                        </div>

                        {/* поиск */}
                        <input
                            type="text"
                            placeholder="Поиск чатов..."
                            value={chatSearch}
                            onChange={(e) => setChatSearch(e.target.value)}
                            className="w-full mb-2 border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />

                        {/* список */}
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

                    {/* save */}
                    <button
                        onClick={handleSave}
                        className="w-full py-3 bg-brand text-white rounded-lg shadow hover:bg-brand2 transition"
                    >
                        Сохранить
                    </button>

                    {/* ── Модалка добавления чата ── */}
                    {showAddChatModal && (
                        <div className="fixed inset-0 flex items-center justify-center bg-black/30 z-50">
                            <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full border border-brand">
                                <h3 className="text-lg font-semibold mb-4">Добавить новый чат</h3>
                                <input
                                    type="text"
                                    placeholder="Ссылка-приглашение"
                                    value={newChatLink}
                                    onChange={(e) => setNewChatLink(e.target.value)}
                                    className="w-full mb-4 border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                                />
                                <div className="flex justify-end space-x-4">
                                    <button
                                        onClick={() => setShowAddChatModal(false)}
                                        className="px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100 transition"
                                    >
                                        Отмена
                                    </button>
                                    <button
                                        onClick={handleAddChat}
                                        className="px-4 py-2 bg-brand text-white rounded-md hover:bg-brand2 transition"
                                    >
                                        Добавить
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* ───────── Schedule tab ───────── */}
            {activeTab === "schedule" && (
                <div className="space-y-4 text-brand">
                    {Object.keys(schedule)
                        .sort() // ISO-строки сортируются лексикографически
                        .map((iso) => {
                            const label = new Date(iso).toLocaleDateString("ru-RU", {
                                day: "2-digit",
                                month: "long",
                                year: "numeric",
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
