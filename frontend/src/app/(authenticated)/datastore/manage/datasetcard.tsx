import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/lib/utils'
import { Mail, User, Loader2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export function DatasetCard({
  dataset_id,
  dataset_name,
  description,
  useremail,
  username,
  updated_at,
  pulled_from_pipeline,
  
}: {
  dataset_id: string
  dataset_name: string
  description: string | null | undefined
  useremail: string
  username: string
  updated_at: string
  pulled_from_pipeline: boolean
}) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleView = async () => {
    setIsLoading(true)
    try {
      await router.push(`/datastore/browse/${encodeURIComponent(dataset_id)}`)
    } catch (error) {
      console.error('Navigation error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="bg-background h-[280px] flex flex-col">
      <CardHeader className="pb-3 flex-shrink-0">
        <CardTitle className="text-lg font-semibold truncate">
          {dataset_name}
        </CardTitle>
        <CardDescription className="text-sm text-muted-foreground line-clamp-2 min-h-[2.5rem]">
          {description ? description : "No description"}
        </CardDescription>
        <p className="text-sm text-muted-foreground">
          {pulled_from_pipeline ? "Pipeline Run on " + formatDate(updated_at) : "Last Updated on " + formatDate(updated_at)}
        </p>
      </CardHeader>
      <CardContent className="pt-0 flex-1 flex flex-col">
        <div className="flex-1">
          <p className="text-sm font-semibold text-foreground mb-2">Pipeline Run By</p>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground flex items-center">
              <User className="w-3 h-3 mr-1.5" />
              {username}
            </p>
            <p className="text-xs text-muted-foreground flex items-center">
              <Mail className="w-3 h-3 mr-1.5" />
              {useremail}
            </p>
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <Button 
            variant="outline"
            className="flex-1 border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground"
            disabled
          >
            Edit
          </Button>
          <Button 
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground"
            onClick={handleView}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              'View'
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
