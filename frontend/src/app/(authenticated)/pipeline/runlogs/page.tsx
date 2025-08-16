import { Input } from '@/components/ui/input'
import { PipelineItem } from './pipe-item'
import { Search } from 'lucide-react'
import { ContentLayout } from '@/components/admin-panel/content-layout'

export default function RunLogs() {
  return (
    <ContentLayout title="Run Logs">
      <div className="h-full flex flex-col p-6">
      <div className="relative mb-8">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search ..."
            className="pl-9"
          />
        </div>
        <h4 className="text-lg font-semibold mb-4">Technical Commands</h4>
        <div className="space-y-4">
          <PipelineItem datasetId="Issue" />
        </div>
      </div>
    </ContentLayout>
  )
}
