import { Box } from "@mui/material";
import { useLocation } from "react-router-dom";

export default function Banner() {
   const location = useLocation();
   console.log("location.pathname", location.pathname);
   return (
      <Box
         width="40vw"
         bgcolor="primary.light"
         color="primary.contrastText"
         py={3}
         textAlign="center"
         boxShadow={2}
         ml="30vw"
         mr="30vw"
         mt="20vh"
         borderRadius="8rem"
         sx={
            location.pathname !== "/"
               ? {
                    animation: "moveToTopLeft 1s forwards",
                    "@keyframes moveToTopLeft": {
                       "0%": {
                          width: "40vw",
                          mt: "20vh",
                          transform: "translate(0, 0)",
                       },
                       "100%": {
                          width: "20vw",
                          mt: "5vh",
                          transform: "translate(-25vw, 0)", // Moves to top-left (5vw, 5vh)
                       },
                    },
                 }
               : {
                    // Reset animation for "/" route
                    animation: "resetPosition 1.5s forwards",
                    "@keyframes resetPosition": {
                       "0%": {
                          width: "20vw",
                          mt: "5vh",
                          transform: "translate(-25vw, 0)",
                       },
                       "100%": { 
                          width: "40vw",
                          mt: "20vh",
                          transform: "translate(0, 0)",
                       },
                    },
                 }
         }
      >
         <span style={{ fontSize: "2rem", fontWeight: 600, letterSpacing: "0.05em" }}>ChatBot</span>
      </Box>
   );
}
