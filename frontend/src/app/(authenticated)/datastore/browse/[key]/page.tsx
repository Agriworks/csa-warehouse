'use client'

import { ContentLayout } from "@/components/admin-panel/content-layout"
import { DataTable } from "@/components/TableView/data-table"
import { getDatasetByIdEndpointGetDatasetByIdPost } from "@/lib/hey-api/client/sdk.gen"
import { GetDatasetByIdRequest, GetDatasetByIdResponse } from "@/lib/hey-api/client/types.gen"
import { useEffect, useState, useCallback } from "react"
import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Loader2, AlertCircle } from "lucide-react"
import { useParams } from "next/navigation"

export default function DatasetDetails() {
    const params = useParams()
    const key = params.key as string
    const [datasetData, setDatasetData] = useState<GetDatasetByIdResponse | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    // Pagination state
    const [currentPage, setCurrentPage] = useState(0)
    const [pageSize, setPageSize] = useState(10)
    const [totalRows, setTotalRows] = useState(0)

    const fetchDatasetRows = useCallback(async (page: number, size: number) => {
        try {
            setLoading(true)
            setError(null)
            
            const offset = page
            const request: GetDatasetByIdRequest = {
                id: key,
                offset: offset,
                limit: size
            }
            
            const response = await getDatasetByIdEndpointGetDatasetByIdPost({
                body: request
            })
            
            if (response.data) {
                const responseData: GetDatasetByIdResponse = response.data
                setDatasetData(responseData)
                setTotalRows(responseData.record_count)
            } else {
                throw new Error('Failed to fetch dataset rows')
            }
        } catch (err) {
            console.error('Error fetching dataset rows:', err)
            setError('Failed to load dataset. Please try again later.')
        } finally {
            setLoading(false)
        }
    }, [key])

    useEffect(() => {
        if (key) {
            fetchDatasetRows(currentPage, pageSize)
        }
    }, [key, currentPage, pageSize, fetchDatasetRows])

    // Handle page size change
    const handlePageSizeChange = (newPageSize: number) => {
        setPageSize(newPageSize)
        setCurrentPage(0) // Reset to first page when page size changes
    }

    // Handle page change
    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage)
    }

    // Generate columns dynamically based on the first row of data
    const generateColumns = (data: Record<string, unknown>[]): ColumnDef<Record<string, unknown>>[] => {
        if (!data || data.length === 0) return []
        
        const firstRow = data[0]
        return Object.keys(firstRow).map((key) => ({
            accessorKey: key,
            header: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
            cell: ({ row }) => {
                const value = row.getValue(key)
                if (value === null || value === undefined) {
                    return <span className="text-muted-foreground">-</span>
                }
                if (typeof value === 'boolean') {
                    return (
                        <Badge variant={value ? "default" : "secondary"}>
                            {value ? "Yes" : "No"}
                        </Badge>
                    )
                }
                if (typeof value === 'number') {
                    return <span className="font-mono">{value}</span>
                }
                return <span>{String(value)}</span>
            }
        }))
    }

    const columns = datasetData?.data ? generateColumns(datasetData.data) : []

    if (loading) {
        return (
            <ContentLayout title="Dataset Details">
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            </ContentLayout>
        )
    }

    if (error) {
        return (
            <ContentLayout title="Dataset Details">
                <div className="flex items-center justify-center h-64">
                    <div className="flex items-center gap-2 text-destructive">
                        <AlertCircle className="h-5 w-5" />
                        <span>{error}</span>
                    </div>
                </div>
            </ContentLayout>
        )
    }

    return (
        <ContentLayout title="Dataset Details">
            <div className="h-full flex flex-col p-6 space-y-6">
                {datasetData && (
                    <>
                        <div className="flex flex-col gap-2">
                            <h4 className="font-bold">{datasetData.dataset_name}</h4>
                            <p className="text-sm text-muted-foreground">By {datasetData.user_name}</p>
                            <p className="text-sm text-muted-foreground">{datasetData.description}</p>
                        </div>
                        <div className="flex-1">
                            <DataTable 
                                columns={columns}
                                data={datasetData.data}
                                isLoading={loading}
                                currentPage={currentPage}
                                pageSize={pageSize}
                                totalRows={totalRows}
                                onPageSizeChange={handlePageSizeChange}
                                onPageChange={handlePageChange}
                            />
                        </div>
                    </>
                )}
            </div>
        </ContentLayout>
    )
}
