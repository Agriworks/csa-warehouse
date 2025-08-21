'use client'
import { Input } from '@/components/ui/input'
import { Search, Loader2 } from 'lucide-react'
import { DatasetCard } from './datasetcard'
import { ContentLayout } from '@/components/admin-panel/content-layout'
import { getDatasetsGetDatasetsGet } from '@/lib/hey-api/client/sdk.gen'
import { useState, useEffect } from 'react'
import { DatasetInformation, DatasetInformationResponse } from '@/lib/hey-api/client/types.gen'

export default function Browse() {
  const [datasets, setDatasets] = useState<DatasetInformation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await getDatasetsGetDatasetsGet()
        if (response.data) {
          const responseData: DatasetInformationResponse = response.data
          setDatasets(responseData.data)
        } else {
          throw new Error('Failed to fetch datasets')
        }
      } catch (err) {
        console.error('Error fetching datasets:', err)
        setError('Failed to load datasets. Please try again later.')
      } finally {
        setLoading(false)
      }
    }

    fetchDatasets()
  }, [])

  return (
    <ContentLayout title="Browse">
      <div className="h-full flex flex-col p-6">
        <div className="relative mb-8">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search datasets..."
            className="pl-9"
          />
        </div>
        {loading && (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {datasets.map((dataset) => (
            <DatasetCard
              key={dataset.dataset_id}
              dataset_id={dataset.dataset_id}
              dataset_name={dataset.dataset_name}
              description={dataset.description || 'No description'}
              useremail={dataset.user_email}
              username={dataset.user_name}
              updated_at={dataset.updated_at}
              pulled_from_pipeline={dataset.pulled_from_pipeline}

            />
          ))}
        </div>
        {datasets.length === 0 && !loading && !error && (
          <div className="flex items-center justify-center h-64">
            <div className="text-muted-foreground">No datasets found.</div>
          </div>
        )}
      </div>
    </ContentLayout>
  )
}
