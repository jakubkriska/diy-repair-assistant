import axios from 'axios';
import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';



function App() {
  // State variables
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [imagePreview, setImagePreview] = useState(null);

  // Function to handle sending a message
  const sendMessage = async (e) => {
    e.preventDefault();

    if (!message.trim()) return;

    // Add user message to the chat
    setChatHistory((prevChatHistory) => [
      ...prevChatHistory,
      { sender: 'user', text: message }
    ]);

    try {
      // Send message to Flask backend
      const response = await axios.post(
        'http://127.0.0.1:5001/chat',
        { message },
        { headers: { 'Content-Type': 'application/json' } }
      );

      // Add bot response to chat
      setChatHistory((prevChatHistory) => [
        ...prevChatHistory,
        { sender: 'bot', text: response.data.response || "I couldn't understand that. Can you rephrase?" }
      ]);
    } catch (error) {
      console.error('Error:', error);
      setChatHistory((prev) => [
        ...prev,
        { sender: 'bot', text: 'Error: Could not reach server.' }
      ]);
    }

    // Clear input field
    setMessage('');
  };

  // Function to handle image upload
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
  
    if (!file) return;
    console.log(`[DEBUG] Selected file: ${file.name}`);
  
    // Create a new FileReader instance
    const reader = new FileReader();
  
    reader.onloadend = () => console.log(`[DEBUG] Image preview data loaded.`);
  
    reader.readAsDataURL(file);
  
    try {
      const formData = new FormData();
      formData.append("file", file);
      console.log("[DEBUG] Sending image to /upload-image endpoint...");
      const response = await axios.post("http://127.0.0.1:5001/upload-image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("[DEBUG] Image analysis response:", response.data);
      
      const damageResults = response.data.image_analysis_results;

      // 🔥 Send analysis results to chat endpoint
      const chatResponse = await axios.post(
        "http://127.0.0.1:5001/chat",
        { message: "Here are the image analysis results.", image_analysis_results: damageResults },
        { headers: { "Content-Type": "application/json" } }
      );

      // 💬 Add result to chat
      setChatHistory((prev) => [
        ...prev,
        { sender: "bot", text: chatResponse.data.response || "I couldn't process the analysis. Can you try again?" }
      ]);
  
    } catch (error) {
      console.error("Error uploading image:", error);
      setChatHistory((prev) => [
        ...prev,
        { sender: "bot", text: "Error: Could not upload the image." },
      ]);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Edit <code>src/App.js</code> and save to reload.</p>
        
        {/* Image Upload Input */}
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleImageUpload} 
          className="image-upload"
          style={{ display: 'block', margin: '20px auto', padding: '10px', border: '1px solid #ccc' }}
        />

        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>

      {/* Chat interface */}
      <div className="chat-window">
        {chatHistory.map((chat, index) => (
          <div key={`${chat.sender}-${index}`} className={chat.sender === 'user' ? 'user-message' : 'bot-message'}>
            <div className={chat.sender === 'user' ? 'user-message' : 'bot-message'}>
              <strong>{chat.sender === 'user' ? 'You' : 'Bot'}:</strong>
              <div style={{ marginLeft: "10px" }}
                dangerouslySetInnerHTML={{ __html: chat.text || "⚠️ Error: No response received." }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Display image preview (optional) */}
      {imagePreview && <img src={imagePreview} alt="Preview" className="image-preview" />}

      {/* Chat message input */}
      <form onSubmit={sendMessage}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;