import {useState, useMemo, useEffect} from "react";
import { useNavigate } from "react-router-dom";
import { FiChevronDown, FiChevronUp } from 'react-icons/fi';
import {on} from '@telegram-apps/sdk';
import FileUploader from "../components/FileUploader.tsx";

export default function StoriesControlPage() {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'schedule' | 'create'>('schedule');

    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string | null>(null);
    const [title, setTitle] = useState('');
    const [text, setText] = useState('');
    const [scheduleType, setScheduleType] = useState<'once' | 'daily'>('once');
    const [date, setDate] = useState('');
    const [time, setTime] = useState('');

    useEffect(() => {
        const removeBackListener = on('back_button_pressed', () => navigate(-1));
        return () => removeBackListener();
    }, [navigate]);

    const initialAccounts = useMemo(
        () => Array.from({ length: 20 }, (_, i) => `Manager ${i + 1}`),
        []
    );
    const [allAccounts] = useState<string[]>(initialAccounts);
    const [selectedAccounts, setSelectedAccounts] = useState<string[]>([]);
    const [accountSearch, setAccountSearch] = useState('');
    const filteredAccounts = useMemo(
        () => allAccounts.filter(acc =>
            acc.toLowerCase().includes(accountSearch.trim().toLowerCase())
        ),
        [accountSearch, allAccounts]
    );

    const [openDays, setOpenDays] = useState<Record<string, boolean>>({});
    const toggleDay = (day: string) => {
        setOpenDays(prev => ({ ...prev, [day]: !prev[day] }));
    };

    const toggleAccount = (acc: string) => {
        setSelectedAccounts(prev =>
            prev.includes(acc) ? prev.filter(a => a !== acc) : [...prev, acc]
        );
    };

    // Для формы создания
    const handlePhotoChange = (file: File | null) => {
        setPhotoFile(file);
        setPhotoPreview(file ? URL.createObjectURL(file) : null);
    };
    const handleSave = () => {
        const payload = {
            photoFile,
            title,
            text,
            scheduleType,
            date: scheduleType === 'once' ? date : null,
            time,
            managers: selectedAccounts,
        };
        console.log('Saving story:', payload);
        // Очистка
        setPhotoFile(null);
        setPhotoPreview(null);
        setTitle('');
        setText('');
        setDate('');
        setTime('');
        setScheduleType('once');
        setSelectedAccounts([]);
        setAccountSearch('');
    };

    // Для расписания (жестко)
    const days = ['17 мая 2025', '18 мая 2025', '19 мая 2025'];
    const events: [string, string][] = [
        ['08:00', 'Утреннее вдохновение'],
        ['12:00', 'Полдник с цитатой'],
        ['18:00', 'Вечерняя история'],
    ];
    const handleDelete = (day: string, t: string, ttl: string) => {
        alert(`${day} ${t} — "${ttl}" удалено`);
    };

    return (
        <div className="container mx-auto p-4 bg-brandlight min-h-screen">
            {/* Tabs */}
            <div className="flex space-x-8 mb-6">
                <button
                    className={`transition pb-1 ${
                        activeTab === 'schedule'
                            ? 'text-2xl font-semibold text-brand border-b-2 border-brand'
                            : 'text-xl text-gray-600'
                    }`}
                    onClick={() => setActiveTab('schedule')}
                >
                    Расписание историй
                </button>
                <button
                    className={`transition pb-1 ${
                        activeTab === 'create'
                            ? 'text-2xl font-semibold text-brand border-b-2 border-brand'
                            : 'text-xl text-gray-600'
                    }`}
                    onClick={() => setActiveTab('create')}
                >
                    Создать историю
                </button>
            </div>

            {activeTab === 'create' && (
                <div className="space-y-6 max-w-lg">
                    <FileUploader
                        label="Фото истории"
                        file={photoFile}
                        preview={photoPreview}
                        onFileChange={handlePhotoChange}
                    />

                    <div>
                        <label className="block mb-2 font-medium">Название истории</label>
                        <input
                            type="text"
                            value={title}
                            onChange={e => setTitle(e.target.value)}
                            className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                    </div>

                    <div>
                        <label className="block mb-2 font-medium">Текст под историей</label>
                        <textarea
                            value={text}
                            onChange={e => setText(e.target.value)}
                            rows={3}
                            className="w-full border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                    </div>

                    <div>
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

                    {scheduleType === 'once' && (
                        <div className="flex space-x-4">
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
                    )}
                    {scheduleType === 'daily' && (
                        <div>
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
                    <div>
                        <label className="block mb-2 font-medium">Аккаунты менеджеров</label>
                        <input
                            type="text"
                            placeholder="Поиск аккаунтов..."
                            value={accountSearch}
                            onChange={e => setAccountSearch(e.target.value)}
                            className="w-full mb-2 border border-brand rounded p-2 focus:outline-none focus:ring-2 focus:ring-brand"
                        />
                        <div className="max-h-60 overflow-y-auto space-y-2 border border-brand rounded p-2">
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

                    <button
                        onClick={handleSave}
                        className="w-full py-3 bg-brand text-white rounded-lg shadow hover:bg-brand2 transition"
                    >
                        Сохранить
                    </button>
                </div>
            )}

            {activeTab === 'schedule' && (
                <div className="space-y-6 text-brand">
                    {days.map(day => (
                        <div key={day} className="bg-brand-pink p-4 rounded-lg shadow">
                            <div
                                className="flex justify-between items-center cursor-pointer"
                                onClick={() => toggleDay(day)}
                            >
                                <h2 className="text-xl font-semibold">{day}</h2>
                                {openDays[day] ? (
                                    <FiChevronUp className="h-5 w-5 text-brand" />
                                ) : (
                                    <FiChevronDown className="h-5 w-5 text-brand" />
                                )}
                            </div>

                            {openDays[day] && (
                                <ul className="mt-4 space-y-2">
                                    {events.map(([t, ttl]) => (
                                        <li
                                            key={t}
                                            className="flex items-center justify-between cursor-pointer hover:bg-gray-100 p-2 rounded"
                                            onClick={() => navigate(`/story-details`)}
                                        >
                      <span>
                        <span className="font-medium">{t}</span> — {ttl}
                      </span>
                                            <img
                                                src="/icons/trash.png"
                                                alt="Удалить"
                                                className="h-5 w-5 cursor-pointer opacity-60 hover:opacity-100 transition"
                                                onClick={e => { e.stopPropagation(); handleDelete(day, time, title); }}

                                            />
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    ))}
                </div>
            )}

        </div>
    );
}
