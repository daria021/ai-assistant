import { useEffect, useState } from 'react';
import { on } from '@telegram-apps/sdk';
import { useNavigate } from 'react-router-dom';
import {
  getAuthCode,
  getUsers,
  sendAuthCode, updateUser,
  type User as APIUser,
} from '../services/api';
import { AxiosError } from 'axios';
import type {UserRole} from "../types/UserRole";

const roles: UserRole[] = ['admin', 'manager', 'publications_manager'];

const STATUS_LABELS: Record<UserRole, string> = {
  admin: 'Админ',
  manager: 'Менеджер',
  publications_manager: 'Менеджер по постам',
  banned: 'Забанен',
};

export default function AccountsControlPage() {
  const [accounts, setAccounts] = useState<APIUser[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [step, setStep] = useState<'form' | 'code'>('form');
  const [phone, setPhone] = useState('');
  const [cloudPassword, setCloudPassword] = useState('');
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [proxyError, setProxyError] = useState(false);
  const [roleUpdatingId, setRoleUpdatingId] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchAccounts = async () => {
    try {
      const users = await getUsers(); // APIUser[]
      setAccounts(users);
    } catch (e) {
      console.error('Не удалось получить пользователей', e);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  // Обработчик системной кнопки назад
  useEffect(() => {
    const off = on('back_button_pressed', () => navigate(-1));
    return () => off();
  }, [navigate]);

  const closeModal = () => {
    setIsModalOpen(false);
    setIsLoading(false);
    setError('');
    setProxyError(false);
  };

  const openModal = () => {
    setIsModalOpen(true);
    setStep('form');
    setError('');
    setPhone('');
    setCloudPassword('');
    setCode('');
    setProxyError(false);
  };

  // Отправка кода SMS
  const handleSendCode = async () => {
    if (!phone) return setError('Введите телефон');
    setIsLoading(true);
    setError('');
    setProxyError(false);
    try {
      await getAuthCode(phone);
      setStep('code');
    } catch (e: unknown) {
      if (e instanceof AxiosError && e.response?.status === 503) {
        closeModal();
        setProxyError(true);
      } else {
        console.error(e);
        setError('Не удалось отправить код. Попробуйте снова.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Подтверждение кода SMS
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

// Смена роли через updateUser
  const handleRoleChange = async (userId: string, newRole: UserRole) => {
    setRoleUpdatingId(userId);
    try {
      const updated = await updateUser(userId, { role: newRole });
      setAccounts(prev =>
        prev.map(u => (u.id === userId ? updated : u))
      );
    } catch (e) {
      console.error('Ошибка при смене роли', e);
      alert('Не удалось сохранить роль');
    } finally {
      setRoleUpdatingId(null);
    }
  };

  // Бан/разбан через updateUser
  const handleToggleBan = async (userId: string, currentIsBanned: boolean) => {
    setRoleUpdatingId(userId);
    try {
      const updated = await updateUser(userId, { is_banned: !currentIsBanned });
      setAccounts(prev =>
        prev.map(u => (u.id === userId ? updated : u))
      );
    } catch (e) {
      console.error('Ошибка при обновлении бана', e);
      alert('Не удалось обновить статус бана');
    } finally {
      setRoleUpdatingId(null);
    }
  };

  return (
    <div className="container mx-auto p-6 bg-brandlight min-h-screen">
      <h1 className="text-2xl text-center font-bold text-brand mb-8">
        Управление аккаунтами
      </h1>

      {proxyError && (
        <div className="max-w-lg mx-auto mb-6 bg-red-100 border border-red-500 px-4 py-3 rounded-lg shadow">
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

<div className="space-y-3">
  {accounts.map((u) => (
    <div
      key={u.id}
      className="bg-white rounded-lg shadow p-2 flex items-center"
    >
      {/* Ник */}
      <div className="flex-1 min-w-0">
        <h2 className="text-base font-semibold text-brand truncate">
          {u.telegram_username || u.id}
        </h2>
      </div>

      {/* Селект сверху + кнопка снизу, прижато вправо */}
      <div className="flex-shrink-0 ml-auto flex flex-col items-end gap-1">
        <select
          value={u.role}
          onChange={(e) => handleRoleChange(u.id, e.target.value as UserRole)}
          disabled={roleUpdatingId === u.id}
          className="
            appearance-none w-32
            py-1 px-2 text-sm
            bg-white border border-gray-300
            rounded focus:outline-none focus:ring-1 focus:ring-brand
            cursor-pointer
          "
        >
          {roles.map((r) => (
            <option key={r} value={r}>
              {STATUS_LABELS[r]}
            </option>
          ))}
        </select>

        <button
          onClick={() => handleToggleBan(u.id, u.is_banned)}
          disabled={roleUpdatingId === u.id}
          className={`
            w-32 py-1 text-sm rounded font-medium disabled:opacity-50 focus:outline-none
            ${u.is_banned
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'}
          `}
        >
          {u.is_banned ? 'Разбанить' : 'Забанить'}
        </button>
      </div>
    </div>
  ))}
</div>

      {/* Модалка подключения нового аккаунта */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md relative">
            <button
              onClick={closeModal}
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
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
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full mb-4 p-2 border rounded focus:ring-2 focus:ring-brand"
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
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full mb-3 p-2 border rounded focus:ring-2 focus:ring-brand"
                />
                <input
                  type="password"
                  placeholder="Облачный пароль (необязательно)"
                  value={cloudPassword}
                  onChange={(e) => setCloudPassword(e.target.value)}
                  className="w-full mb-4 p-2 border rounded focus:ring-2 focus:ring-brand"
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
