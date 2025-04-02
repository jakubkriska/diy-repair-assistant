import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Stage, Layer, Rect, Circle, Line, Image as KonvaImage } from "react-konva";
import useImage from "use-image";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [imagePreview, setImagePreview] = useState(null);
  const [tool, setTool] = useState("rectangle"); // Tool selection
  const [shapes, setShapes] = useState([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const chatWindowRef = useRef(null);
  const lastMessageRef = useRef(null);
  const stageRef = useRef(null);
  const [uploadedImage] = useImage(imagePreview);
    // Define maximum preview dimensions
    const maxWidth = 500;
    const maxHeight = 500;
    // Default values if image is not loaded yet
    let previewWidth = maxWidth;
    let previewHeight = maxHeight;
    if (uploadedImage) {
      // Calculate scale factor to maintain aspect ratio
      const scale = Math.min(maxWidth / uploadedImage.width, maxHeight / uploadedImage.height);
      previewWidth = uploadedImage.width * scale;
      previewHeight = uploadedImage.height * scale;
    }
  const chatFooterRef = useRef(null); // Reference to footer element

  // Auto-scroll when chatHistory updates
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatHistory]);

  // Dynamically adjust chat window padding based on the footer height
  useEffect(() => {
    if (chatFooterRef.current && chatWindowRef.current) {
      const footerHeight = chatFooterRef.current.offsetHeight;
      const extraSpace = 20;
      chatWindowRef.current.style.paddingBottom = (footerHeight + extraSpace) + "px";
    }
  }, [chatHistory, imagePreview, message, shapes]);

  // Handle Image Upload
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // Handle User Drawing
  const handleMouseDown = (e) => {
    setIsDrawing(true);
    const stage = e.target.getStage();
    const pos = stage.getPointerPosition();

    if (tool === "rectangle") {
      setShapes([...shapes, { type: "rect", x: pos.x, y: pos.y, width: 0, height: 0 }]);
    } else if (tool === "circle") {
      setShapes([...shapes, { type: "circle", x: pos.x, y: pos.y, radius: 0 }]);
    } else if (tool === "freehand") {
      setShapes([...shapes, { type: "line", points: [pos.x, pos.y] }]);
    }
  };

  const handleMouseMove = (e) => {
    if (!isDrawing) return;
    const stage = e.target.getStage();
    const pos = stage.getPointerPosition();
    const updatedShapes = [...shapes];
    const index = updatedShapes.length - 1;
    if (index < 0) return;

    if (tool === "rectangle") {
      updatedShapes[index].width = pos.x - updatedShapes[index].x;
      updatedShapes[index].height = pos.y - updatedShapes[index].y;
    } else if (tool === "circle") {
      const radius = Math.sqrt((pos.x - updatedShapes[index].x) ** 2 + (pos.y - updatedShapes[index].y) ** 2);
      updatedShapes[index].radius = radius;
    } else if (tool === "freehand") {
      updatedShapes[index].points = [...updatedShapes[index].points, pos.x, pos.y];
    }
    setShapes(updatedShapes);
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
  };

  function dataURLtoFile(dataurl, filename) {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type: mime});
  }

  // Convert Canvas to Image and Send to Backend
  const sendAnnotatedImage = async () => {
    const uri = stageRef.current.toDataURL(); // Convert Konva canvas to image
    const file = dataURLtoFile(uri, 'annotated_image.png'); // Convert to File object
    const formData = new FormData();
    formData.append('file', file); // Append file with key 'file'

    try {
      const response = await axios.post("http://127.0.0.1:5001/upload-image", formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setChatHistory([...chatHistory, { sender: "bot", text: response.data.response || "Error: No response received from server." }]);
      setImagePreview(null);
      setShapes([]);
    } catch (error) {
      console.error("Error uploading annotated image:", error);
    }
  };

  // Send Message
  const sendMessage = async () => {
    if (!message.trim()) return;
    setChatHistory((prev) => [...prev, { sender: "user", text: message }]);
    setMessage("");
    try {
      const response = await axios.post("http://127.0.0.1:5001/chat", { message });
      setChatHistory((prev) => [...prev, { sender: "bot", text: response.data.response }]);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevents a newline in the input
      sendMessage();
    }
  };

  return (
    <div className="App">
      {/* Header Section */}
      <header className="App-header">
        <h1>🛠 DIY Repair Assistant</h1>
      </header>


      <div className="chat-wrapper">
        {/* Main Chat Section */}
        <main className="chat-container">
          <div className="chat-window" ref={chatWindowRef}>
            {chatHistory.map((chat, index) => (
              <div
                key={index}
                className={chat.sender === "user" ? "user-message" : "bot-message"}
                ref={index === chatHistory.length - 1 ? lastMessageRef : null}
              >
                {chat.sender !== "user" && (
                  <strong>🛠 DIY Repair Assistant:</strong>
                )}
                <div dangerouslySetInnerHTML={{ __html: chat.text }} />
              </div>
            ))}
            <div ref={lastMessageRef} style={{ height: "1px" }} />
          </div>
        </main>

        {/* Footer with Tools and Upload */}
        <footer className="chat-footer" ref={chatFooterRef}>
          <div className="chat-input-form">
            <label className="image-upload-icon">
              {/* Use any icon or emoji you like; here we use a paperclip emoji as an example */}
            📎
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="image-upload-hidden"
              />
            </label>
            <textarea
              placeholder="Type your message..."
              className="chat-textarea"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
            />
            <button onClick={sendMessage}>Send</button>
          </div>
          {imagePreview && (
            <div className="annotation-container">
              <div className="canvas-container">
                <Stage
                  width={previewWidth}
                  height={previewHeight}
                  ref={stageRef}
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                >
                  <Layer>
                    {uploadedImage && (
                      <KonvaImage image={uploadedImage} x={0} y={0} width={previewWidth} height={previewHeight} />
                    )}
                    {shapes.map((shape, i) =>
                      shape.type === "rect" ? (
                        <Rect key={i} {...shape} stroke="red" strokeWidth={2} />
                      ) : shape.type === "circle" ? (
                        <Circle key={i} {...shape} stroke="blue" strokeWidth={2} />
                      ) : (
                        <Line key={i} {...shape} stroke="green" strokeWidth={2} lineCap="round" />
                      )
                    )}
                  </Layer>
                </Stage>
              </div>
              <div className="annotation-tools">
                <button onClick={() => setShapes(shapes.slice(0, -1))}>  ↩  </button>
                <button onClick={() => setTool("freehand")}>✏️ Draw</button>
                <button onClick={sendAnnotatedImage}>Send</button>
              </div>
            </div>
          )}
        </footer>
      </div>
    </div>
  );
}

export default App;
