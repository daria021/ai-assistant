import {useNavigate, useParams} from "react-router-dom";
import {useEffect, useMemo, useRef, useState} from "react";
import FileUploader from "../components/FileUploader";
import DatePicker from "react-datepicker";
// import "react-datepicker/dist/react-datepicker.css";
import {RichEditor, type RichEditorHandle} from "../components/RichEditor";
import type {Emoji, MessageEntityDTO} from "../services/api";
import {
    createPostToPublish,
    getChats,
    getPostToPublish,
    type PostToPublish,
    updatePost,
    updatePostToPublish,
    getChatTypes,
} from "../services/api";
import {useAuth} from "../contexts/auth";
import {on} from "@telegram-apps/sdk";
import {EmojiPicker} from "../components/EmojiPicker";
import {normalizeLineBreaksToDivBr} from "../utils/normalizeHtml";

interface PostDetailsPageProps {
    emojis: Emoji[]
}

export default function PostDetailsPage({emojis}: PostDetailsPageProps) {
    // ...
    const {postToPublishId} = useParams<{ postToPublishId: string }>();
    const navigate = useNavigate();
    const {userId, loading: authLoading} = useAuth();

    console.log('PostDetailsPage render', { postToPublishId, userId, authLoading });

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
    const [chats, setChats] = useState<{ id: string; name: string; chat_type_id?: string | null }[]>([]);
    const [selectedChats, setSelectedChats] = useState<string[]>([]);
    const [chatSearch, setChatSearch] = useState<string>("");
    const [chatTypes, setChatTypes] = useState<{ id: string; name: string }[]>([]);

    const [editorHtml, setEditorHtml] = useState<string>('');
    const [editorText, setEditorText] = useState<string>('');
    const [is_template, setIsTemplate] = useState<boolean>(false);
    const [editorEntities, setEditorEntities] = useState<MessageEntityDTO[]>([]);
    const [pickerOpen, setPickerOpen] = useState(false)
    const richEditorRef = useRef<RichEditorHandle>(null)

    // ↑ твои импорты…
const DEBUG = true;

const dbg = (...args: unknown[]) => {
  if (DEBUG) console.log('[PostDetails]', ...args);
};

const warn = (...args: unknown[]) => {
  if (DEBUG) console.warn('[PostDetails][WARN]', ...args);
};

const errl = (...args: unknown[]) => {
  if (DEBUG) console.error('[PostDetails][ERROR]', ...args);
};

const preview = (s?: string, n = 220) =>
  (s ?? '').replace(/\n/g, '⏎').slice(0, n);

    // const [activeTab, setActiveTab] = useState<"schedule" | "create" | "templates">(
    //     "schedule"
    // );
    // const location = useLocation();
    // type LocationState = { template?: Post; openCreate?: true };
    // const {template, openCreate} = (location.state as LocationState) || {};

    // useEffect(() => {
    //     if (openCreate) setActiveTab("create");
    // }, [openCreate]);

    // загрузить все чаты из API
    useEffect(() => {
        getChats().then(setChats).catch(() => alert("Не удалось загрузить чаты"));
        getChatTypes().then(setChatTypes).catch(() => {});
    }, []);

    const filteredChats = useMemo(
        () =>
            chats.filter((c) =>
                c.name.toLowerCase().includes(chatSearch.trim().toLowerCase())
            ),
        [chatSearch, chats]
    );

    const groupedFilteredChats = useMemo(() => {
        const byType = new Map<string, { id: string; name: string; chat_type_id?: string | null }[]>();
        for (const chat of filteredChats) {
            const typeId = chat.chat_type_id ?? "__none__";
            if (!byType.has(typeId)) byType.set(typeId, []);
            byType.get(typeId)!.push(chat);
        }
        const typeNameById = new Map<string, string>(chatTypes.map(ct => [ct.id, ct.name]));
        const result = Array.from(byType.entries()).map(([typeId, list]) => ({
            typeId,
            typeName: typeId === "__none__" ? "Без группы" : (typeNameById.get(typeId) ?? "Другая группа"),
            chats: list.sort((a, b) => a.name.localeCompare(b.name)),
        }));
        result.sort((a, b) => {
            if (a.typeId === "__none__" && b.typeId !== "__none__") return 1;
            if (a.typeId !== "__none__" && b.typeId === "__none__") return -1;
            return a.typeName.localeCompare(b.typeName);
        });
        return result;
    }, [filteredChats, chatTypes]);

    const toggleChat = (id: string) =>
        setSelectedChats((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );

// Загрузка одной записи PostToPublish (вместе с entry.post и entry.chats)
useEffect(() => {
  if (!postToPublishId) {
    console.warn('PostDetailsPage: postToPublishId is not defined');
    return;
  }
  (async () => {
    console.log('PostDetailsPage: starting data load for postToPublishId:', postToPublishId);
    dbg('route param postToPublishId =', postToPublishId);
    try {
      dbg('getPostToPublish: start', { postToPublishId });
      const e = await getPostToPublish(postToPublishId);
      console.log('PostDetailsPage: getPostToPublish returned:', e);
      dbg('getPostToPublish: OK', {
        id: e?.id,
        hasPost: !!e?.post,
        postId: e?.post?.id,
        chats: e?.chats?.length,
        scheduled_type: e?.scheduled_type,
        scheduled_date: e?.scheduled_date,
        scheduled_time: e?.scheduled_time,
      });

      setEntry(e);
      console.log('PostDetailsPage: entry set to:', e);

      // 1) Поля поста
      setTitle(e.post.name);

const loadedHtml = e.post.html || e.post.text || "";
dbg('loadedHtml (from API)', { length: loadedHtml.length, preview: preview(loadedHtml) });

setEditorHtml(loadedHtml); // ← без normalize тут


      if (loadedHtml && !loadedHtml) {
        warn('Normalizer produced EMPTY html on non-empty input at LOAD phase!');
      }

      setEditorHtml(loadedHtml);
      setEditorText(e.post.text);
      setIsTemplate(e.post.is_template);
      setEditorEntities(e.post.entities || []);

      if (e.post.image_path) setPhotoPreview(e.post.image_path);

      // 2) Тип рассылки и дата/время
      setScheduleType(e.scheduled_type === "single" ? "once" : "daily");
      if (e.scheduled_type === "single" && e.scheduled_date) {
        const dt = new Date(`${e.scheduled_date}T${e.scheduled_time}`);
        dbg('parsed single schedule', { dt: dt.toISOString() });
        setScheduledAt(dt);
      } else {
        const now = new Date();
        const [h, m] = e.scheduled_time.split(":").map(Number);
        now.setHours(h, m, 0, 0);
        dbg('parsed daily schedule (time only)', { h, m });
        setTimeOnly(now);
      }

      // 3) Чаты
      const chatIds = e.chats.map(c => c.id);
      dbg('chats selected', { count: chatIds.length, ids: chatIds });
      setSelectedChats(chatIds);
} catch (error: unknown) {
  if (error instanceof Error) {
    errl('getPostToPublish FAILED', {
      postToPublishId,
      message: error.message,
      stack: error.stack,
    });
  } else {
    errl('getPostToPublish FAILED (non-Error)', error);
  }
  alert("Не удалось загрузить данные для редактирования");
  navigate(-1);
}
  })();
}, [postToPublishId, navigate]);


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
        return `${h}:${m}:00`;          // "HH:mm:ss"
    }

const handleSave = async () => {
  const e = entry;
  const uid = userId;
  console.log('handleSave called', { hasEntry: !!e, hasUserId: !!uid, entry: e, userId: uid });
  if (!e || !uid) {
    errl('handleSave: early return', { hasEntry: !!e, hasUser: !!uid });
    alert(`Ошибка: ${!e ? 'Данные поста не загружены' : ''} ${!uid ? 'Пользователь не авторизован' : ''}`);
    return;
  }

  dbg('handleSave: start', { postToPublishId: e.id, postId: e.post.id });

  // ✳️ нормализуем HTML
  const normalizedHtml = normalizeLineBreaksToDivBr(editorHtml || "");
  const htmlBaseline = e.post.html ?? e.post.text ?? "";
  const entitiesChanged =
    JSON.stringify(editorEntities ?? []) !== JSON.stringify(e.post.entities ?? []);
  const isTemplateChanged = is_template !== e.post.is_template;

  dbg('normalize at SAVE', {
    inputLen: (editorHtml || '').length,
    outputLen: normalizedHtml.length,
    baselineLen: htmlBaseline.length,
    changedFromInput: normalizedHtml !== (editorHtml || ''),
    changedFromBaseline: normalizedHtml !== htmlBaseline,
    inputPreview: preview(editorHtml),
    outputPreview: preview(normalizedHtml),
  });

  try {
    // 1) контент поста — через updatePost
    const willSendHtml = normalizedHtml !== htmlBaseline ? normalizedHtml : undefined;
    dbg('updatePost payload flags', {
      titleChanged: title !== e.post.name,
      isTemplateChanged,
      textChanged: editorText !== e.post.text,
      htmlChanged: !!willSendHtml,
      entitiesChanged,
      photoFile: !!photoFile,
    });

    const upRes = await updatePost(
      e.post.id,
      title !== e.post.name ? title : undefined,
      isTemplateChanged ? is_template : undefined,
      editorText !== e.post.text ? editorText : undefined,
      willSendHtml,
      entitiesChanged ? editorEntities : undefined,
      photoFile ?? undefined
    );
    dbg('updatePost OK', upRes);

    // 2) расписание
    let scheduled_date: string | null = null;
    let scheduled_time: string;

    if (scheduleType === "once" && scheduledAt) {
      scheduled_date = formatLocalDate(scheduledAt);
      scheduled_time = formatLocalTime(scheduledAt);
    } else if (scheduleType === "daily" && timeOnly) {
      scheduled_time = formatLocalTime(timeOnly);
    } else {
      warn('schedule missing', { scheduleType, scheduledAt, timeOnly });
      alert("Выберите дату и время");
      return;
    }

    const payload = {
      post_id: e.post.id,
      manager_id: uid,
      scheduled_type: scheduleType === "once" ? "single" : "everyday",
      scheduled_date,
      scheduled_time,
      chat_ids: selectedChats,
      status: e.status,
    } as const;

    dbg('postToPublish payload', payload);

    if (e.id) {
      const updRes = await updatePostToPublish(e.id, payload);
      dbg('updatePostToPublish OK', updRes);
    } else {
      const crtRes = await createPostToPublish(payload);
      dbg('createPostToPublish OK', crtRes);
    }

    alert("Изменения сохранены");
    navigate(-1);
} catch (error: unknown) {
  if (error instanceof Error) {
    errl('handleSave FAILED', { message: error.message, stack: error.stack });
  } else {
    errl('handleSave FAILED (non-Error)', error);
  }
  alert('Не удалось сохранить изменения');
}

};

    if (authLoading) {
        return <div>Проверка авторизации…</div>;
    }

    if (!userId) {
        return <div>Пользователь не авторизован</div>;
    }

    if (!entry) {
        return <div>Загрузка данных поста…</div>;
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
                <label className="block mb-1 font-medium">Текст поста</label>
                <button
                    type="button"
                    onClick={() => setPickerOpen((o) => !o)}
                    className="ml-2 px-2 py-1 mb-2 rounded hover:bg-gray-200"
                >
                    😊
                </button>
                <RichEditor
  ref={richEditorRef}
  emojis={emojis}
  initialContent={editorHtml}
  onChange={({ html, text, entities }) => {
    dbg('editor.onChange', {
      htmlLen: (html || '').length,
      htmlPreview: preview(html),
      textLen: (text || '').length,
      entities: (entities || []).length,
    });
    setEditorHtml(html);
    setEditorText(text);
    setEditorEntities(entities);
  }}
/>

                {pickerOpen && (

                    <EmojiPicker
                        emojis={emojis}
                        onSelect={(emoji) => {
                            richEditorRef.current?.insertEmoji(emoji)
                            // setPickerOpen(false)
                        }}
                    />
                )}

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
                <div className="max-h-40 overflow-y-auto border p-2 rounded space-y-3">
                    {groupedFilteredChats.map((group) => (
                        <div key={group.typeId}>
                            <div className="px-2 py-1 mb-2 text-xs font-semibold text-gray-700 bg-gray-100 rounded">
                                {group.typeName}
                            </div>
                            <div className="space-y-2">
                                {group.chats.map((c) => (
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
                    ))}
                </div>
            </div>

{/* Сделать шаблоном */}
<div className="mt-2">
  <label className="flex items-center space-x-2">
    <input
      type="checkbox"
      checked={is_template}
      onChange={() => setIsTemplate((prev) => !prev)}
      className="form-checkbox h-5 w-5 text-brand focus:ring-brand"
    />
    <span>Сделать шаблоном</span>
  </label>
</div>
            <div className="flex justify-end">
                <button
                    onClick={handleSave}
                    disabled={!entry || !userId}
                    className="px-5 py-2 bg-brand text-white rounded hover:bg-brand2"
                >
                    Сохранить
                </button>
            </div>
        </div>
    );
}
