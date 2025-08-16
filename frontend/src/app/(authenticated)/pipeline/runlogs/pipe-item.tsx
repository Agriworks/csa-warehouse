'use client'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { getPipelineStatusPipelineStatusPost, runPipelineRunPipelinePost } from '@/lib/hey-api/client/sdk.gen'
import { RunPipelineRequest, PipelineStatusRequest, RunPipelineResponse, PipelineStatusResponse } from '@/lib/hey-api/client/types.gen'
import { useSession } from 'next-auth/react'
import { usePipelineStatusCheck } from '@/components/hooks/usePipelineStatusCheck'
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

export function PipelineItem({ datasetId }: { datasetId: string }) {
  const { data: session } = useSession()
  const [pipelineStatus, setPipelineStatus] = useState<'completed' | 'running' | 'error' | null>(null)

  const runPipeline = async () => {
    try {
      const runRequest: RunPipelineRequest = {
        dataset_id: datasetId,
        user_id: session?.user?.email || '',
        username: session?.user?.name || ''
      }

      // Submit the task
      const response = await runPipelineRunPipelinePost({
        body: runRequest
      })

      if (response.data) {
        const responseData: RunPipelineResponse = response.data
        setPipelineStatus(responseData.status)
      }
    } catch (error) {
      console.error('Failed to run pipeline:', error)
      setPipelineStatus('error')
    }
  }

  const checkPipelineStatus = async () => {
    try {
      const requestBody: PipelineStatusRequest = {
        dataset_id: datasetId,
        user_id: session?.user?.email || ''
      }
      const response = await getPipelineStatusPipelineStatusPost({
        body: requestBody
      })
      if (response.data) {
        const responseData: PipelineStatusResponse = response.data
        setPipelineStatus(responseData.status)
      }
    } catch (error) {
      console.error('Failed to check pipeline status:', error)
    }
  }

  // Use the custom hook to automatically check pipeline status after 30 seconds
  usePipelineStatusCheck(pipelineStatus, checkPipelineStatus, datasetId)

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="p-4">
          <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Pipeline {datasetId}</h2>
              {pipelineStatus == null && (
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1"
                  onClick={runPipeline}
                >
                Run Pipeline
              </Button>
              )}
              {pipelineStatus == 'running' && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="gap-1"
                >
                <div className="flex items-center gap-2">
                  <Loader2 className="animate-spin" />
                  {pipelineStatus}
                </div>
              </Button>
              )}
              {pipelineStatus == 'completed' && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="gap-1"
                >
                  <div className="flex items-center gap-2">
                  <CheckCircle className="text-green-500" />
                  {pipelineStatus}
                </div>
                </Button>
              )}
              {pipelineStatus == 'error' && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="gap-1"
                >
                  <div className="flex items-center gap-2">
                  <AlertCircle className="text-red-500" />
                  {pipelineStatus}
                </div>
                </Button>
              )}
        </div>
      </div>
    </div>
  )
}

