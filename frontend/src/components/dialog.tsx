import { cn } from "@/lib/utils";
import { Button } from "./ui/button";
import { X } from "lucide-react";

export default function Dialog({
  className,
  isOpen,
  onClose,
  dialogTitle,
  dialogDescription,
  children,
}: Readonly<{
  className?: string;
  isOpen: boolean;
  onClose: () => void;
  dialogTitle?: string;
  dialogDescription?: string;
  children: React.ReactNode;
}>) {
  return (
    <div
      className={cn(
        "fixed w-screen h-screen overflow-hidden z-[999] bg-background/50 backdrop-blur top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2",
        isOpen ? "fixed" : "hidden",
      )}
    >
      <div className="h-screen w-screen flex justify-center items-center">
        <div
          className={cn(
            "h-fit max-h-[95vh] overflow-y-scroll w-[320px] sm:w-[500px] md:w-[700px] border border-md px-8 pb-8 rounded-lg shadow-md bg-background",
            className,
          )}
        >
          <div className="flex justify-between items-start mb-4 pt-8 pb-4 sticky top-0 bg-background border-b z-[99999]">
            <div className="space-y-2">
              <h3 className="font-semibold text-2xl">{dialogTitle}</h3>
              <p className="text-muted-foreground text-sm">
                {dialogDescription}
              </p>
            </div>
            <Button size="icon" variant="ghost" onClick={onClose}>
              <X />
            </Button>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}