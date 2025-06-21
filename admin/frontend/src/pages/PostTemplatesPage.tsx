import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPosts } from '../services/api';
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
}

export default function PostTemplatesPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const data = await getPosts();
        setPosts(data);
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
              className="bg-white rounded-2xl shadow p-4 flex flex-col"
            >
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
