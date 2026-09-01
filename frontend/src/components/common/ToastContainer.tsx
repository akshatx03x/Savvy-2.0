'use client';

import React from 'react';
import { useToast } from './ToastContext';

export default function ToastContainer() {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-md w-full">
      {toasts.map((toast) => {
        let borderClass = 'border-slate-300';
        let bgClass = 'bg-white';
        let textClass = 'text-slate-900';

        if (toast.type === 'error') {
          borderClass = 'border-red-300';
          bgClass = 'bg-red-50';
          textClass = 'text-red-900';
        } else if (toast.type === 'success') {
          borderClass = 'border-emerald-300';
          bgClass = 'bg-emerald-50';
          textClass = 'text-emerald-900';
        }

        return (
          <div
            key={toast.id}
            className={`flex items-center justify-between p-3.5 rounded-lg border shadow-sm text-xs font-medium transition ${bgClass} ${borderClass} ${textClass}`}
          >
            <span>{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="ml-3 text-slate-400 hover:text-slate-700 text-sm font-bold"
            >
              ×
            </button>
          </div>
        );
      })}
    </div>
  );
}
