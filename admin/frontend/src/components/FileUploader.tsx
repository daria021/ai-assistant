import type {ChangeEvent} from "react";

interface FileUploaderProps {
    label: string;
    file: File | null;
    preview: string | null;
    onFileChange: (file: File | null) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({
                                                       label,
                                                       preview,
                                                       onFileChange
                                                   }) => (
    <div className="flex flex-col gap-2 items-start px-4">
        <p className="uppercase text-xs text-gray-500">{label}</p>
        <label className="bg-brandlight text-brand border border-brand py-2 px-4 rounded cursor-pointer hover:shadow-lg transition-shadow duration-200 text-sm inline-flex flex-col items-center gap-2">
            {preview ? (
                <>
                    <img
                        src={preview}
                        alt="preview"
                        className="w-32 h-32 object-cover mb-1"
                    />
                    <div className="flex items-center text-green-600 text-sm">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-4 h-4 mr-1"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-10.707a1 1 0 10-1.414-1.414L9 9.586 7.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                clipRule="evenodd"
                            />
                        </svg>
                        Файл загружен
                    </div>
                </>
            ) : (
                <div className="flex items-center gap-2">
                    <img
                        src="/icons/paperclip.png"
                        alt="paperclip"
                        className="h-4 w-4"
                    />
                    <span>Выбрать файл</span>
                </div>
            )}
            <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    onFileChange(e.target.files?.[0] || null)
                }
            />
        </label>
    </div>
);

export default FileUploader;
