import { useState, useRef } from "react";
import { Box, Button, Typography, Paper } from "@mui/material";
import { CloudUpload } from "@mui/icons-material";
import { useLoaderData } from "react-router-dom";

export async function userLoader() {
   const response = await fetch(`${import.meta.env.VITE_REMOTE_ENDPOINT}/files/get-file-injested`);
   if (!response.ok) throw new Error("Failed to fetch user");
   return (await response.json()).message;
}

export default function AddDoc() {
   const [files, setFiles] = useState<File[]>([]);
   const [dragOver, setDragOver] = useState(false);
   const fileInputRef = useRef<HTMLInputElement | null>(null);
   const [error, setError] = useState<string | null>(null);
   const [success, setSuccess] = useState<string | null>(null);
   const ingestedFiles = useLoaderData<string[]>();
   console.log("ingestedFiles", ingestedFiles);

   // Allowed file types and max size (5MB)
   const allowedTypes = ["text/plain"];
   const maxSize = 5 * 1024 * 1024; // 5MB in bytes

   // Handle file selection via input
   const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      if (!event.target.files) return;
      const selectedFiles = Array.from(event.target.files);
      processFiles(selectedFiles);
   };

   // Handle drag-and-drop files
   const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragOver(false);
      const droppedFiles = Array.from(event.dataTransfer.files);
      processFiles(droppedFiles);
   };

   // Process and validate files
   const processFiles = (selectedFiles: File[]) => {
      const validFiles = selectedFiles.filter((file) => {
         if (!allowedTypes.includes(file.type)) {
            setError(`File "${file.name}" is not an allowed type. Only text/plain are allowed.`);
            return false;
         }
         if (file.size > maxSize) {
            setError(`File "${file.name}" exceeds 5MB limit.`);
            return false;
         }
         return true;
      });
      setFiles(validFiles);
   };

   // Handle drag-over event
   const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragOver(true);
   };

   // Handle drag-leave event
   const handleDragLeave = () => {
      setDragOver(false);
   };

   // Trigger file input click
   const handleButtonClick = () => {
      if (!fileInputRef.current) return;
      fileInputRef.current.click();
   };

   // Handle upload (placeholder for API call)
   const handleUpload = async () => {
      if (files.length === 0) {
         setError("No files selected.");
         return;
      }
      // Example: Send files to a server
      console.log("Uploading files:", files);
      // Reset files after upload
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      try {
         const response = await fetch(`${import.meta.env.VITE_REMOTE_ENDPOINT}/files/upload`, {
            method: "POST",
            body: formData,
         });

         if (!response.ok) {
            throw new Error("Upload failed");
         }

         const result = await response.json();
         setSuccess(result.message || "Files uploaded successfully!");
         setFiles([]);
         if (fileInputRef.current) {
            fileInputRef.current.value = "";
         }
      } catch (error) {
         setError("Failed to upload files. Please try again.");
         console.error("Upload error:", error);
      }

      setFiles([]);
      if (fileInputRef.current) {
         fileInputRef.current.value = "";
      }
   };

   return (
      <Box sx={{ maxWidth: 500, mx: "auto", p: 3 }}>
         <Paper
            elevation={3}
            sx={{
               p: 3,
               border: `2px dashed ${dragOver ? "#1976d2" : "#ccc"}`,
               borderRadius: "8px",
               textAlign: "center",
               bgcolor: dragOver ? "rgba(25, 118, 210, 0.1)" : "background.paper",
               transition: "all 0.3s ease",
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
         >
            <CloudUpload sx={{ fontSize: 48, color: "primary.main", mb: 2 }} />
            <Typography variant="h6" gutterBottom>
               Drag and Drop Files Here
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
               or
            </Typography>
            <Button variant="contained" color="primary" onClick={handleButtonClick} sx={{ mb: 2 }}>
               Select Files
            </Button>
            <input
               type="file"
               multiple
               accept="text/plain"
               onChange={handleFileChange}
               ref={fileInputRef}
               style={{ display: "none" }}
            />
            {files.length > 0 && (
               <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1">Selected Files:</Typography>
                  {files.map((file, index) => (
                     <Typography key={index} variant="body2">
                        {file.name} ({(file.size / 1024).toFixed(2)} KB)
                     </Typography>
                  ))}
                  <Button variant="contained" color="secondary" onClick={handleUpload} sx={{ mt: 2 }}>
                     Upload Files
                  </Button>
               </Box>
            )}
            {error && (
               <Typography variant="body2" color="error">
                  {error}
               </Typography>
            )}
            {success && (
               <Typography variant="body2" color="success">
                  {success}
               </Typography>
            )}
         </Paper>
         <Box sx={{ mt: 4, textAlign: "left" }}>
            <Typography variant="h6" gutterBottom>
               Already Ingested Files
            </Typography>
            {/* Replace the following array with your actual ingested files data */}
            {Array.isArray(ingestedFiles) && ingestedFiles.length > 0 ? (
               <Box component="ul" sx={{ pl: 2, mb: 0 }}>
                  {ingestedFiles.map((s) => {
                     const [filename, filesize] = s.split("::");
                     return { filename, filesize };
                  }).map((file: { filename: string; filesize: string }, idx: number) => (
                     <li key={idx}>
                        <Typography variant="body2">
                           {file.filename} ({(parseInt(file.filesize) / 1024).toFixed(2)} KB)
                        </Typography>
                     </li>
                  ))}
               </Box>
            ) : (
               <Typography variant="body2" color="text.secondary">
                  No files have been ingested yet.
               </Typography>
            )}
         </Box>
      </Box>
   );
}
