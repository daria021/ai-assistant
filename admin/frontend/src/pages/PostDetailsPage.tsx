// src/pages/PostDetailsPage.tsx
import {useNavigate, useParams} from "react-router-dom";
import {useEffect, useMemo, useState} from "react";
import FileUploader from "../components/FileUploader";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import {RichEditor} from "../components/RichEditor";
import type {Emoji, MessageEntityDTO} from "../services/api";
import {
    getChats,
    getPostToPublish,
    type PostToPublish,
    updatePost,
    updatePostToPublish,
} from "../services/api";
import {useAuth} from "../contexts/auth";
import {on} from "@telegram-apps/sdk";

interface PostDetailsPageProps {
    emojis: Emoji[]
}

export default function PostDetailsPage({emojis}: PostDetailsPageProps) {
    // ...
    const {postToPublishId} = useParams<{ postToPublishId: string }>();
    const navigate = useNavigate();
    const {userId} = useAuth();

    // форма самого поста
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string>("/default-photo.png");
    const [title, setTitle] = useState<string>("");

    // расписание
    const [entry, setEntry] = useState<PostToPublish | null>(null);
    const [scheduleType, setScheduleType] = useState<"once" | "daily">("once");
    const [scheduledAt, setScheduledAt] = useState<Date | null>(null);
    const [timeOnly, setTimeOnly] = useState<Date | null>(null);

    // чаты
    const [chats, setChats] = useState<{ id: string; name: string }[]>([]);
    const [selectedChats, setSelectedChats] = useState<string[]>([]);
    const [chatSearch, setChatSearch] = useState<string>("");

    const [editorHtml, setEditorHtml] = useState<string>('');
    const [editorText, setEditorText] = useState<string>('');
    const [editorEntities, setEditorEntities] = useState<MessageEntityDTO[]>([]);




    // загрузить все чаты из API
    useEffect(() => {
        getChats().then(setChats).catch(() => alert("Не удалось загрузить чаты"));
    }, []);

    const filteredChats = useMemo(
        () =>
            chats.filter((c) =>
                c.name.toLowerCase().includes(chatSearch.trim().toLowerCase())
            ),
        [chatSearch, chats]
    );
    const toggleChat = (id: string) =>
        setSelectedChats((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );

    // Загрузка одной записи PostToPublish (вместе с entry.post и entry.chats)
    useEffect(() => {
        if (!postToPublishId) return;
        (async () => {
            try {
                const e = await getPostToPublish(postToPublishId);
                setEntry(e);

                // 1) Заполняем поля поста из вложенного entry.post
                setTitle(e.post.name);
                setEditorHtml(e.post.html || e.post.text); // если бекенд хранит HTML
                setEditorText(e.post.text);
                setEditorEntities(e.post.entities || []);

                if (e.post.image_path) setPhotoPreview(e.post.image_path);

                // 2) Тип рассылки и дата/время
                setScheduleType(e.scheduled_type === "single" ? "once" : "daily");
                if (e.scheduled_type === "single" && e.scheduled_date) {
                    setScheduledAt(
                        new Date(`${e.scheduled_date}T${e.scheduled_time}`)
                    );
                } else {
                    const now = new Date();
                    const [h, m] = e.scheduled_time.split(":").map(Number);
                    now.setHours(h, m, 0, 0);
                    setTimeOnly(now);
                }

                // 3) Отмечаем чаты из entry.chats (список объектов Chat)
                setSelectedChats(e.chats.map((c) => c.id));
            } catch {
                alert("Не удалось загрузить данные для редактирования");
                navigate(-1);
            }
        })();
    }, [postToPublishId, navigate]);

    // кнопка «назад» в телеге
    useEffect(() => {
        return on("back_button_pressed", () => navigate(-1));
    }, [navigate]);

    function formatLocalDate(d: Date): string {
      const Y = d.getFullYear();
      const M = String(d.getMonth() + 1).padStart(2, "0");
      const D = String(d.getDate()).padStart(2, "0");
      return `${Y}-${M}-${D}`;        // "YYYY-MM-DD"
    }

    function formatLocalTime(d: Date): string {
      const h = String(d.getHours()).padStart(2, "0");
      const m = String(d.getMinutes()).padStart(2, "0");
      return `${h}:${m}`;             // "HH:mm"
        }
    const handleSave = async () => {
      if (!entry || !userId) return;

      // 1) Обновляем содержимое поста
      await updatePost(
        entry.post.id,
        title !== entry.post.name ? title : null,
        editorText !== entry.post.text ? editorText : null,
        editorHtml !== entry.post.html ? editorHtml : null,
        editorEntities !== entry.post.entities ? editorEntities : null,
        photoFile ?? null
      );

      // 2) Готовим поля расписания
      let scheduled_date: string | null = null;
      let scheduled_time: string;

      if (scheduleType === "once" && scheduledAt) {
        scheduled_date = formatLocalDate(scheduledAt);   // "YYYY-MM-DD" локально
        scheduled_time = formatLocalTime(scheduledAt);   // "HH:mm" локально
      } else if (scheduleType === "daily" && timeOnly) {
        scheduled_time = formatLocalTime(timeOnly);      // "HH:mm" локально
      } else {
        alert("Выберите дату и время");
        return;
      }

  // 3) Обновляем запись в расписании через API
  await updatePostToPublish(entry.id, {
    post_id: entry.post.id,
    manager_id: userId,
    scheduled_type: scheduleType === "once" ? "single" : "everyday",
    scheduled_date,
    scheduled_time,
    chat_ids: selectedChats,
    status: entry.status,
  });

  alert("Изменения сохранены");
  navigate(-1);
};

    if (!entry) {
        return <div>Загрузка…</div>;
    }
    return (
        <div className="container mx-auto p-4 bg-brandlight min-h-screen relative">
            <h1 className="text-2xl font-semibold mb-6">
                Редактирование поста
            </h1>

            {/* Фото */}
            <FileUploader
                label="Фото поста"
                file={photoFile}
                preview={photoPreview}
                onFileChange={setPhotoFile}
            />

            {/* Название */}
            <div className="mb-4">
                <label className="block mb-1 font-medium">Название</label>
                <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full border border-brand rounded p-2"
                />
            </div>

            {/* Текст */}
            <div className="mb-4">
                <label className="block mb-1 font-medium">Текст</label>
                <RichEditor
                    emojis={emojis}
                    initialContent={editorHtml}
                    onChange={({html, text, entities}) => {
                        setEditorHtml(html);
                        setEditorText(text);
                        setEditorEntities(entities);
                    }}
                />

            </div>

            {/* Расписание */}
            <div className="mb-4">
                <label className="block mb-1 font-medium">
                    Тип рассылки
                </label>
                <div className="flex space-x-4">
                    <label className="flex items-center space-x-2">
                        <input
                            type="radio"
                            checked={scheduleType === "once"}
                            onChange={() => setScheduleType("once")}
                            className="form-radio"
                        />
                        <span>В указанный день</span>
                    </label>
                    <label className="flex items-center space-x-2">
                        <input
                            type="radio"
                            checked={scheduleType === "daily"}
                            onChange={() => setScheduleType("daily")}
                            className="form-radio"
                        />
                        <span>Каждый день</span>
                    </label>
                </div>
            </div>

            {scheduleType === "once" ? (
                <DatePicker
                    selected={scheduledAt}
                    onChange={setScheduledAt}
                    showTimeSelect
                    dateFormat="dd.MM.yyyy HH:mm"
                    className="w-full border p-2 mb-4"
                />
            ) : (
                <DatePicker
                    selected={timeOnly}
                    onChange={setTimeOnly}
                    showTimeSelectOnly
                    dateFormat="HH:mm"
                    className="w-full border p-2 mb-4"
                />
            )}

            {/* Чаты */}
            <div className="mb-6">
                <label className="block mb-1 font-medium">
                    Чаты для отправки
                </label>
                <input
                    type="text"
                    placeholder="Поиск..."
                    value={chatSearch}
                    onChange={(e) => setChatSearch(e.target.value)}
                    className="w-full border p-2 mb-2"
                />
                <div className="max-h-40 overflow-y-auto border p-2 rounded">
                    {filteredChats.map((c) => (
                        <label
                            key={c.id}
                            className="flex items-center space-x-2 mb-1"
                        >
                            <input
                                type="checkbox"
                                checked={selectedChats.includes(c.id)}
                                onChange={() => toggleChat(c.id)}
                                className="form-checkbox"
                            />
                            <span>{c.name}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="flex justify-end">
                <button
                    onClick={handleSave}
                    className="px-5 py-2 bg-brand text-white rounded hover:bg-brand2"
                >
                    Сохранить
                </button>
            </div>
        </div>
    );
}
