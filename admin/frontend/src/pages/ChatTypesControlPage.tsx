import { useEffect, useState } from "react";
import {
  getChatTypes,
  createChatType,
  deleteChatType,
  getChatsByType,
  updateChat,
  createChatByLink,
} from "../services/api";
import { useAuth } from "../contexts/auth";
import { FiPlus, FiTrash2, FiChevronDown, FiChevronUp } from "react-icons/fi";
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

  async function handleAddChat() {
    if (!newChatLink.trim() || !currentTypeForChat) return;
    try {
      const chat = await createChatByLink({
        invite_link: newChatLink.trim(),
        chat_type_id: currentTypeForChat,
        manager_id: userId!,
      });
      setChatsMap((prev) => ({
        ...prev,
        [currentTypeForChat]: [...(prev[currentTypeForChat] || []), chat],
      }));
      setShowChatModal(false);
    } catch {
      alert("Не удалось добавить чат.");
    }
  }

  async function handleRemoveChat(chatId: string) {
    await updateChat(chatId, { chat_type_id: null });
    loadTypes()
  }

  return (
    <div className="p-4 bg-brandlight min-h-screen space-y-6">
      {/* Сами группы чатов */}
      {types.map((type) => (
        <div key={type.id} className="bg-brand-pink rounded-2xl p-4 shadow-lg">
          <div
            className="flex justify-between items-center cursor-pointer"
            onClick={() => toggleExpand(type.id)}
          >
            <div>
              <h2 className="text-lg font-medium">{type.name}</h2>
              <p className="text-sm text-gray-700">{type.description}</p>
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
                    className="flex justify-between items-center bg-white rounded-xl p-3 shadow"
                  >
                    <span>{chat.name}</span>
                    <FiTrash2
                      onClick={() => handleRemoveChat(chat.id)}
                      className="text-red-500 cursor-pointer"
                    />
                  </li>
                ))
              ) : (
                <li className="text-gray-600 italic">Чатов нет</li>
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
              <button
                onClick={handleAddChat}
                className="px-4 py-2 bg-brand-pink text-white rounded-lg"
              >
                Добавить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
