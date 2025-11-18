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
        className="keyboard-shortcuts-trigger"
        onClick={() => setIsOpen(true)}
        aria-label="Show keyboard shortcuts"
        title="Keyboard shortcuts (Press ?)"
      >
        <FaKeyboard />
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
      <div className="modal-overlay" onClick={() => setIsOpen(false)} />
      <div className="keyboard-shortcuts-modal" ref={modalRef} role="dialog" aria-labelledby="shortcuts-title">
        <div className="modal-header">
          <h2 id="shortcuts-title">
            <FaKeyboard /> Keyboard Shortcuts
          </h2>
          <button
            className="modal-close"
            onClick={() => setIsOpen(false)}
            aria-label="Close keyboard shortcuts"
          >
            <FaTimes />
          </button>
        </div>

        <div className="shortcuts-content">
          {Object.entries(groupedShortcuts).map(([category, items]) => (
            <div key={category} className="shortcut-category">
              <h3>{category}</h3>
              <div className="shortcuts-list">
                {items.map((shortcut, index) => (
                  <div key={index} className="shortcut-item">
                    <kbd className="shortcut-key">{shortcut.key}</kbd>
                    <span className="shortcut-description">{shortcut.description}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="modal-footer">
          <p>Press <kbd>?</kbd> anytime to see this help</p>
        </div>
      </div>
    </>
  );
}
