import { useState } from 'react'
import { Link } from 'react-router-dom'
import { mockPurchases } from '../lib/mock-data.ts'
import { StoreIcon } from '../components/StoreIcon.tsx'

const stores = ['all', ...new Set(mockPurchases.map((p) => p.storeName))]

export function Purchases() {
  const [storeFilter, setStoreFilter] = useState('all')

  const filtered =
    storeFilter === 'all'
      ? mockPurchases
      : mockPurchases.filter((p) => p.storeName === storeFilter)

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Purchase History</h1>

      {/* Store filter chips */}
      <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
        {stores.map((store) => (
          <button
            key={store}
            onClick={() => setStoreFilter(store)}
            className={`min-h-10 shrink-0 rounded-full px-4 text-sm font-medium ${
              storeFilter === store
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 shadow-sm'
            }`}
          >
            {store === 'all' ? 'All Stores' : store}
          </button>
        ))}
      </div>

      {/* Purchase list */}
      <div className="mt-4 space-y-3">
        {filtered.length === 0 ? (
          <div className="rounded-xl bg-white p-6 text-center shadow-sm">
            <p className="text-sm text-gray-500">No purchases found for this filter.</p>
          </div>
        ) : (
          filtered.map((purchase) => (
            <Link
              key={purchase.id}
              to={`/purchases/${purchase.id}`}
              className="block rounded-xl bg-white p-4 shadow-sm active:bg-gray-50"
            >
              <div className="flex items-center gap-3">
                <StoreIcon storeId={purchase.storeId} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900">{purchase.storeName}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(purchase.date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-900">${purchase.total.toFixed(2)}</p>
                  <p className="text-xs text-gray-500">{purchase.items.length} items</p>
                </div>
              </div>

              {/* Item preview */}
              <p className="mt-2 truncate text-xs text-gray-400">
                {purchase.items
                  .slice(0, 3)
                  .map((i) => i.name)
                  .join(', ')}
                {purchase.items.length > 3 && ` +${purchase.items.length - 3} more`}
              </p>
            </Link>
          ))
        )}
      </div>
    </div>
  )
}
