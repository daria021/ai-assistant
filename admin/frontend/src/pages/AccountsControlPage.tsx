import { useEffect, useState } from 'react';
import { FiTrash2 } from 'react-icons/fi';
import { on } from '@telegram-apps/sdk';
import { useNavigate } from 'react-router-dom';
import { deleteUser, getAuthCode, getUsers, sendAuthCode } from '../services/api';
import type { UserRole } from "../types/UserRole";
import { AxiosError } from "axios";

const roles = ['admin', 'moderator1', 'moderator2'] as const;
type Role = typeof roles[number];

interface Account {
  userId: string;
  username: string;
  role: Role;
}

export interface User {
  id: string;             // UUID
  telegram_username: string;
  role: UserRole;
}

export default function AccountsControlPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [step, setStep] = useState<'form' | 'code'>('form');
  const [phone, setPhone] = useState('');
  const [cloudPassword, setCloudPassword] = useState('');
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [proxyError, setProxyError] = useState(false);
  const navigate = useNavigate();

  const openModal = () => {
    setIsModalOpen(true);
    setStep('form');
    setError('');
    setPhone('');
    setCloudPassword('');
    setCode('');
    setProxyError(false);
  };

  const fetchAccounts = async () => {
          try {
        const users: User[] = await getUsers();
        const mapped: Account[] = users.map(u => ({
          userId: u.id,
          username: u.telegram_username || u.id, // Если username отсутствует — показываем ID
          role: u.role as Role
        }));
        setAccounts(mapped);
      } catch (e) {
        console.error('Не удалось получить пользователей', e);
      }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const closeModal = () => {
    setIsModalOpen(false);
    setIsLoading(false);
    setError('');
    setProxyError(false);
  };

const handleSendCode = async () => {
  if (!phone) return setError('Введите телефон');
  setIsLoading(true);
  setError('');
  setProxyError(false);
  try {
    await getAuthCode(phone);
    setStep('code');
  } catch (e: unknown) {
    console.error(e);
    // Если получили 503 — «нет свободного прокси», закрываем модалку и показываем плашку
    if (
      typeof e === 'object' &&
      e !== null &&
      'response' in e &&
      (e as AxiosError).response?.status === 503
    ) {
      // Закроем окно «Новый аккаунт»
      closeModal();
      // Поднимем флаг proxyError, чтобы отрисовалась плашка
      setProxyError(true);
    } else {
      setError('Не удалось отправить код. Попробуйте снова.');
    }
  } finally {
    setIsLoading(false);
  }
};

  const handleConfirmCode = async () => {
    if (!code) return setError('Введите код подтверждения');
    setIsLoading(true);
    setError('');
    try {
      await sendAuthCode(phone, code, cloudPassword);
      alert('Ваш аккаунт подключен!');
      closeModal();
      await fetchAccounts();
    } catch (e) {
      console.error(e);
      setError('Ошибка подтверждения. Проверьте код и пароль.');
    } finally {
      setIsLoading(false);
    }
  };

  const changeRole = (userId: string, newRole: Role) => {
    setAccounts(prev =>
      prev.map(acc => acc.userId === userId ? { ...acc, role: newRole } : acc)
    );
  };

  const deleteAccount = async (userId: string, username: string) => {
    if (!confirm(`Удалить ${username}?`)) return;

    try {
      await deleteUser(userId);
      setAccounts(prev => prev.filter(acc => acc.userId !== userId));
    } catch (e) {
      console.error('Ошибка при удалении пользователя', e);
      alert('Не удалось удалить пользователя. Попробуйте ещё раз.');
    }
  };

  useEffect(() => {
    const removeBackListener = on('back_button_pressed', () => navigate(-1));
    return () => removeBackListener();
  }, [navigate]);

  return (
    <div className="container mx-auto p-6 bg-brandlight min-h-screen">
      <h1 className="text-2xl text-center font-bold text-brand mb-8">Управление аккаунтами</h1>

      {proxyError && (
        <div className="max-w-lg mx-auto mb-6 bg-red-100 border border-red-500 text-black px-4 py-3 rounded-lg shadow">
          Нет свободного прокси сервера. Он нужен, чтобы аккаунт не забанили. Необходимо добавить новый прокси сервер.
        </div>
      )}

      <div className="flex justify-center mb-8">
        <button
          onClick={openModal}
          className="px-6 py-3 border-2 border-brand text-brand bg-white rounded-lg hover:bg-brandlight transition"
        >
          Подключить аккаунт
        </button>
      </div>

      <h2 className="text-center mb-2">─── ⋆⋅☆⋅⋆ ──</h2>

      {/* Список аккаунтов */}
      <div className="space-y-4">
        {accounts.map(acc => (
          <div
            key={acc.username} // используем username как key
            className="bg-white rounded-lg shadow p-4 flex items-center justify-between"
          >
            <div>
              {/* Показываем telegram_username (или, если его нет, userId) */}
              <div className="font-medium text-brand">{acc.username}</div>
              <select
                value={acc.role}
                onChange={e => changeRole(acc.userId, e.target.value as Role)}
                className="mt-1 bg-brandlight border border-brand px-2 py-1 rounded focus:ring-2 focus:ring-brand"
              >
                {roles.map(r => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={() => deleteAccount(acc.userId, acc.username)}
              className="text-red-500 hover:text-red-700"
              title="Удалить аккаунт"
            >
              <FiTrash2 size={20} />
            </button>
          </div>
        ))}
      </div>

      {/* Модалка для подключения аккаунта */}
      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md relative">
            <button
              onClick={closeModal}
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
              title="Закрыть"
            >
              ✕
            </button>

            {step === 'form' ? (
              <>
                <h2 className="text-xl font-semibold mb-4">Новый аккаунт</h2>
                <input
                  type="tel"
                  placeholder="Телефон"
                  value={phone}
                  onChange={e => setPhone(e.target.value)}
                  className="w-full mb-4 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-brand"
                />
                <button
                  onClick={handleSendCode}
                  disabled={isLoading}
                  className="w-full py-2 bg-brand text-white rounded hover:bg-brand transition disabled:opacity-50"
                >
                  {isLoading ? 'Отправка...' : 'Получить код'}
                </button>
              </>
            ) : (
              <>
                <h2 className="text-xl font-semibold mb-4">Код подтверждения</h2>
                <input
                  type="text"
                  placeholder="Код из Telegram"
                  value={code}
                  onChange={e => setCode(e.target.value)}
                  className="w-full mb-3 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-brand"
                />
                <input
                  type="password"
                  placeholder="Облачный пароль (необязательно)"
                  value={cloudPassword}
                  onChange={e => setCloudPassword(e.target.value)}
                  className="w-full mb-4 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-brand"
                />
                <button
                  onClick={handleConfirmCode}
                  disabled={isLoading}
                  className="w-full py-2 bg-brand text-white rounded hover:bg-brand transition disabled:opacity-50"
                >
                  {isLoading ? 'Подключение...' : 'Подключить'}
                </button>
              </>
            )}

            {error && <div className="text-red-500 mt-3">{error}</div>}
          </div>
        </div>
      )}
    </div>
  );
}
