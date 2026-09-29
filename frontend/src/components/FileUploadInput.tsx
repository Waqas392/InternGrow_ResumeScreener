import { useRef, useState } from "react";
import { Button } from "./Button";

interface FileUploadInputProps {
  label: string;
  accept: string;
  multiple?: boolean;
  disabled?: boolean;
  onFiles: (files: File[]) => void;
}

export function FileUploadInput({
  label,
  accept,
  multiple = false,
  disabled = false,
  onFiles
}: FileUploadInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  const openPicker = () => {
    inputRef.current?.click();
  };

  const handleChange = () => {
    const files = Array.from(inputRef.current?.files ?? []);
    setSelectedFiles(files.map(file => file.name));
    onFiles(files);

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-3">
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        className="sr-only"
        onChange={handleChange}
        disabled={disabled}
        aria-label={label}
      />
      <div className="flex flex-wrap items-center gap-3">
        <Button type="button" variant="secondary" onClick={openPicker} disabled={disabled}>
          Choose files
        </Button>
        <p className="text-sm text-slate-500 dark:text-slate-300">
          {selectedFiles.length > 0 ? selectedFiles.join(", ") : label}
        </p>
      </div>
    </div>
  );
}
