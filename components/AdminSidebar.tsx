'use client';

type AdminSidebarItem = {
  key: string;
  label: string;
  description?: string;
  icon?: string;
  disabled?: boolean;
  lockedReason?: string;
};

type AdminSidebarProps = {
  items: AdminSidebarItem[];
  activeKey: string | null;
  onSelect: (key: string) => void;
};

export default function AdminSidebar({
  items,
  activeKey,
  onSelect,
}: AdminSidebarProps) {
  return (
    <aside className="w-full max-w-xs space-y-4">
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
          Navigation admin
        </h2>
        <nav className="mt-4 space-y-2">
          {items.map((item) => {
            const isActive = item.key === activeKey;
            const isDisabled = item.disabled;

            const baseClasses =
              'w-full rounded-lg border px-3 py-2 text-left transition';
            const stateClasses = isActive
              ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
              : 'border-transparent hover:border-indigo-200 hover:bg-indigo-50';
            const disabledClasses =
              'cursor-not-allowed border-dashed border-gray-200 bg-gray-50 text-gray-400 hover:border-gray-200 hover:bg-gray-50';

            const buttonClassName = [
              baseClasses,
              stateClasses,
              isDisabled ? disabledClasses : '',
            ]
              .filter(Boolean)
              .join(' ');

            return (
              <button
                key={item.key}
                type="button"
                onClick={() => {
                  if (!isDisabled) {
                    onSelect(item.key);
                  }
                }}
                className={buttonClassName}
                disabled={isDisabled}
                title={isDisabled ? item.lockedReason : undefined}
              >
                <div className="flex items-center gap-2">
                  {item.icon && <span className="text-lg">{item.icon}</span>}
                  <div>
                    <p className="text-sm font-semibold">{item.label}</p>
                    {item.description && (
                      <p className="text-xs text-gray-500">{item.description}</p>
                    )}
                    {isDisabled && item.lockedReason && (
                      <p className="mt-1 text-xs font-medium text-red-500">
                        {item.lockedReason}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
