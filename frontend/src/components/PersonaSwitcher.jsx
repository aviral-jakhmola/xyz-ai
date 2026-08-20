import { Check } from 'lucide-react'

export default function PersonaSwitcher({ users, currentUser, onSelect }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
      <div className="mb-3">
        <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
          Demo Accounts
        </p>
        <h2 className="mt-1 text-sm font-semibold text-slate-200">
          Switch Role
        </h2>
      </div>

      <div className="space-y-2">
        {users.map((user) => {
          const active = user.id === currentUser.id

          return (
            <button
              key={user.id}
              type="button"
              onClick={() => onSelect(user)}
              className={`
                flex w-full items-center justify-between rounded-xl border p-3 text-left transition
                ${
                  active
                    ? 'border-emerald-400/30 bg-emerald-400/10'
                    : 'border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900'
                }
              `}
            >
              <div className="min-w-0">
                <p
                  className={`truncate text-sm font-medium ${
                    active ? 'text-emerald-300' : 'text-slate-300'
                  }`}
                >
                  {user.name}
                </p>
                <p className="mt-0.5 text-xs capitalize text-slate-500">
                  {user.role}
                </p>
              </div>

              {active && <Check size={16} className="shrink-0 text-emerald-400" />}
            </button>
          )
        })}
      </div>
    </section>
  )
}