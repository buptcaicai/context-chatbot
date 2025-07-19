import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import ErrorPage from "./pages/ErrorPage";
import AddDoc from "./pages/AddDoc";
import Chat from "./pages/Chat";
import Index from "./pages/Index";
import { userLoader as ingestedFilesLoader } from "./pages/AddDoc";

export const router = createBrowserRouter([
   {
      errorElement: <ErrorPage />,
      Component: App,
      children: [
         {
            path: "/",
            Component: Index,
         },
         {
            path: "/add-documents",
            Component: AddDoc,
            loader: ingestedFilesLoader,
         },
         {
            path: "/chat",
            Component: Chat,
         },
      ],
   },
]);
