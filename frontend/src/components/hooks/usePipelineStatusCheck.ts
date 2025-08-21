import { useEffect, useRef } from 'react'

type PipelineStatus = 'completed' | 'running' | 'error'

/**
 * Custom hook to automatically check pipeline status every 30 seconds when pipeline is running
 * @param pipelineStatus - Current status of the pipeline
 * @param checkPipelineStatus - Function to call for checking pipeline status
 * @param datasetId - ID of the dataset for logging purposes
 */
export const usePipelineStatusCheck = (
  pipelineStatus: PipelineStatus | null,
  checkPipelineStatus: () => Promise<void>,
  datasetId: string
) => {
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // If pipeline is running, set up an interval to check status every 30 seconds
    if (pipelineStatus === 'running') {
      console.log(`Setting up status check interval for dataset ${datasetId} every 15 seconds`)
      
      // Check immediately
      checkPipelineStatus()
      
      // Then set up interval for every 15 seconds
      intervalRef.current = setInterval(() => {
        console.log(`Checking pipeline status for dataset ${datasetId} (15-second interval)`)
        checkPipelineStatus()
      }, 30 * 1000) // 15 seconds in milliseconds
    }

    // Cleanup function to clear interval when component unmounts or status changes
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [pipelineStatus, checkPipelineStatus, datasetId])
}
