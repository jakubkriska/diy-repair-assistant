import axios from 'axios';
import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  // State variables
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  // Function to handle sending a message
  const sendMessage = async (e) => {
    e.preventDefault();

    if (!message.trim()) return;

    // Add user message to the chat
    setChatHistory([...chatHistory, { sender: 'user', text: message }]);

    try {
        // Send message to Flask backend
        const response = await axios.post(
            'http://127.0.0.1:5000/chat', 
            { message }, 
            { headers: { 'Content-Type': 'application/json' } }
        );

        // Add bot response to chat
        setChatHistory((prev) => [...prev, { sender: 'bot', text: response.data.response }]);
    } catch (error) {
        console.error('Error:', error);
        setChatHistory((prev) => [...prev, { sender: 'bot', text: 'Error: Could not reach server.' }]);
    }

    setMessage('');  // Clear input field
};

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
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
          <div key={index} className={chat.sender === 'user' ? 'user-message' : 'bot-message'}>
            <strong>{chat.sender === 'user' ? 'You' : 'Bot'}:</strong> {chat.text}
          </div>
        ))}
      </div>

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

