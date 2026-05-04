import { useState, useEffect, useRef } from 'react'

interface EditableTextProps {
  value: string
  onSave: (newValue: string) => void
  multiline?: boolean
  className?: string
}

export default function EditableText({ value, onSave, multiline = false, className = '' }: EditableTextProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const [expanded, setExpanded] = useState(false)
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null)

  useEffect(() => { setDraft(value) }, [value])

  useEffect(() => {
    if (editing) inputRef.current?.focus()
  }, [editing])

  function handleSave() {
    setEditing(false)
    if (draft !== value) onSave(draft)
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Escape') {
      setDraft(value)
      setEditing(false)
    } else if (e.key === 'Enter' && !multiline) {
      handleSave()
    } else if (e.key === 'Enter' && multiline && !e.shiftKey) {
      handleSave()
    }
  }

  if (!editing) {
    if (multiline) {
      return (
        <div className="flex flex-col items-start w-full">
          <div
            className={`cursor-pointer font-black w-full ${className} ${!expanded ? 'line-clamp-5' : 'whitespace-pre-wrap'}`}
            onClick={() => setEditing(true)}
            title="Click to edit"
          >
            {value || <span style={{ color: 'var(--muted)' }}>(empty)</span>}
          </div>
          {value && value.length > 0 && (
            <button 
              onClick={() => setExpanded(!expanded)} 
              className="text-[10px] underline mt-1 font-bold" 
              style={{ color: 'var(--muted)' }}
            >
              {expanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      )
    }

    return (
      <span
        className={`cursor-pointer font-black ${className}`}
        onClick={() => setEditing(true)}
        title="Click to edit"
      >
        {value || <span style={{ color: 'var(--muted)' }}>(empty)</span>}
      </span>
    )
  }

  if (multiline) {
    return (
      <textarea
        ref={inputRef as React.RefObject<HTMLTextAreaElement>}
        value={draft}
        onChange={e => setDraft(e.target.value)}
        onBlur={handleSave}
        onKeyDown={handleKeyDown}
        className={`nb-input w-full ${className}`}
        style={{ minHeight: '150px', resize: 'vertical' }}
        autoFocus
      />
    )
  }

  return (
    <input
      ref={inputRef as React.RefObject<HTMLInputElement>}
      type="text"
      value={draft}
      onChange={e => setDraft(e.target.value)}
      onBlur={handleSave}
      onKeyDown={handleKeyDown}
      className={`nb-input ${className}`}
      autoFocus
    />
  )
}