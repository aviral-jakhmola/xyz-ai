import { CheckCircle2, LockKeyhole } from 'lucide-react'

export default function PermissionPanel({ user, tools }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
      <div className="mb-3">
        <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
          Security
        </p>
        <h2 className="mt-1 text-sm font-semibold text-slate-200">
          Active RBAC Permissions
        </h2>
      </div>

      <div className="space-y-2">
        {tools.map((tool) => {
          const permitted = user.allowed.includes(tool)

          return (
            <div
              key={tool}
              className="flex items-center justify-between gap-3 rounded-xl border border-slate-800/80 bg-slate-950/40 px-3 py-2.5"
            >
              <div className="flex min-w-0 items-center gap-2">
                {permitted ? (
                  <CheckCircle2 size={14} className="shrink-0 text-emerald-400" />
                ) : (
                  <LockKeyhole size={14} className="shrink-0 text-rose-400" />
                )}
                <span className="truncate font-mono text-[11px] text-slate-400">
                  {tool}
                </span>
              </div>

              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide ${
                  permitted
                    ? 'bg-emerald-400/10 text-emerald-400'
                    : 'bg-rose-400/10 text-rose-400'
                }`}
              >
                {permitted ? 'Allowed' : 'Blocked'}
              </span>
            </div>
          )
        })}
      </div>
    </section>
  )
}