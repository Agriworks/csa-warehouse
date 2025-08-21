/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { 
  getPresignedUrlGeneratePresignedUrlGet,
  extractCsvDataExtractCsvDataPost,
  createFileEndpointCreateFilePost
} from "@/lib/hey-api/client/sdk.gen";
import { CreateFileResponse, ExtractCsvDataResponse } from "@/lib/hey-api/client/types.gen";
import React, {
  Dispatch,
  SetStateAction,
  forwardRef,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  useDropzone,
  DropzoneState,
  FileRejection,
  DropzoneOptions,
} from "react-dropzone";
import { toast } from "sonner";
import {
  Trash2 as RemoveIcon,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { Paperclip } from "lucide-react";

interface FileRecord {
  fileId: number;
  fileExt: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  fileURI: string;
}

type DirectionOptions = "rtl" | "ltr" | undefined;

type FileUploadStatus = {
  file: File;
  status: "uploading" | "success" | "error";
  error?: string;
};

type FileUploaderProps = {
  value: File[] | null;
  reSelect?: boolean;
  onValueChange: (value: File[] | null) => void;
  onUploadComplete?: (urls: string[], fileData?: {
    dataset_id: string;
    file_id: string;
    columns: string[];
  }) => void;
  dropzoneOptions: DropzoneOptions;
  orientation?: "horizontal" | "vertical";
  authToken: string;
};

interface FileUploaderContentProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: "horizontal" | "vertical";
  value?: File[] | null;
  uploadStatus?: FileUploadStatus[];
  removeFileFromSet?: (index: number) => void;
  activeIndex?: number;
  setActiveIndex?: Dispatch<SetStateAction<number>>;
}

interface FileUploaderItemProps extends React.HTMLAttributes<HTMLDivElement> {
  file: File;
  index: number;
  uploadStatus: FileUploadStatus["status"];
  removeFileFromSet: (index: number) => void;
  activeIndex: number;
  setActiveIndex: Dispatch<SetStateAction<number>>;
  className?: string;
}

interface FileInputProps extends React.HTMLAttributes<HTMLDivElement> {
  dropzoneState?: DropzoneState;
  isFileTooBig?: boolean;
  isLOF?: boolean;
}

export const FileUploader = forwardRef<
  HTMLDivElement,
  FileUploaderProps & React.HTMLAttributes<HTMLDivElement>
