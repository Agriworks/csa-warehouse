import React from "react";
import { Button, ButtonProps } from "../ui/button";
import { Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "../hooks/use-toast";

export interface FileDownloadButtonProps extends Omit<ButtonProps, 'onClick'> {
    fileID: string | undefined; // Allow undefined for cases where fileID is not yet available
    downloadName: string;
    accessToken: string;
    children?: React.ReactNode; // Replace buttonText with children
}

const FileDownloadButton = React.forwardRef<HTMLButtonElement, FileDownloadButtonProps>(
    ({ fileID, downloadName, accessToken, children, className, variant = "outline", size, ...props }, ref) => {
        const theToast = useToast();

        const handleDownload = async () => {
            try {
                // If accessToken is "", show an error toast
                if (!accessToken || accessToken === "") {
                    console.error("No access token provided");
                    theToast.toast({
                        title: "Error",
                        description: "No authorization information found, aborting download",
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

                // // Get the download URL from the API
                // const response = await getNimbusFileDownloadUrl({
                //     path: {
                //         fileId: fileID,
                //     },
                //     headers: {
                //         Authorization: `Bearer ${accessToken}`,
                //     },
                // });

                const response = {
                    data: "https://example.com/file.csv",
                };

                if (response.data) {
                    window.open(response.data as string, "_blank");
                } else {
                    theToast.toast({
                        title: "Error",
                        description: "Failed to get file download URL",
                        variant: "destructive",
                    });
                    console.error("No download URL received");
                    throw new Error("No download URL received");
                }
            } catch (error) {
                console.error("Error getting file download URL:", error);
                theToast.toast({
                    title: "Error",
                    description: "Failed to get file download URL",
                    variant: "destructive",
                });
            }
        };

        return (
            <Button
                ref={ref}
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
    }
);

FileDownloadButton.displayName = "FileDownloadButton";

export default FileDownloadButton;