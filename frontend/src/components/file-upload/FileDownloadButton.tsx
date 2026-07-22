import React from "react";
import { Button, ButtonProps } from "../ui/button";
import { Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "../hooks/use-toast";

export interface FileDownloadButtonProps extends Omit<ButtonProps, "onClick"> {
  fileID: string | null;
  downloadName: string;
  accessToken: string;
  children?: React.ReactNode; // Replace buttonText with children
}

const FileDownloadButton = React.forwardRef<
  HTMLButtonElement,
  FileDownloadButtonProps
>(
  (
    {
      fileID,
      downloadName,
      accessToken,
      children,
      className,
      variant = "outline",
      size,
      ...props
    },
    ref,
  ) => {
    const theToast = useToast();

    const handleDownload = async (e: React.MouseEvent<HTMLButtonElement>) => {
      e.preventDefault();
      try {
        // If accessToken is "", show an error toast
        if (!accessToken || accessToken === "") {
          console.error("No access token provided");
          theToast.toast({
            title: "Error",
            description:
              "No authorization information found, aborting download",
            variant: "destructive",
          });
          return;
        }

        if (!fileID) {
          console.error("No file ID provided");
          theToast.toast({
            title: "Error",
            description: "No file ID provided, aborting download",
            variant: "destructive",
          });
          return;
        }

        // Direct download from FastAPI backend to bypass browser CORS / PNA / SSL restrictions
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
        const downloadResponse = await fetch(`${backendUrl}/files/${fileID}/view`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        if (!downloadResponse.ok) {
          const errorText = await downloadResponse.text();
          throw new Error(errorText || `Download request failed: ${downloadResponse.statusText}`);
        }

        const blob = await downloadResponse.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = downloadName.endsWith(".csv") ? downloadName : `${downloadName}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(blobUrl);
      } catch (error) {
        console.error("Error downloading file:", error);
        theToast.toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to download file",
          variant: "destructive",
        });
      }
    };

    return (
      <Button
        ref={ref}
        type="button"
        variant={variant}
        size={size}
        className={cn("w-full", className)}
        onClick={handleDownload}
        {...props}
      >
        {children || (
          <>
            <Download className="h-4 w-4" />
            {`Download ${downloadName}`}
          </>
        )}
      </Button>
    );
  },
);

FileDownloadButton.displayName = "FileDownloadButton";

export default FileDownloadButton;