>(
  (
    {
      className,
      dropzoneOptions,
      value,
      onValueChange,
      onUploadComplete,
      reSelect,
      orientation = "vertical",
      children,
      dir,
      authToken,
      ...props
    },
    ref,
  ) => {
    const [isFileTooBig, setIsFileTooBig] = useState(false);
    const [isLOF, setIsLOF] = useState(false);
    const [activeIndex, setActiveIndex] = useState(-1);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<FileUploadStatus[]>([]);
    const {
      accept = {
        "text/csv": [".csv"],
      },
      maxFiles = 1,
      maxSize = 4 * 1024 * 1024,
      multiple = false,
    } = dropzoneOptions;

    const reSelectAll = maxFiles === 1 ? true : reSelect;
    const direction: DirectionOptions = dir === "rtl" ? "rtl" : "ltr";

    if (authToken === "") {
      toast.error(
        "file uploader initialization error: unable to set auth credentials",
      );
    }

    const removeFileFromSet = useCallback(
      (i: number) => {
        if (!value) return;
        const newFiles = value.filter((_, index) => index !== i);
        onValueChange(newFiles);
      },
      [value, onValueChange],
    );

    const uploadFile = useCallback(async (file: File) => {
      const formData = new FormData();
      formData.append("files", file);
      formData.append("metadata", JSON.stringify({}));

      try {
        // Add timestamp to filename to prevent duplicates
        const timestamp = new Date().getTime();
        const fileExt = file.name.split(".").pop() || "";
        const fileNameWithoutExt = file.name.slice(0, -(fileExt.length + 1));
        const uniqueFileName = `${fileNameWithoutExt}_${timestamp}.${fileExt}`;

        // Get presigned URL using SDK
        const presignedResponse = await getPresignedUrlGeneratePresignedUrlGet({
          query: {
            filename: uniqueFileName,
          },
        });
        console.log("Presigned response:", presignedResponse);

        if (presignedResponse.error) {
          throw new Error("Failed to get presigned URL");
        }

        const presignedUrl = (presignedResponse.data as { upload_url: string })?.upload_url;
        console.log("Presigned URL response:", presignedUrl);
        console.log("Type of presignedUrl:", typeof presignedUrl);

        // Now upload the file using the presigned URL
        const uploadResponse = await fetch(presignedUrl as string, {
          method: "PUT",
          body: file,
          headers: {
            "Content-Type": file.type,
          },
        });

        if (!uploadResponse.ok) {
          throw new Error("Upload failed");
        }
        console.log("Upload response:", uploadResponse);

        // Extract CSV data after successful upload
        const extractResponse = await extractCsvDataExtractCsvDataPost({
          body: {
            filename: uniqueFileName,
            user_id: "",
            username: "",
          },
        });

        if (extractResponse.error) {
          throw new Error("Failed to extract CSV data");
        }

        console.log("CSV extraction response:", extractResponse.data);
        
        // Get the file URL (remove query parameters from presigned URL)
        const fileUrl = presignedUrl.split("?")[0];

        // Store file record in database and get file ID
        const recordResponse = await createFileEndpointCreateFilePost({
          body: {
            file_ext: fileExt,
            file_name: uniqueFileName,
            file_size: file.size,
            file_type: file.type,
            file_url: fileUrl,
          },
        });

        if (recordResponse.error) {
          throw new Error("Failed to record file metadata");
        }

        const recordData = recordResponse.data as CreateFileResponse;
        console.log("File record data:", recordData);
        
        // Extract dataset_id and columns from the CSV extraction response
        const extractData = extractResponse.data as ExtractCsvDataResponse;
        const dataset_id = extractData.data?.dataset_id as string || "";
        const columns = extractData.data?.columns as string[] || [];
        const file_id = recordData?.data?.id || "";
        
        // Return both the file ID and the extracted data
        return {
          file_id,
          dataset_id,
          columns,
        };
      } catch (error) {
        console.error("Upload error:", error);
        throw error;
      }
    }, []);

    const onDrop = useCallback(
      async (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
        const files = acceptedFiles;

        if (!files) {
          toast.error("file error , probably too big");
          return;
        }

        const newValues: File[] = value ? [...value] : [];

        if (reSelectAll) {
          newValues.splice(0, newValues.length);
        }

        files.forEach((file) => {
          if (newValues.length < maxFiles) {
            newValues.push(file);
          }
        });

        onValueChange(newValues);

        // Initialize upload status for new files
        const newUploadStatus = newValues.map((file) => ({
          file,
          status: "uploading" as const,
        }));
        setUploadStatus(newUploadStatus);

        // Upload files and get URLs
        if (onUploadComplete) {
          setUploading(true);
          try {
            const uploadPromises = newValues.map(async (file, index) => {
              try {
                const fileData = await uploadFile(file);
                setUploadStatus((prev) =>
                  prev.map((status, i) =>
                    i === index ? { ...status, status: "success" } : status,
                  ),
                );
                return fileData;
              } catch (error) {
                setUploadStatus((prev) =>
                  prev.map((status, i) =>
                    i === index
                      ? { ...status, status: "error", error: "Upload failed" }
                      : status,
                  ),
                );
                throw error;
              }
            });

            const fileDataArray = await Promise.all(uploadPromises);
            // Filter out any undefined values and extract URLs and file data
            const validFileData = fileDataArray.filter(
              (data): data is { file_id: string; dataset_id: string; columns: string[] } => 
                data !== undefined && data.file_id !== undefined && data.file_id !== "",
            );
            
            // Extract URLs for backward compatibility
            const urls = validFileData.map(data => data.file_id);
            
            // Pass both URLs and file data to the callback
            onUploadComplete(urls, validFileData[0]); // For single file upload, pass the first file data
          } catch (error) {
            console.error("Upload failed:", error);
            toast.error("Some files failed to upload");
          } finally {
            setUploading(false);
          }
        }

        if (rejectedFiles.length > 0) {
          for (let i = 0; i < rejectedFiles.length; i++) {
            if (rejectedFiles[i].errors[0]?.code === "file-too-large") {
              toast.error(
                `File is too large. Max size is ${maxSize / 1024 / 1024}MB`,
              );
              break;
            }
            if (rejectedFiles[i].errors[0]?.message) {
              toast.error(rejectedFiles[i].errors[0].message);
              break;
            }
          }
        }
      },
      [
        reSelectAll,
        value,
        onUploadComplete,
        maxFiles,
        maxSize,
        onValueChange,
        uploadFile,
      ],
    );

    const opts = dropzoneOptions
      ? dropzoneOptions
      : { accept, maxFiles, maxSize, multiple };

    const dropzoneState = useDropzone({
      ...opts,
      onDrop, // Use the actual onDrop callback here
      onDropRejected: () => setIsFileTooBig(true),
      onDropAccepted: () => setIsFileTooBig(false),
    });

    const handleKeyDown = useCallback(
      (e: React.KeyboardEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();

        if (!value) return;

        const moveNext = () => {
          const nextIndex = activeIndex + 1;
          setActiveIndex(nextIndex > value.length - 1 ? 0 : nextIndex);
        };

        const movePrev = () => {
          const nextIndex = activeIndex - 1;
          setActiveIndex(nextIndex < 0 ? value.length - 1 : nextIndex);
        };

        const prevKey =
          orientation === "horizontal"
            ? direction === "ltr"
              ? "ArrowLeft"
              : "ArrowRight"
            : "ArrowUp";

        const nextKey =
          orientation === "horizontal"
            ? direction === "ltr"
              ? "ArrowRight"
              : "ArrowLeft"
            : "ArrowDown";

        if (e.key === nextKey) {
          moveNext();
        } else if (e.key === prevKey) {
          movePrev();
        } else if (e.key === "Enter" || e.key === "Space") {
          if (activeIndex === -1) {
            dropzoneState.inputRef.current?.click();
          }
        } else if (e.key === "Delete" || e.key === "Backspace") {
          if (activeIndex !== -1) {
            removeFileFromSet(activeIndex);
            if (value.length - 1 === 0) {
              setActiveIndex(-1);
              return;
            }
            movePrev();
          }
        } else if (e.key === "Escape") {
          setActiveIndex(-1);
        }
      },
      [value, activeIndex, removeFileFromSet, direction, orientation, dropzoneState],
    );

    useEffect(() => {
      if (!value) return;
      if (value.length === maxFiles) {
        setIsLOF(true);
        return;
      }
      setIsLOF(false);
    }, [value, maxFiles]);

    // Clone children and pass props to FileUploaderContent and FileInput
    const childrenWithProps = React.Children.map(children, (child) => {
      if (React.isValidElement(child)) {
        if (child.type === FileUploaderContent) {
          return React.cloneElement(child as React.ReactElement<FileUploaderContentProps>, {
            orientation,
            value,
            uploadStatus,
            removeFileFromSet,
            activeIndex,
            setActiveIndex,
          });
        }
        if (child.type === FileInput) {
          return React.cloneElement(child as React.ReactElement<FileInputProps>, {
            dropzoneState,
            isFileTooBig,
            isLOF,
          });
        }
      }
      return child;
    });

    return (
      <div
        ref={ref}
        tabIndex={0}
        onKeyDownCapture={handleKeyDown}
        className={cn(
          "grid w-full focus:outline-none overflow-hidden ",
          className,
          {
            "gap-2": value && value.length > 0,
          },
        )}
        dir={dir}
        {...props}
      >
        {childrenWithProps}
      </div>
    );
  },
);

