import { cn } from "@/lib/utils";

interface DataTableColumnHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
}

export function DataTableColumnHeader({
  title,
  className,
}: DataTableColumnHeaderProps) {
  return (
    <div 
      className={cn("flex items-center space-x-2 whitespace-nowrap overflow-hidden text-ellipsis", className)}
      title={title}
    >
      {title}
    </div>
  );
}
