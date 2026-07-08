import { useMemo, useState } from 'react'
import { deletePrediction } from '../api/healthApi'
import { formatDate, getStressColor } from '../utils/colors'

export default function HistoryTable({ items, onRefresh, loading }) {
  const [filter, setFilter] = useState('')
  const [sortKey, setSortKey] = useState('date')
  const [sortDir, setSortDir] = useState('desc')

  const filtered = useMemo(() => {
    let rows = [...(items || [])]
    if (filter) {
      const q = filter.toLowerCase()
      rows = rows.filter(
        (row) =>
          row.stress?.toLowerCase().includes(q) ||
          row.fatigue_type?.toLowerCase().includes(q) ||
          String(row.wellness_score).includes(q),
      )
    }
    rows.sort((a, b) => {
      let av = a[sortKey]
      let bv = b[sortKey]
      if (sortKey === 'date') {
        av = new Date(av).getTime()
        bv = new Date(bv).getTime()
      }
      if (av < bv) return sortDir === 'asc' ? -1 : 1
      if (av > bv) return sortDir === 'asc' ? 1 : -1
      return 0
    })
    return rows
  }, [items, filter, sortKey, sortDir])

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this history entry?')) return
    await deletePrediction(id)
    onRefresh()
  }

  return (
    <div className="card">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold">Assessment History</h2>
        <input
          type="search"
          placeholder="Filter by stress, fatigue type, score..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
        />
      </div>

      {loading ? (
        <p className="text-slate-400">Loading history...</p>
      ) : filtered.length === 0 ? (
        <p className="text-slate-400">No history records yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-700">
                {[
                  ['date', 'Date'],
                  ['stress', 'Stress'],
                  ['fatigue', 'Fatigue'],
                  ['fatigue_type', 'Fatigue Type'],
                  ['wellness_score', 'Wellness Score'],
                ].map(([key, label]) => (
                  <th key={key} className="cursor-pointer px-3 py-2 font-medium" onClick={() => toggleSort(key)}>
                    {label} {sortKey === key ? (sortDir === 'asc' ? '↑' : '↓') : ''}
                  </th>
                ))}
                <th className="px-3 py-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => (
                <tr key={row.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="px-3 py-3">{formatDate(row.date)}</td>
                  <td className="px-3 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${getStressColor(row.stress)}`}>
                      {row.stress}
                    </span>
                  </td>
                  <td className="px-3 py-3">{row.fatigue === 1 ? 'Yes' : 'No'}</td>
                  <td className="px-3 py-3 capitalize">{row.fatigue_type}</td>
                  <td className="px-3 py-3 font-medium">{row.wellness_score}</td>
                  <td className="px-3 py-3">
                    <button
                      onClick={() => handleDelete(row.id)}
                      className="rounded-lg px-2 py-1 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
