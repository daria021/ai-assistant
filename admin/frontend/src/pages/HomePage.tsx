// src/pages/HomePage.tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/auth';

export default function HomePage() {
  const navigate = useNavigate();
  const { role, loading, isBanned } = useAuth();

  // Как только загрузился контекст и это обычный менеджер, сразу кидаем в /posts
  useEffect(() => {
    if (!loading && role === 'manager') {
      navigate('/posts');
    }
  }, [loading, role, navigate]);

  if (loading || isBanned) {
    return (
      <div className="container mx-auto flex items-center justify-center h-screen">
        Загрузка…
      </div>
    );
  }


  return (
    <div className="container mx-auto flex flex-col items-center px-4 justify-center h-screen gap-8 bg-brandlight">
      <h1 className="text-3xl text-brand font-bold">Админ Панель ♡</h1>
      <div className="flex flex-col gap-4 w-full max-w-md">
        {role === 'admin' && (
          <>
            <button
              onClick={() => navigate('/accounts')}
              className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
            >
              Управление пользователями
            </button>
            <button
              onClick={() => navigate('/posts')}
              className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
            >
              Расписание постов
            </button>
          </>
        )}

        {role === 'publications_manager' && (
          <>
            <button
              onClick={() => navigate('/chats')}
              className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
            >
              Управление группами
            </button>
            <button
              onClick={() => navigate('/posts')}
              className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
            >
              Расписание постов
            </button>
          </>
        )}
      </div>
    </div>
  );
}
