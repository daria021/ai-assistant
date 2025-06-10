import { useNavigate } from 'react-router-dom';
import {useState, useMemo, useEffect} from 'react';
import FileUploader from '../components/FileUploader';
import {on} from '@telegram-apps/sdk';

export default function StoryDetailsPage() {
    const navigate = useNavigate();

    // Захардкоженные данные истории
    const [photoUrl] = useState('/default-story.png');
    const [title, setTitle] = useState('Название захардкоженной истории');
    const [text, setText] = useState('Текст под историей захардкоженный...');
    const [scheduleType, setScheduleType] = useState<'once' | 'daily'>('once');
    const [date, setDate] = useState('2025-05-17');
    const [time, setTime] = useState('08:00');

    // Управление аккаунтами менеджеров
    const initialAccounts = useMemo(
        () => ['ManagerAccount1', 'ManagerAccount2'],
        []
    );
    const [allAccounts] = useState<string[]>(initialAccounts);
    const [selectedAccounts, setSelectedAccounts] = useState<string[]>(initialAccounts);
    const [accountSearch, setAccountSearch] = useState('');
    const filteredAccounts = useMemo(
        () => allAccounts.filter(acc =>
            acc.toLowerCase().includes(accountSearch.trim().toLowerCase())
        ),
        [accountSearch, allAccounts]
    );
    const toggleAccount = (acc: string) => {
        setSelectedAccounts(prev =>
            prev.includes(acc) ? prev.filter(a => a !== acc) : [...prev, acc]
        );
    };

    useEffect(() => {
        const removeBackListener = on('back_button_pressed', () => navigate(-1));
        return () => removeBackListener();
    }, [navigate]);

    const handleSave = () => {
        // Логика сохранения изменений истории
        alert('Изменения истории сохранены');
    };

    const handleDelete = () => {
        // Логика удаления истории
        alert('История удалена');
        navigate(-1);
    };

    return (
        <div className="container mx-auto p-4 bg-brandlight min-h-screen relative">
            {/* Навигация и удаление */}
            <button
                onClick={() => navigate(-1)}
                className="mb-4 text-gray-600 hover:underline"
            >
                ← Назад
            </button>
            <button
                onClick={handleDelete}
                className="absolute top-4 right-4 text-brand font-semibold"
            >
                Удалить
            </button>

            <div className="mb-6">
                <FileUploader
                    label="Фото истории"
                    file={null}
                    preview={photoUrl}
                    onFileChange={() => {}}
                />
            </div>

            <div className="mb-4">
                <label className="block mb-2 font-medium">Название истории</label>
                <input
                    type="text"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                />
            </div>

            <div className="mb-4">
                <label className="block mb-2 font-medium">Текст под историей</label>
                <textarea
                    value={text}
                    onChange={e => setText(e.target.value)}
                    rows={3}
                    className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                />
            </div>

            <div className="mb-4">
                <label className="block mb-2 font-medium">Тип рассылки</label>
                <div className="flex space-x-4">
                    <label className="flex items-center space-x-2">
                        <input
                            type="radio"
                            value="once"
                            checked={scheduleType === 'once'}
                            onChange={() => setScheduleType('once')}
                            className="form-radio h-4 w-4 text-brand"
                        />
                        <span>В указанный день</span>
                    </label>
                    <label className="flex items-center space-x-2">
                        <input
                            type="radio"
                            value="daily"
                            checked={scheduleType === 'daily'}
                            onChange={() => setScheduleType('daily')}
                            className="form-radio h-4 w-4 text-brand"
                        />
                        <span>Каждый день</span>
                    </label>
                </div>
            </div>

            {scheduleType === 'once' ? (
                <div className="flex space-x-4 mb-6">
                    <div className="flex-1">
                        <label className="block mb-2 font-medium">Дата</label>
                        <input
                            type="date"
                            value={date}
                            onChange={e => setDate(e.target.value)}
                            className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                    </div>
                    <div className="flex-1">
                        <label className="block mb-2 font-medium">Время</label>
                        <input
                            type="time"
                            value={time}
                            onChange={e => setTime(e.target.value)}
                            className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                    </div>
                </div>
            ) : (
                <div className="mb-6">
                    <label className="block mb-2 font-medium">Время</label>
                    <input
                        type="time"
                        value={time}
                        onChange={e => setTime(e.target.value)}
                        className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                    />
                </div>
            )}

            {/* Выбор аккаунтов менеджеров */}
            <div className="mb-4">
                <label className="block mb-2 font-medium">Аккаунты для публикации</label>
                <input
                    type="text"
                    placeholder="Поиск аккаунтов..."
                    value={accountSearch}
                    onChange={e => setAccountSearch(e.target.value)}
                    className="w-full mb-2 border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                />
                <div className="max-h-40 overflow-y-auto space-y-2 border border-brand rounded p-2 mb-6">
                    {filteredAccounts.map(acc => (
                        <label key={acc} className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                checked={selectedAccounts.includes(acc)}
                                onChange={() => toggleAccount(acc)}
                                className="form-checkbox h-5 w-5 text-brand focus:ring-brand"
                            />
                            <span>{acc}</span>
                        </label>
                    ))}
                    {filteredAccounts.length === 0 && (
                        <div className="text-gray-500 italic">Аккаунты не найдены</div>
                    )}
                </div>
            </div>

            <div className="flex justify-end">
                <button
                    onClick={handleSave}
                    className="px-4 py-2 bg-brand text-white rounded hover:bg-brand2 transition"
                >
                    Сохранить
                </button>
            </div>
        </div>
    );
}
