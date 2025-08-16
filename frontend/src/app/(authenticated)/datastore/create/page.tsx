'use client'
import { useState, useEffect } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { CloudUpload, Paperclip } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Form, FormControl, FormField, FormItem, FormLabel } from '@/components/ui/form'
import { ContentLayout } from '@/components/admin-panel/content-layout'
import { FileInput, FileUploader, FileUploaderContent } from '@/components/file-upload/FileUpload'
import FileDownloadButton from '@/components/file-upload/FileDownloadButton'
import { TagInput } from '@/app/(authenticated)/datastore/create/tag-input'
import { DatasetConfigurationDialog, DatasetConfigFormData } from '@/app/(authenticated)/datastore/create/dataset-cofig-dialogue'
import { useToast } from '@/components/hooks/use-toast'
import { useSession } from 'next-auth/react'
import { SearchDatatype } from '@/app/(authenticated)/datastore/create/search-datatype'

// Zod schemas for each section
const datasetInformationSchema = z.object({
  name: z.string().min(1, "Dataset name is required"),
  description: z.string().optional(),
  permission: z.enum(["public", "private"]),
  category: z.string().optional(),
  tags: z.array(z.string()).optional(),
})

// Type for the complete form data
type CompleteFormData = {
  datasetInformation: z.infer<typeof datasetInformationSchema>
  dataSelection: {
    file_id: number
  }
  configuration?: {
    isSpatial: boolean
    spatialHierarchy?: {
      lat?: number
      long?: number
      country?: string
      state?: string
      district?: string
      village?: string
    }
    isTemporal: boolean
    temporalHierarchy?: string
  }
}

