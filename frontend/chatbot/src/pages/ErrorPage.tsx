import { useNavigate, useRouteError } from "react-router-dom";

export default function () {
   const error = useRouteError();
   const navigate = useNavigate();

   return (
      <div
         style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100vh",
            width: "100vw",
            padding: "20px",
            fontFamily: "Arial, sans-serif",
         }}
      >
         <h1 style={{ color: "#e74c3c", marginBottom: "20px" }}>Oops! Something went wrong</h1>
         <div
            style={{
               backgroundColor: "#f8f9fa",
               padding: "20px",
               borderRadius: "8px",
               marginBottom: "30px",
               maxWidth: "500px",
               textAlign: "center",
            }}
         >
            <p style={{ marginBottom: "10px", color: "#6c757d" }}>
               {error instanceof Error ? error.message : "An unexpected error occurred"}
            </p>
            {error instanceof Error && error.stack && (
               <details style={{ textAlign: "left", marginTop: "15px" }}>
                  <summary style={{ cursor: "pointer", color: "#495057" }}>Show error details</summary>
                  <pre
                     style={{
                        backgroundColor: "#e9ecef",
                        padding: "10px",
                        borderRadius: "4px",
                        fontSize: "12px",
                        overflow: "auto",
                        marginTop: "10px",
                     }}
                  >
                     {error.stack}
                  </pre>
               </details>
            )}
         </div>
         <button
            onClick={() => navigate("/")}
            style={{
               backgroundColor: "#007bff",
               color: "white",
               border: "none",
               padding: "12px 24px",
               borderRadius: "6px",
               fontSize: "16px",
               cursor: "pointer",
               transition: "background-color 0.2s",
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#0056b3")}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#007bff")}
         >
            Go to Home
         </button>
      </div>
   );
}
