import { useNavigate } from 'react-router-dom'

export default function HomePage() {
    const navigate = useNavigate()

    return (
        <div className="container mx-auto flex flex-col items-center px-4 justify-center h-screen gap-8 bg-brandlight">
        <h1 className="text-3xl text-brand font-bold">Админ Панель ♡</h1>
    <div className="flex flex-col gap-4 w-full max-w-md">
    <button
        onClick={() => navigate('/stories')}
    className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
        >
        Управление Историями
    </button>
    <button
    onClick={() => navigate('/posts')}
    className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
        >
        Управление Постами
    </button>
    <button
    onClick={() => navigate('/assistant')}
    className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
        >
        Управление Ассистентом
    </button>
    <button
    onClick={() => navigate('/accounts')}
    className="w-full py-6 text-xl bg-brandlight text-brand border border-brand rounded-lg shadow hover:bg-brand hover:text-brandlight transition"
        >
        Управление аккаунтами
    </button>
    </div>
    </div>
)
}
