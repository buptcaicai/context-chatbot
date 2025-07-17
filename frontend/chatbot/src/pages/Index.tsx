import { Box, Button, Stack } from "@mui/material";
import { Link } from "react-router-dom";

export default function Index() {
   const buttonStyle = {
      height: "5rem",
      fontSize: "2rem",
      minWidth: "15rem",
      maxWidth: "35rem",
      borderRadius: "1rem",
   };
   return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" mt="20vh">
         <Stack
            spacing={4}
            width="100vw"
            minWidth={"40rem"}
            direction="row"
            justifyContent="space-evenly"
            alignItems="center"
         >
            {/* @ts-ignore */}
            <Button variant="contained" size="large" style={buttonStyle} component={Link} to="/add-documents">
               Add Documents
            </Button>
            {/* @ts-ignore */}
            <Button variant="contained" size="large" color="secondary" style={buttonStyle} component={Link} to="/chat">
               Start Chat
            </Button>
         </Stack>
      </Box>
   );
}
