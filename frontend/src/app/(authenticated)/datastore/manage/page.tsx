'use client'
import { Input } from '@/components/ui/input'
import { Search, Loader2 } from 'lucide-react'
import { DatasetCard } from './datasetcard'
import { ContentLayout } from '@/components/admin-panel/content-layout'
import { useState, useEffect } from 'react'
import { getMyDatasetsEndpointGetMyDatasetsPost } from '@/lib/hey-api/client/sdk.gen'
import { GetMyDatasetsResponse, GetMyDatasetsRequest, ManageDatasetResponse } from '@/lib/hey-api/client/types.gen'
import { useSession } from 'next-auth/react'

export default function Manage() {
  const { data: session } = useSession()
  const [datasets, setDatasets] = useState<ManageDatasetResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        setLoading(true)
        setError(null)
        const request: GetMyDatasetsRequest = {
          user_id: session?.user?.email || ''
        }
        const response = await getMyDatasetsEndpointGetMyDatasetsPost({
          body: request
        })
        if (response.data) {
          const responseData: GetMyDatasetsResponse = response.data
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
  }, [session?.user?.email])

  return (
    <ContentLayout title="Manage">
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
              key={dataset.id}
              title={dataset.datasetname}
              description={dataset.description}
              user_id={dataset.user_id}
              username={dataset.user_name}
              ingestedAt={dataset.ingested_date}
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