FileUploader.displayName = "FileUploader";

export const FileUploaderContent = forwardRef<
  HTMLDivElement,
  FileUploaderContentProps
>(({ children, className, orientation = "vertical", value = null, uploadStatus = [], removeFileFromSet, activeIndex = -1, setActiveIndex, ...props }, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div
      className={cn("w-full px-1")}
      ref={containerRef}
      aria-description="content file holder"
    >
      <div
        {...props}
        ref={ref}
        className={cn(
          "flex rounded-xl gap-1",
          orientation === "horizontal" ? "flex-raw flex-wrap" : "flex-col",
          className,
        )}
      >
        {value &&
          value.length > 0 &&
          value.map((file, i) => {
            const status = uploadStatus[i];
            return (
              <FileUploaderItem
                key={i}
                file={file}
                index={i}
                uploadStatus={status?.status || "uploading"}
                removeFileFromSet={removeFileFromSet!}
                activeIndex={activeIndex}
                setActiveIndex={setActiveIndex!}
              />
            );
          })}
        {children}
      </div>
    </div>
  );
});

FileUploaderContent.displayName = "FileUploaderContent";

export const FileUploaderItem = ({
  file,
  index,
  uploadStatus,
  removeFileFromSet,
  activeIndex,
  setActiveIndex,
  className,
  ...props
}: FileUploaderItemProps) => {
  return (
    <div
      role="button"
      tabIndex={0}
      className={cn(
        "group relative flex items-center justify-between gap-2 rounded-lg border p-2 text-sm",
        activeIndex === index && "ring-2 ring-primary",
        className,
      )}
      onClick={() => setActiveIndex(index)}
      {...props}
    >
      <div className="flex items-center gap-2 overflow-hidden">
        <Paperclip className="h-4 w-4 shrink-0" />
        <span
          className="truncate"
          style={{ maxWidth: "180px" }}
          title={file.name}
        >
          {file.name}
        </span>
      </div>
      <div className="flex items-center gap-2">
        {uploadStatus === "uploading" && (
          <Loader2 className="h-4 w-4 animate-spin" />
        )}
        {uploadStatus === "success" && (
          <CheckCircle2 className="h-4 w-4 text-green-500" />
        )}
        {uploadStatus === "error" && (
          <AlertCircle className="h-4 w-4 text-red-500" />
        )}
        <button
          type="button"
          aria-label="Remove file"
          onClick={(e) => {
            e.stopPropagation();
            removeFileFromSet(index);
          }}
          className="ml-auto rounded-md p-1 hover:bg-destructive/90 hover:text-destructive-foreground"
        >
          <RemoveIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

FileUploaderItem.displayName = "FileUploaderItem";

export const FileInput = forwardRef<
  HTMLDivElement,
  FileInputProps
>(({ className, children, dropzoneState, isFileTooBig = false, isLOF = false, ...props }, ref) => {
  // If dropzoneState is not provided, create a fallback (this shouldn't happen in normal usage)
  if (!dropzoneState) {
    console.warn("FileInput: dropzoneState not provided. Component may not function correctly.");
    return (
      <div ref={ref} {...props} className={className}>
        {children}
      </div>
    );
  }

  const rootProps = isLOF ? {} : dropzoneState.getRootProps();
  return (
    <div
      ref={ref}
      {...props}
      className={`relative w-full ${isLOF ? "opacity-50 cursor-not-allowed " : "cursor-pointer "
        }`}
    >
      <div
        className={cn(
          `w-full rounded-lg duration-300 ease-in-out
         ${dropzoneState.isDragAccept
            ? "border-green-500"
            : dropzoneState.isDragReject || isFileTooBig
              ? "border-red-500"
              : "border-gray-300"
          }`,
          className,
        )}
        {...rootProps}
      >
        {children}
      </div>
      <Input
        ref={dropzoneState.inputRef}
        disabled={isLOF}
        {...dropzoneState.getInputProps()}
        className={`${isLOF ? "cursor-not-allowed" : ""}`}
      />
    </div>
  );
});

FileInput.displayName = "FileInput";