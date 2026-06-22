import React from 'react';

const FileUploadCard = ({
  title,
  description,
  allowedTypesLabel,
  accept,
  selectedFile,
  onFileSelect,
  onUpload,
  isLoading,
  uploadStatus
}) => {
  const getStatusBg = (type) => {
    switch (type) {
      case 'success':
        return 'bg-emerald-50 text-emerald-800 border-emerald-100';
      case 'warning':
        return 'bg-amber-50 text-amber-800 border-amber-100';
      case 'error':
      default:
        return 'bg-rose-50 text-rose-800 border-rose-100';
    }
  };

  const getStatusIcon = (type) => {
    switch (type) {
      case 'success':
        return (
          <svg className="h-4 w-4 text-emerald-655" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="h-4 w-4 text-amber-655" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 9v2m0 4h.01" />
          </svg>
        );
      case 'error':
      default:
        return (
          <svg className="h-4 w-4 text-rose-655" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
    }
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs select-none">
      <h2 className="text-left text-sm font-bold text-slate-900">{title}</h2>
      {description && <p className="text-left text-[11px] text-slate-400 mt-1">{description}</p>}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          onUpload();
        }}
        className="mt-5 space-y-4 text-left"
      >
        {uploadStatus && (
          <div className={`flex items-start gap-2.5 rounded-lg border p-3 text-xs font-semibold ${getStatusBg(uploadStatus.type)}`}>
            <span className="shrink-0 mt-0.5">{getStatusIcon(uploadStatus.type)}</span>
            <span>{uploadStatus.message}</span>
          </div>
        )}

        <div className="flex w-full items-center justify-center">
          <label className="flex h-32 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-slate-100 transition-colors">
            <div className="flex flex-col items-center justify-center pb-6 pt-5 px-4 text-center">
              <svg className="mb-2.5 h-7 w-7 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-xs text-slate-605 font-bold leading-normal truncate max-w-xs">
                {selectedFile ? selectedFile.name : `Select Statement or Receipt`}
              </p>
              <p className="mt-1 text-[10px] text-slate-400">{allowedTypesLabel}</p>
            </div>
            <input
              type="file"
              accept={accept}
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  onFileSelect(e.target.files[0]);
                }
              }}
              disabled={isLoading}
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={isLoading || !selectedFile}
          className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-indigo-500 disabled:opacity-50 select-none cursor-pointer"
        >
          {isLoading ? (
            <>
              <svg className="h-4 w-4 animate-spin text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing statement...
            </>
          ) : (
            'Process and Upload file'
          )}
        </button>
      </form>
    </div>
  );
};

export default FileUploadCard;
