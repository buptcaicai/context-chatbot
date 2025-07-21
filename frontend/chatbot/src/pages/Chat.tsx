import React, { useState, useEffect, useRef, useCallback } from "react";
import {
   Box,
   TextField,
   Button,
   Paper,
   Typography,
   Container,
   IconButton,
   Avatar,
   List,
   ListItem,
   ListItemText,
   ListItemAvatar,
   Divider,
   CircularProgress,
} from "@mui/material";
import { Send as SendIcon, SmartToy as BotIcon, Person as PersonIcon } from "@mui/icons-material";

interface Message {
   content: string;
   sender: "user" | "bot";
}

export default function Chat() {
   const [messages, setMessages] = useState<Message[]>([]);
   const [query, setQuery] = useState("");
   const [isConnected, setIsConnected] = useState(false);
   const messagesEndRef = useRef<HTMLDivElement>(null);
   const eventSourceRef = useRef<EventSource | null>(null);

   // Auto-scroll to bottom when new messages arrive
   const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
   };

   useEffect(() => {
      scrollToBottom();
   }, [messages]);

   const connectSSE = useCallback(() => {
      try {
         // Replace with your actual SSE endpoint
         const eventSource = new EventSource(
            `${import.meta.env.VITE_REMOTE_ENDPOINT}/chat/start?query=${encodeURIComponent(query)}`
         );
         eventSourceRef.current = eventSource;

         eventSource.onopen = () => {
            setIsConnected(true);
            console.log("SSE connection established");
         };

         eventSource.onmessage = (event) => {
            try {
               const data = JSON.parse(event.data);
               if (data.status === "completed") {
                  // Stream has ended gracefully
                  eventSource.close();
                  // Handle completion logic here
               } else {
                  // Handle regular message
                  setMessages((prev) => [...prev, data.message]);
               }
            } catch (error) {
               console.error("Error parsing SSE message:", error);
            }
         };

         eventSource.onerror = (error) => {
            console.error("SSE connection error:", error);
            setIsConnected(false);
            eventSource.close();
         };

         return () => {
            eventSource.close();
         };
      } catch (error) {
         console.error("Failed to establish SSE connection:", error);
         setIsConnected(false);
      }
   }, [query]);

   const handleKeyPress = (event: React.KeyboardEvent) => {
      if (event.key === "Enter" && !event.shiftKey) {
         event.preventDefault();
         connectSSE();
      }
   };

   return (
      <Container
         maxWidth="md"
         sx={{
            height: "80vh",
            py: 2,
            animation: "growUp 1s forwards",
            "@keyframes growUp": {
               "0%": {
                  height: "40vh",
                  mt: "20vh",
               },
               "100%": {
                  height: "80vh",
                  mt: "0vh",
               },
            },
         }}
      >
         <Paper
            elevation={3}
            sx={{
               height: "100%",
               display: "flex",
               flexDirection: "column",
               borderRadius: 2,
            }}
         >
            {/* Header */}
            <Box
               sx={{
                  p: 2,
                  borderBottom: 1,
                  borderColor: "divider",
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
               }}
            >
               <BotIcon color="primary" />
               <Typography variant="h6" component="h1">
                  AI Chat Assistant
               </Typography>
               <Box sx={{ ml: "auto", display: "flex", alignItems: "center", gap: 1 }}>
                  <Box
                     sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        backgroundColor: isConnected ? "success.main" : "error.main",
                     }}
                  />
                  <Typography variant="caption" color="text.secondary">
                     {isConnected ? "Connected" : "Disconnected"}
                  </Typography>
               </Box>
            </Box>

            <Box
               sx={{
                  flex: 1,
                  overflow: "auto",
                  p: 2,
                  backgroundColor: "grey.50",
               }}
            >
               {messages.length === 0 ? (
                  <Box
                     sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        height: "100%",
                        color: "text.secondary",
                     }}
                  >
                     <BotIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                     <Typography variant="h6" gutterBottom>
                        Welcome to the AI Chat!
                     </Typography>
                     <Typography variant="body2" textAlign="center">
                        Start a conversation by typing a message below.
                     </Typography>
                  </Box>
               ) : (
                  <List sx={{ p: 0 }}>
                     {messages.map((message, index) => (
                        <React.Fragment key={index}>
                           <ListItem
                              sx={{
                                 flexDirection: "column",
                                 alignItems: message.sender === "user" ? "flex-end" : "flex-start",
                                 px: 0,
                              }}
                           >
                              <Box
                                 sx={{
                                    display: "flex",
                                    alignItems: "flex-start",
                                    gap: 1,
                                    maxWidth: "70%",
                                    flexDirection: message.sender === "user" ? "row-reverse" : "row",
                                 }}
                              >
                                 <Avatar
                                    sx={{
                                       width: 32,
                                       height: 32,
                                       bgcolor: message.sender === "user" ? "primary.main" : "secondary.main",
                                    }}
                                 >
                                    {message.sender === "user" ? <PersonIcon /> : <BotIcon />}
                                 </Avatar>
                                 <Paper
                                    elevation={1}
                                    sx={{
                                       p: 1.5,
                                       backgroundColor: message.sender === "user" ? "primary.main" : "white",
                                       color: message.sender === "user" ? "white" : "text.primary",
                                       borderRadius: 2,
                                       maxWidth: "100%",
                                    }}
                                 >
                                    <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                                       {message.content}
                                    </Typography>
                                    <Typography
                                       variant="caption"
                                       sx={{
                                          display: "block",
                                          mt: 0.5,
                                          opacity: 0.7,
                                       }}
                                    ></Typography>
                                 </Paper>
                              </Box>
                           </ListItem>
                           {index < messages.length - 1 && <Divider sx={{ my: 1 }} />}
                        </React.Fragment>
                     ))}
                  </List>
               )}
               <div ref={messagesEndRef} />
            </Box>

            {/* Input Area */}
            <Box
               sx={{
                  p: 2,
                  borderTop: 1,
                  borderColor: "divider",
                  backgroundColor: "white",
               }}
            >
               <Box sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}>
                  <TextField
                     fullWidth
                     multiline
                     maxRows={4}
                     value={query}
                     onChange={(e) => setQuery(e.target.value)}
                     onKeyPress={handleKeyPress}
                     placeholder="Type your message..."
                     variant="outlined"
                     size="small"
                     sx={{ flex: 1 }}
                  />
                  <IconButton
                     onClick={connectSSE}
                     color="primary"
                     sx={{
                        bgcolor: "primary.main",
                        color: "white",
                        "&:hover": {
                           bgcolor: "primary.dark",
                        },
                        "&:disabled": {
                           bgcolor: "grey.300",
                           color: "grey.500",
                        },
                     }}
                  >
                     <SendIcon />
                  </IconButton>
               </Box>
               <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
                  Press Enter to send, Shift+Enter for new line
               </Typography>
            </Box>
         </Paper>
      </Container>
   );
}
