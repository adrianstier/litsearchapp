import { useState } from 'react';
import { FaKeyboard, FaTimes } from 'react-icons/fa';
import { useFocusTrap } from '../hooks/useKeyboardShortcuts';
import { useRef, useEffect } from 'react';

const shortcuts = [
  { key: '/', description: 'Focus search bar', category: 'Navigation' },
  { key: 'Ctrl/Cmd + K', description: 'Quick search', category: 'Navigation' },
  { key: 'Esc', description: 'Close modal or clear search', category: 'Navigation' },
  { key: '?', description: 'Show keyboard shortcuts', category: 'Help' },
  { key: 'Tab', description: 'Navigate between elements', category: 'Navigation' },
  { key: 'Enter', description: 'Perform search or submit', category: 'Actions' },
  { key: 'Ctrl/Cmd + S', description: 'Save to library', category: 'Actions' },
  { key: 'Ctrl/Cmd + D', description: 'Download paper', category: 'Actions' },
];

export function KeyboardShortcutsHelp() {
  const [isOpen, setIsOpen] = useState(false);
  const modalRef = useRef(null);

  useFocusTrap(isOpen, modalRef);

  useEffect(() => {
    const handleQuestionMark = (e) => {
      if (e.key === '?' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        setIsOpen(true);
      }
    };

    window.addEventListener('keydown', handleQuestionMark);
    return () => window.removeEventListener('keydown', handleQuestionMark);
  }, []);

  if (!isOpen) {
    return (
      <button
        className="fixed bottom-6 right-6 w-12 h-12 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-30"
        onClick={() => setIsOpen(true)}
        aria-label="Show keyboard shortcuts"
        title="Keyboard shortcuts (Press ?)"
      >
        <FaKeyboard size={20} />
      </button>
    );
  }

  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {});

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 animate-fade-in"
        onClick={() => setIsOpen(false)}
      />

      {/* Modal */}
      <div
        className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-full md:max-w-2xl max-h-[90vh] bg-white dark:bg-slate-800 rounded-2xl shadow-2xl z-50 flex flex-col animate-scale-in"
        ref={modalRef}
        role="dialog"
        aria-labelledby="shortcuts-title"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 id="shortcuts-title" className="text-2xl font-bold text-slate-900 dark:text-slate-50 flex items-center gap-3">
            <FaKeyboard className="text-primary-600 dark:text-primary-400" />
            Keyboard Shortcuts
          </h2>
          <button
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 transition-colors"
            onClick={() => setIsOpen(false)}
            aria-label="Close keyboard shortcuts"
          >
            <FaTimes size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {Object.entries(groupedShortcuts).map(([category, items]) => (
            <div key={category} className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-50 uppercase tracking-wider">
                {category}
              </h3>
              <div className="space-y-2">
                {items.map((shortcut, index) => (
                  <div key={index} className="flex items-center justify-between gap-4 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                    <span className="text-sm text-slate-700 dark:text-slate-300">
                      {shortcut.description}
                    </span>
                    <kbd className="px-3 py-1.5 bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg text-xs font-mono text-slate-900 dark:text-slate-50 shadow-sm">
                      {shortcut.key}
                    </kbd>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 rounded-b-2xl">
          <p className="text-sm text-center text-slate-600 dark:text-slate-400">
            Press <kbd className="px-2 py-1 bg-slate-200 dark:bg-slate-700 rounded text-xs font-mono">?</kbd> anytime to see this help
          </p>
        </div>
      </div>
    </>
  );
}
