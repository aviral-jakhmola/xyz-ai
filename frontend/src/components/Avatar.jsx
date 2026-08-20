import { Bot, Sparkles } from 'lucide-react'

export default function Avatar({ state = 'idle', size = 'md' }) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  }

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 28,
  }

  const isActive =
    state === 'thinking' ||
    state === 'listening' ||
    state === 'speaking'

  return (
    <div
      className={`
        ${sizes[size]}
        relative
        shrink-0
        rounded-2xl
        border
        border-emerald-400/30
        bg-emerald-400/10
        text-emerald-400
        flex
        items-center
        justify-center
        shadow-lg
        shadow-emerald-500/5
      `}
    >
      {isActive && (
        <span className="absolute inset-0 rounded-2xl animate-ping bg-emerald-400/10" />
      )}

      {state === 'thinking' ? (
        <Sparkles size={iconSizes[size]} className="relative animate-pulse" />
      ) : (
        <Bot
          size={iconSizes[size]}
          className={`relative ${state === 'speaking' ? 'animate-pulse' : ''}`}
        />
      )}
    </div>
  )
}