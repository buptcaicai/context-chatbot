import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./route.tsx";
import { loadConfigFromS3 } from "./resource/config_from_s3.ts";

loadConfigFromS3();

createRoot(document.getElementById("root")!).render(
   <StrictMode>
      <RouterProvider router={router} />
   </StrictMode>
);

