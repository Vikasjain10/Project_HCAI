import { useCallback, useEffect, useState } from 'react'
import { fetchPredictionHistory } from '../api/healthApi'
import HistoryTable from '../components/HistoryTable'

export default function HistoryPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  const loadHistory = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchPredictionHistory()
      setItems(data)
    } catch {
      setItems([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">History</h1>
        <p className="text-slate-500 dark:text-slate-400">
          View, filter, sort, and manage past health assessments
        </p>
      </div>
      <HistoryTable items={items} onRefresh={loadHistory} loading={loading} />
    </div>
  )
}
