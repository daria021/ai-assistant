import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {getPosts, updatePost} from '../services/api';
import {on} from "@telegram-apps/sdk";

export interface MessageEntityDTO {
  type: "custom_emoji" | "bold" | "italic" | "underline";
  offset: number;
  length: number;
  custom_emoji_id?: string;
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

export default function PostTemplatesPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const navigate = useNavigate();

  const handleDeleteTemplate = async (post: Post) => {
    if (!window.confirm(`Удалить шаблон "${post.name}"?`)) return;
    try {
      await updatePost(
        post.id,
        null,
        false
      );
      setPosts(prev => prev.filter(p => p.id !== post.id));
    } catch (err) {
      console.error('Ошибка при удалении шаблона:', err);
      alert('Не удалось удалить шаблон.');
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const data = await getPosts();
        setPosts(data.filter(p => p.is_template));
      } catch (err) {
        console.error('Ошибка при загрузке шаблонов:', err);
        alert('Не удалось загрузить список шаблонов.');
      }
    })();
  }, []);

  const handleUseTemplate = (post: Post) => {
    navigate('/posts', { state: { template: post } });
  };

  useEffect(() => {
    const removeBack = on("back_button_pressed", () => navigate(`/`));
    return () => removeBack();

}, [navigate]);

  return (
    <div className="container mx-auto p-4 bg-brandlight min-h-screen">

      <div className="flex space-x-8 mb-6">
  {(["schedule", "create", "templates"] as const).map(tab => (
    <button
      key={tab}
      onClick={() => {
        if (tab === "schedule")        navigate("/posts");                     // «Расписание»
        else if (tab === "create")     navigate("/posts", { state: { openCreate: true } });
      }}
      className={`transition pb-1 ${
        tab === "templates"
          ? "text-2xl font-semibold text-brand border-b-2 border-brand"        // активная
          : "text-xl text-gray-600"
      }`}
    >
      {tab === "schedule" ? "Расписание" : tab === "create" ? "Создать пост" : "Шаблоны"}
    </button>
  ))}
</div>
      <h1 className="text-2xl font-semibold text-brand mb-6">Шаблоны постов</h1>
      {posts.length === 0 ? (
        <div className="text-gray-500 italic">Шаблоны не найдены.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map(post => (
            <div
              key={post.id}
              className="relative bg-white rounded-2xl shadow p-4 flex flex-col"
            >
              <img
                src="/icons/trash.png"
                alt="Удалить шаблон"
                className="absolute top-2 right-2 h-6 w-6 cursor-pointer opacity-60 hover:opacity-100 transition"
                onClick={e => { e.stopPropagation(); handleDeleteTemplate(post); }}
              />
              {post.image_path && (
                <img
                  src={post.image_path}
                  alt={post.name}
                  className="h-40 w-full object-cover rounded-lg mb-4"
                />
              )}
              <h2 className="text-lg font-semibold text-brand mb-2">
                {post.name}
              </h2>
              <p className="text-gray-700 flex-grow">
                {post.text.length > 100
                  ? post.text.slice(0, 100) + '…'
                  : post.text}
              </p>
              <button
                onClick={() => handleUseTemplate(post)}
                className="mt-4 py-2 bg-brand text-white rounded-lg shadow hover:bg-brand2 transition"
              >
                Использовать шаблон
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
