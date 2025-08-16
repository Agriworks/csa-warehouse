'use client'

import Dialog from '@/components/dialog'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
  Form,
} from '@/components/ui/form'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { useState } from 'react'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

// --- Zod Schema ---
const datasetConfigSchema = z.object({
  isSpatial: z.boolean(),
  isTemporal: z.boolean(),
  hasLatitude: z.boolean(),
  hasLongitude: z.boolean(),
  district: z.string().optional(),
  mandal: z.string().optional(),
  wardNo: z.string().optional(),
})

type DatasetConfigFormType = z.infer<typeof datasetConfigSchema>

// --- Types ---
export interface DatasetConfigFormData {
  isSpatial: boolean
  isTemporal: boolean
  hasLatitude: boolean
  hasLongitude: boolean
  district?: string
  mandal?: string
  wardNo?: string
}

interface DatasetConfigDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onComplete: (data: DatasetConfigFormData) => void
  onSubmitForm?: (configData: DatasetConfigFormData) => void
}

// --- Progress Step Component ---
interface ProgressStepProps {
  step: number
  currentStep: number
  title: string
  isCompleted: boolean
  showConnector: boolean
}

function ProgressStep({ step, currentStep, title, isCompleted, showConnector }: ProgressStepProps) {
  const isCurrent = step === currentStep
  const isCompletedStep = isCompleted || step < currentStep
  
  return (
    <div className="flex flex-row items-center flex-1">
      <div className="flex flex-row items-center justify-center">
        <div 
          className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-200",
            isCompletedStep 
              ? "bg-primary text-primary-foreground" 
              : isCurrent 
                ? "bg-primary/20 text-primary border-2 border-primary" 
                : "bg-muted text-muted-foreground"
          )}
        >
          {isCompletedStep ? <Check className="w-4 h-4" /> : step + 1}
        </div>
        <span 
          className={cn(
            "ml-2 text-xs font-medium transition-colors duration-200 whitespace-nowrap",
            isCompletedStep 
              ? "text-primary" 
              : isCurrent 
                ? "text-foreground" 
                : "text-muted-foreground"
          )}
        >
          {title}
        </span>
      </div>
      {showConnector && (
        <div 
          className={cn(
            "flex-1 h-px mx-4",
            isCompletedStep ? "bg-primary" : "bg-border"
          )} 
        />
      )}
    </div>
  )
}

// --- Main Dialog Component ---
export function DatasetConfigurationDialog({
  open,
  onOpenChange,
  onComplete,
  onSubmitForm,
}: DatasetConfigDialogProps) {
  const [currentStep, setCurrentStep] = useState(0)

  // --- React Hook Form ---
  const form = useForm<DatasetConfigFormType>({
    resolver: zodResolver(datasetConfigSchema),
    defaultValues: {
      isSpatial: false,
      isTemporal: false,
      hasLatitude: false,
      hasLongitude: false,
      district: '',
      mandal: '',
      wardNo: '',
    },
  })

  // --- Handlers ---
  const handleNext = () => {
    if (currentStep < 2) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async (data: DatasetConfigFormType) => {
    try {
      console.log('Dataset Configuration Data:', data)
      onComplete(data)
      if (onSubmitForm) {
        await onSubmitForm(data)
      }
      onOpenChange(false)
      setCurrentStep(0) // Reset step when closing
    } catch (error) {
      console.error('Error submitting form:', error)
    }
  }

  const handleClose = () => {
    onOpenChange(false)
    setCurrentStep(0) // Reset step when closing
  }

  // --- Progress Steps ---
  const steps = [
    { id: 0, title: 'Time/Location Data Checking' },
    { id: 1, title: 'Select Data Column' },
    { id: 2, title: 'Select Granularity' },
  ]

  // --- Step Content ---
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-3">
            <div className="border border-border rounded-lg p-2">
              <FormField
                control={form.control}
                name="isTemporal"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox
                        id="isTemporal"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <FormLabel htmlFor="isTemporal" className="text-sm font-medium">
                      My Dataset Contains Time Data
                    </FormLabel>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="border border-border rounded-lg p-2">
              <FormField
                control={form.control}
                name="isSpatial"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox
                        id="isSpatial"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <FormLabel htmlFor="isSpatial" className="text-sm font-medium">
                      My Dataset Contains Location Data
                    </FormLabel>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
        )
      case 1:
        return (
          <div className="space-y-3">
            <div className="border border-border rounded-lg p-2">
              <FormField
                control={form.control}
                name="isTemporal"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox
                        id="isTemporal"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <FormLabel htmlFor="isTemporal" className="text-sm font-medium">
                      Time
                    </FormLabel>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="border border-border rounded-lg p-2">
              <FormField
                control={form.control}
                name="isSpatial"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox
                        id="isSpatial"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <FormLabel htmlFor="isSpatial" className="text-sm font-medium">
                      Location
                    </FormLabel>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="border border-border rounded-lg p-2">
              <FormField
                control={form.control}
                name="hasLatitude"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox
                        id="hasLatitude"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <FormLabel htmlFor="hasLatitude" className="text-sm font-medium">
                      Latitude
                    </FormLabel>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="border border-border rounded-lg p-2">
              <FormField
                control={form.control}
                name="hasLongitude"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox
                        id="hasLongitude"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <FormLabel htmlFor="hasLongitude" className="text-sm font-medium">
                      Longitude
                    </FormLabel>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
        )
      case 2:
        return (
          <div className="space-y-3">
            <div className="border border-border rounded-lg p-2">
              <FormField
                control={form.control}
                name="isSpatial"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox
                        id="location-checkbox"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <FormLabel htmlFor="location-checkbox" className="text-sm font-medium">
                      Location
                    </FormLabel>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <div className="space-y-3 pl-6">
              <FormField
                control={form.control}
                name="district"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      District *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="District"
                        className="w-full"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="mandal"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      Mandal *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Mandal"
                        className="w-full"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="wardNo"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      Ward No *
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Ward No"
                        className="w-full"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
        )
      default:
        return null
    }
  }

  // --- UI ---
  return (
    <Dialog
      isOpen={open}
      onClose={handleClose}
      dialogTitle="Dataset Configuration"
      dialogDescription="Configure your dataset settings"
      className="w-full max-w-7xl max-h-[80vh] overflow-y-auto"
    >
      {/* Progress Indicator */}
      <div className="mt-6 mb-6">
        <div className="border border-border rounded-lg p-3 bg-card">
          <div className="flex items-center justify-between gap-2">
            {steps.map((step, index) => (
              <ProgressStep
                key={step.id}
                step={step.id}
                currentStep={currentStep}
                title={step.title}
                isCompleted={currentStep > step.id}
                showConnector={index < steps.length - 1}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {renderStepContent()}
            
            <div className="flex items-center justify-start space-x-2 pt-4">
              {currentStep > 0 && (
                <Button 
                  variant="outline" 
                  type="button" 
                  onClick={handleBack}
                  className="bg-background text-foreground border-border hover:bg-muted"
                >
                  Back
                </Button>
              )}
              {currentStep < 2 ? (
                <Button 
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    handleNext();
                  }}
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  Continue
                </Button>
              ) : (
                <Button 
                  type="submit"
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  Save and Upload
                </Button>
              )}
            </div>
          </form>
        </Form>
      </div>
    </Dialog>
  );
}
