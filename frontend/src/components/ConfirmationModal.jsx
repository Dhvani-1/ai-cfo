import React from 'react';

const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = 'Are you sure?',
  message = 'This action cannot be undone.',
  confirmLabel = 'Delete',
  cancelLabel = 'Cancel',
  isDestructive = true
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity" onClick={onClose} />

      {/* Modal Content */}
      <div className="relative w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 shadow-xl text-left select-none transform transition-all">
        <h3 className="text-base font-bold text-slate-950">{title}</h3>
        <p className="mt-2 text-xs leading-relaxed text-slate-500">{message}</p>

        <div className="mt-6 flex justify-end gap-3 text-xs font-semibold">
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-200 px-4 py-2 text-slate-700 hover:bg-slate-50 cursor-pointer"
          >
            {cancelLabel}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`rounded-lg px-4 py-2 text-white shadow-xs cursor-pointer ${
              isDestructive
                ? 'bg-rose-600 hover:bg-rose-500'
                : 'bg-indigo-600 hover:bg-indigo-500'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