export default function Create() {
  const [files, setFiles] = useState<File[] | null>(null)
  const [fileUrls, setFileUrls] = useState<number[]>([]);
  const [isConfigDialogOpen, setIsConfigDialogOpen] = useState(false)
  const [isFormValid, setIsFormValid] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()
  const { data: session } = useSession()

  const dropZoneConfig = {
    accept: {
      "text/csv": [".csv"],
    },
    maxFiles: 1,
    multiple: false,
    maxSize: 4 * 1024 * 1024,
  };

  const form = useForm<z.infer<typeof datasetInformationSchema>>({
    resolver: zodResolver(datasetInformationSchema),
    defaultValues: {
      name: "",
      description: "",
      permission: "public",
      tags: [],
    },
  });

  // Check if all required fields are filled
  useEffect(() => {
    const checkFormValidity = () => {
      const datasetInfoValid = form.formState.isValid
      const dataSelectionValid = fileUrls.length > 0
      
      setIsFormValid(datasetInfoValid && dataSelectionValid)
    }

    checkFormValidity()
  }, [form.formState.isValid, fileUrls.length])

  async function onSubmit(
    data: z.infer<typeof datasetInformationSchema>,
    configData: DatasetConfigFormData
  ) {
    setIsSubmitting(true)
    
    try {
      const completeData: CompleteFormData = {
        datasetInformation: data,
        dataSelection: {
          file_id: fileUrls[0] || 0,
        },
        configuration: configData,
      };
      
      console.log('Complete form data:', completeData);
      
      // Prepare the dataset object for the API
      const datasetPayload: {
        title: string
        description: string
        uploader: {
          id: string
          username: string
          firstName: string
          lastName: string
          email: string
          organisation: string
        }
        uploadDate: string
        tags: {
          name: string
        }[]
        isSpatial: boolean
        isTemporal: boolean
      } = {
        title: data.name,
        description: data.description || "",
        uploader: {
          id: "",
          username: session?.user?.name || "",
          firstName: "",
          lastName: "",
          email: session?.user?.email || "",
          organisation: ""
        },
        uploadDate: new Date().toISOString(),
        tags: data.tags?.map(tag => ({ name: tag })) || [],
        isSpatial: configData.isSpatial,
        isTemporal: configData.isTemporal,
      }
      console.log('Dataset payload:', datasetPayload);

      // Make the API call
      // const response = await addDataset({
      //   body: datasetPayload
      // });
      // console.log('Response:', response);

      // if (response.data) {
      //   toast({
      //     title: "Success!",
      //     description: "Dataset created successfully.",
      //   });
        
      //   // Reset the form
      //   form.reset({
      //     name: "",
      //     description: "",
      //     permission: "public",
      //     tags: [],
      //   });
      //   setFiles(null);
      //   setFileUrls([]);
      //   setIsConfigDialogOpen(false);
      // } else {
      //   console.error('API Error:', response.error);
      //   toast({
      //     title: "Error",
      //     description: "Failed to create dataset. Please try again.",
      //     variant: "destructive",
      //   });
      // }
    } catch (error) {
      console.error('Error creating dataset:', error);
      toast({
        title: "Error",
        description: "Failed to create dataset. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  const handleConfigureDataset = () => {
    setIsConfigDialogOpen(true)
  }

  const handleConfigComplete = (data: DatasetConfigFormData) => {
    console.log('Configuration completed:', data)
    setIsConfigDialogOpen(false)
  }

  const handleSubmitForm = async (configData: DatasetConfigFormData) => {
    const data = form.getValues();
    await onSubmit(data, configData);
  }

  return (
    <ContentLayout title="Create">
      <Form {...form}>
        <form className="h-full flex flex-col space-y-6 p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-background shadow-none">
            <CardHeader>
              <CardTitle>Dataset Information</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-6">
              <div className="space-y-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({field}) => (
                    <FormItem>
                      <FormLabel>Dataset Name<span className="text-destructive">*</span></FormLabel>
                      <FormControl>
                        <Input placeholder="Enter dataset name" {...field} type="text"/>
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>

              <div className="space-y-2">
                <FormField
                  control={form.control}
                  name="description"
                  render={({field}) => (
                    <FormItem>
                      <FormLabel>Description (Optional)</FormLabel>
                      <FormControl>
                        <Textarea placeholder="Enter dataset description" {...field} />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>

              <div className="space-y-2">
                <FormField
                  control={form.control}
                  name="permission"
                  render={({field}) => (
                    <FormItem>
                      <FormLabel>Permission<span className="text-destructive">*</span></FormLabel>
                      <FormControl>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <SelectTrigger id="permission" className="w-full">
                          <SelectValue placeholder="Select permission" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="public">Public</SelectItem>
                            <SelectItem value="private">Private</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>

              <div className="space-y-2">
                <FormField
                  control={form.control}
                  name="category"
                  render={({field}) => (
                    <FormItem>
                      <FormLabel>Dataset Type</FormLabel>
                      <FormControl>
                        <SearchDatatype
                          options={[]}
                          value={field.value}
                          onValueChange={field.onChange}
                          placeholder="Implement soon"
                          searchPlaceholder="Search categories..."
                          emptyMessage="No categories found."
                          disabled={true}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>

              <div className="space-y-2">
                <FormField
                  control={form.control}
                  name="tags"
                  render={({field}) => (
                    <FormItem>
                      <FormLabel>Tags</FormLabel>
                      <FormControl>
                        <TagInput
                          value={field.value || []}
                          onChange={field.onChange}
                          placeholder="Add tags (press Enter or comma to add)"
                          maxTags={5}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-background shadow-none">
            <CardHeader>
              <CardTitle>Data Selection</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-6">
              <p className="text-sm text-muted-foreground">
                Choose a file with relevant data from your computer to upload.
                <br />
                Acceptable file format: CSV
              </p>
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  File Upload<span className="text-destructive">*</span>
                </label>
                <FileUploader
                  value={files}
                  onValueChange={
                    (value) => {
                      setFiles(value)
                    }
                  }
                  onUploadComplete={(urls) => {
                    setFileUrls(urls);
                  }}
                  dropzoneOptions={dropZoneConfig}
                  className="relative bg-background rounded-lg p-2"
                  authToken={""}
                >
                  <FileInput
                    id="file-input"
                    className="outline-dashed outline-1 outline-border"
                  >
                    <div className="flex items-center justify-center flex-col p-8 w-full">
                    <CloudUpload className="text-muted-foreground w-8 h-8" />
                    <p className="mb-1 text-sm text-muted-foreground text-center">
                      Click&nbsp;to&nbsp;upload or drag&nbsp;and&nbsp;drop
                    </p>
                  </div> 
                  </FileInput>
                  <FileUploaderContent />
                </FileUploader>
              </div>
              {fileUrls.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium">Uploaded File</h3>
              <div className="space-y-2">
                {fileUrls.map((url, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 p-2 border rounded-lg"
                  >
                    <Paperclip className="h-4 w-4 stroke-current" />
                    <span className="flex-1 truncate">{url}</span>
                    <FileDownloadButton
                      fileID={url}
                      variant="outline"
                      size="sm"
                      downloadName={`File-${index + 1}`}
                      accessToken={""}
                    >
                      View File
                    </FileDownloadButton>
                  </div>
                ))}
              </div>
            </div>
          )}
          <Button 
            className="w-full" 
            disabled={!isFormValid || isSubmitting} 
            onClick={handleConfigureDataset}
            type="button"
          >
            Configure Dataset
          </Button>
          </CardContent>
          </Card>
        </div>
        </form>
        </Form>
        <DatasetConfigurationDialog
          open={isConfigDialogOpen}
          onOpenChange={setIsConfigDialogOpen}
          onComplete={handleConfigComplete}
          onSubmitForm={handleSubmitForm}
        />
    </ContentLayout>
  )
}
