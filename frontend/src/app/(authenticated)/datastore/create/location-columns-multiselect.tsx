'use client'

import { cn } from '@/lib/utils'
import {
  MultiSelector,
  MultiSelectorTrigger,
  MultiSelectorInput,
  MultiSelectorContent,
  MultiSelectorList,
  MultiSelectorItem,
} from '@/components/ui/multi-select'

type LocationColumnsMultiSelectProps = {
  columns: string[]
  value: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export default function LocationColumnsMultiSelect({
  columns,
  value,
  onChange,
  placeholder = 'Select location columns...'
  ,
  disabled = false,
  className,
}: LocationColumnsMultiSelectProps) {
  const selectedValues = Array.isArray(value) ? value : []

  return (
    <div className={cn('relative', disabled && 'pointer-events-none opacity-60', className)}>
      <MultiSelector
        values={selectedValues}
        onValuesChange={onChange}
        className="w-full"
      >
        <MultiSelectorTrigger className="w-full">
          <MultiSelectorInput placeholder={placeholder} className="p-2" />
        </MultiSelectorTrigger>
        <MultiSelectorContent>
          <MultiSelectorList>
            {columns.map((col) => (
              <MultiSelectorItem key={col} value={col}>
                {col}
              </MultiSelectorItem>
            ))}
          </MultiSelectorList>
        </MultiSelectorContent>
      </MultiSelector>
    </div>
  )
}


