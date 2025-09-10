import { useEffect, useState } from "react";
import {
  getChatTypes,
  createChatType,
  deleteChatType,
  getChatsByType,
  createChatByLink, deleteChat,
  updateChatType, updateChat,
} from "../services/api";
import { useAuth } from "../contexts/auth";
import { FiPlus, FiTrash2, FiChevronDown, FiChevronUp, FiCheck, FiX } from "react-icons/fi";
import { on } from "@telegram-apps/sdk";
import { useNavigate } from "react-router-dom";

type ChatType = { id: string; name: string; description: string };
type Chat = { id: string; name: string; invite_link?: string };

export default function ChatTypesControlPage() {
  const { userId } = useAuth();
  const navigate = useNavigate();

  const [types, setTypes] = useState<ChatType[]>([]);
  const [chatsMap, setChatsMap] = useState<Record<string, Chat[]>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const [showTypeModal, setShowTypeModal] = useState(false);
  const [newTypeName, setNewTypeName] = useState("");
  const [newTypeDescription, setNewTypeDescription] = useState("");

  const [showChatModal, setShowChatModal] = useState(false);
  const [newChatLink, setNewChatLink] = useState("");
  const [currentTypeForChat, setCurrentTypeForChat] = useState<string | null>(null);
  const [highlightChatId, setHighlightChatId] = useState<string | null>(null);

  // inline-редактирование названия группы
  const [editingTypeId, setEditingTypeId] = useState<string | null>(null);
  const [editingTypeName, setEditingTypeName] = useState("");

  // подсветка зоны дропа
  const [dragOverTypeId, setDragOverTypeId] = useState<string | null>(null);

  useEffect(() => {
    loadTypes();
  }, []);

  useEffect(() => {
    return on("back_button_pressed", () => navigate(-1));
  }, [navigate]);

  async function loadTypes() {
    const data = await getChatTypes();
    setTypes(data);
    data.forEach((t) => loadChats(t.id));
  }

  async function loadChats(typeId: string) {
    const data = await getChatsByType(typeId);
    setChatsMap((prev) => ({ ...prev, [typeId]: data }));
  }

  async function handleCreateType() {
    if (!newTypeName.trim()) return;
    await createChatType({
      name: newTypeName.trim(),
      description: newTypeDescription.trim(),
    });
    setShowTypeModal(false);
    setNewTypeName("");
    setNewTypeDescription("");
    loadTypes();
  }

  async function handleDeleteType(id: string) {
    if (!window.confirm("Удалить этот вид чатов?")) return;
    await deleteChatType(id);
    loadTypes();
  }

  function toggleExpand(typeId: string) {
    setExpanded((prev) => ({ ...prev, [typeId]: !prev[typeId] }));
  }

  function openAddChat(typeId: string) {
    setCurrentTypeForChat(typeId);
    setNewChatLink("");
    setShowChatModal(true);
  }

  // Нормализация инвайта: убираем @, http/https, префикс t.me/, завершающий слэш, lower-case
  function normalizeInvite(s?: string): string {
    if (!s) return "";
    let v = s.trim();
    if (v.startsWith("@")) v = v.slice(1);
    v = v.replace(/^https?:\/\//i, "");
    v = v.replace(/^t\.me\//i, "");
    if (v.endsWith("/")) v = v.slice(0, -1);
    return v.toLowerCase();
  }

  // Поиск и подсветка существующего чата по нормализованному ключу
  async function findAndHighlightByInviteKey(targetKey: string): Promise<boolean> {
    // 1) Пытаемся найти в уже загруженных списках
    let found: { typeId: string; chat: Chat } | null = null;
    for (const [typeId, list] of Object.entries(chatsMap)) {
      const hit = (list || []).find(c => normalizeInvite(c.invite_link) === targetKey);
      if (hit) { found = { typeId, chat: hit }; break; }
    }

    const expandAndHighlight = (typeId: string, chatId: string) => {
      setExpanded(prev => ({ ...prev, [typeId]: true }));
      setShowChatModal(false);
      setTimeout(() => {
        setHighlightChatId(chatId);
        requestAnimationFrame(() => {
          const el = document.querySelector(`[data-chat-id="${chatId}"]`);
          if (el && 'scrollIntoView' in el) (el as any).scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
        setTimeout(() => setHighlightChatId(null), 2000);
      }, 100);
    };

    if (found) { expandAndHighlight(found.typeId, found.chat.id); return true; }

    // 2) Обновляем данные и пробуем ещё раз
    const typesData = await getChatTypes();
    setTypes(typesData);
    for (const t of typesData) {
      const data = await getChatsByType(t.id);
      setChatsMap(prev => ({ ...prev, [t.id]: data }));
      const hit = data.find(c => normalizeInvite(c.invite_link) === targetKey);
      if (hit) { expandAndHighlight(t.id, hit.id); return true; }
    }
    return false;
  }

  async function handleAddChat() {
    if (!newChatLink.trim() || !currentTypeForChat) return;
    try {
      const raw = newChatLink.trim();
      const normalizedForRequest = raw.startsWith("@") ? raw.slice(1) : raw;
      const chat = await createChatByLink({
        invite_link: normalizedForRequest,
        chat_type_id: currentTypeForChat,
        manager_id: userId!,
      });
      setChatsMap((prev) => ({
        ...prev,
        [currentTypeForChat]: [...(prev[currentTypeForChat] || []), chat],
      }));
      setShowChatModal(false);
    } catch (err: any) {
      const status = err?.response?.status ?? err?.status;
      // 1) Если бэкенд вернул id и chat_type_id — подсветим по ним сразу
      const byId = err?.response?.data;
      if (status === 409 && byId?.id && byId?.chat_type_id) {
        setExpanded(prev => ({ ...prev, [byId.chat_type_id]: true }));
        setShowChatModal(false);
        setTimeout(() => {
          setHighlightChatId(byId.id);
          requestAnimationFrame(() => {
            const el = document.querySelector(`[data-chat-id="${byId.id}"]`);
            if (el && 'scrollIntoView' in el) (el as any).scrollIntoView({ behavior: 'smooth', block: 'center' });
          });
          setTimeout(() => setHighlightChatId(null), 2000);
        }, 100);
        alert("Такой чат уже существует. Вот он в списке.");
      } else {
        // 2) Фолбэк: ищем по нормализованной ссылке
        const key = normalizeInvite(newChatLink);
        const highlighted = await findAndHighlightByInviteKey(key);
        if (highlighted || status === 409) {
          alert("Такой чат уже существует. Вот он в списке.");
        } else {
          alert("Не удалось добавить чат.");
        }
        setShowChatModal(false);
      }
    }
  }

  async function handleRemoveChat(chatId: string) {
    await deleteChat(chatId);
    loadTypes()
  }

  // сохранить новое имя группы
  async function handleSaveTypeName(typeId: string) {
    const name = editingTypeName.trim();
    if (!name) {
      // пустое значение — просто выйти из режима редактирования, не отправляя PATCH
      setEditingTypeId(null);
      setEditingTypeName("");
      return;
    }
    await updateChatType(typeId, { name });
    setEditingTypeId(null);
    setEditingTypeName("");
    await loadTypes();
  }

  // DnD: начало перетаскивания чата
  function onChatDragStart(e: React.DragEvent, chatId: string, fromTypeId: string) {
    e.dataTransfer.setData("text/plain", JSON.stringify({ chatId, fromTypeId }));
    e.dataTransfer.effectAllowed = "move";
  }

  // DnD: сюда можно бросать
  function onGroupDragOver(e: React.DragEvent, typeId: string) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    setDragOverTypeId(typeId);
  }

  // DnD: обработка сброса в группу typeId
  async function onGroupDrop(e: React.DragEvent, toTypeId: string) {
    e.preventDefault();
    try {
      const data = JSON.parse(e.dataTransfer.getData("text/plain")) as { chatId: string; fromTypeId: string };
      if (!data?.chatId) return;
      if (data.fromTypeId === toTypeId) return;
      await updateChat(data.chatId, { chat_type_id: toTypeId });
      // обновляем обе группы
      await Promise.all([loadChats(data.fromTypeId), loadChats(toTypeId)]);
    } catch (err) {
      // noop
    }
    setDragOverTypeId(null);
  }

  return (
    <div className="p-4 bg-brandlight min-h-screen space-y-6">
      {/* Сами группы чатов */}
      {types.map((type) => (
        <div
          key={type.id}
          className={`bg-brand-pink rounded-2xl p-4 shadow-lg ${dragOverTypeId === type.id ? 'ring-2 ring-brand' : ''}`}
          onDragOver={(e) => onGroupDragOver(e, type.id)}
          onDragLeave={() => setDragOverTypeId((prev) => (prev === type.id ? null : prev))}
          onDrop={(e) => onGroupDrop(e, type.id)}
        >
          <div
            className="flex justify-between items-center cursor-pointer"
            onClick={() => toggleExpand(type.id)}
          >
            <div className="flex-1 min-w-0">
              {editingTypeId === type.id ? (
                <div className="flex items-start gap-2" onClick={(e) => e.stopPropagation()}>
                  <div className="flex-1 min-w-0">
                    <input
                      value={editingTypeName}
                      onChange={(e) => setEditingTypeName(e.target.value)}
                      className="w-full border rounded px-2 py-1"
                      autoFocus
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleSaveTypeName(type.id);
                        } else if (e.key === 'Escape') {
                          setEditingTypeId(null);
                          setEditingTypeName("");
                        }
                      }}
                      onBlur={() => handleSaveTypeName(type.id)}
                      placeholder="Название группы"
                    />
                    <div className="mt-1 text-xs text-gray-500">Enter — сохранить, Esc — отменить</div>
                  </div>
                  <button
                    onClick={() => handleSaveTypeName(type.id)}
                    className="p-2 rounded-full hover:bg-white/70 border border-transparent hover:border-brand"
                    title="Сохранить"
                    aria-label="Сохранить"
                  >
                    <FiCheck className="text-green-600" />
                  </button>
                  <button
                    onClick={() => { setEditingTypeId(null); setEditingTypeName(""); }}
                    className="p-2 rounded-full hover:bg-white/70 border border-transparent hover:border-brand"
                    title="Отменить"
                    aria-label="Отменить"
                  >
                    <FiX className="text-red-600" />
                  </button>
                </div>
              ) : (
                <div>
                  <h2
                    className="text-lg font-medium truncate hover:underline cursor-text"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditingTypeId(type.id);
                      setEditingTypeName(type.name);
                    }}
                    title="Нажмите, чтобы отредактировать"
                  >
                    {type.name}
                  </h2>
                  <p className="text-sm text-gray-700 truncate">{type.description}</p>
                </div>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  openAddChat(type.id);
                }}
                className="p-2 bg-brandlight rounded-full shadow"
                title="Добавить чат"
              >
                <FiPlus className="text-xl text-brand-pink" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteType(type.id);
                }}
                className="p-2 bg-brandlight rounded-full shadow"
                title="Удалить группу"
              >
                <FiTrash2 className="text-xl text-red-500" />
              </button>
              {expanded[type.id] ? (
                <FiChevronUp className="text-xl" />
              ) : (
                <FiChevronDown className="text-xl" />
              )}
            </div>
          </div>

          {expanded[type.id] && (
            <ul className="mt-4 space-y-2">
              {chatsMap[type.id]?.length ? (
                chatsMap[type.id].map((chat) => (
                  <li
                    key={chat.id}
                    className={`flex justify-between items-center rounded-xl p-3 shadow ${highlightChatId === chat.id ? 'bg-blue-100 ring-2 ring-blue-300' : 'bg-white'}`}
                    draggable
                    onDragStart={(e) => onChatDragStart(e, chat.id, type.id)}
                    data-chat-id={chat.id}
                  >
                    <span className="truncate mr-3">{chat.name}</span>
                    <div className="flex items-center gap-2">
                      <select
                        className="border rounded px-2 py-1 text-sm"
                        value={type.id}
                        onChange={async (e) => {
                          const toTypeId = e.target.value;
                          if (toTypeId && toTypeId !== type.id) {
                            await updateChat(chat.id, { chat_type_id: toTypeId });
                            await Promise.all([loadChats(type.id), loadChats(toTypeId)]);
                          }
                        }}
                      >
                        {types.map(t => (
                          <option key={t.id} value={t.id}>{t.name}</option>
                        ))}
                      </select>
                      <FiTrash2
                        onClick={() => handleRemoveChat(chat.id)}
                        className="text-red-500 cursor-pointer"
                      />
                    </div>
                  </li>
                ))
              ) : (
                <li className="text-gray-600 italic">Чатов нет — перетащите сюда из другой группы</li>
              )}
            </ul>
          )}
        </div>
      ))}

      {/* Кнопка «+» для создания новой группы чатов */}
      <div className="flex justify-center">
        <button
          onClick={() => setShowTypeModal(true)}
          className="p-3 bg-brand-pink text-brandlight rounded-full shadow-lg"
          title="Добавить группу чатов"
        >
          <FiPlus size={24} />
        </button>
      </div>

      {/* Модалка создания новой группы чатов */}
      {showTypeModal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-2xl shadow-lg w-96">
            <h3 className="text-xl font-semibold mb-4">Новая группа чатов</h3>
            <input
              type="text"
              placeholder="Название"
              value={newTypeName}
              onChange={(e) => setNewTypeName(e.target.value)}
              className="w-full mb-2 p-2 border rounded-lg"
            />
            <textarea
              placeholder="Описание"
              value={newTypeDescription}
              onChange={(e) => setNewTypeDescription(e.target.value)}
              className="w-full mb-4 p-2 border rounded-lg"
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowTypeModal(false)}
                className="px-4 py-2 rounded-lg"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateType}
                className="px-4 py-2 bg-brand-pink text-black rounded-lg"
              >
                Создать
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модалка добавления чата в выбранную группу */}
      {showChatModal && currentTypeForChat && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-2xl shadow-lg w-96">
            <h3 className="text-xl font-semibold mb-4">Добавить чат</h3>
            <input
              type="text"
              placeholder="Ссылка-приглашение"
              value={newChatLink}
              onChange={(e) => setNewChatLink(e.target.value)}
              className="w-full mb-4 p-2 border rounded-lg"
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowChatModal(false)}
                className="px-4 py-2 rounded-lg"
              >
                Отмена
              </button>
              {(() => {
                const canAdd = !!newChatLink.trim();
                const className = canAdd
                  ? "px-4 py-2 rounded-lg bg-brand text-white hover:bg-brand2 transition"
                  : "px-4 py-2 rounded-lg bg-gray-300 text-gray-600 cursor-not-allowed";
                return (
                  <button
                    onClick={handleAddChat}
                    className={className}
                    disabled={!canAdd}
                    title={canAdd ? "Добавить чат" : "Введите ссылку"}
                  >
                    Добавить
                  </button>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
