import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [email, setEmail] = useState('');
  const [course, setCourse] = useState('');
  const [sectionIndex, setSectionIndex] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    try {
      const response = await axios.post('http://localhost:5000/subscribe', {
        email,
        course,
        section_index: parseInt(sectionIndex)
      });

      setMessage('Subscription added successfully!');
      setEmail('');
      setCourse('');
      setSectionIndex('');
    } catch (error) {
      setMessage('Error: ' + (error.response?.data?.message || 'Something went wrong'));
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Course Notification System</h1>
      </header>
      <main>
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Your Email"
            required
          />
          <input
            type="text"
            value={course}
            onChange={(e) => setCourse(e.target.value)}
            placeholder="Course Code (e.g., CMSC131)"
            required
          />
          <input
            type="number"
            value={sectionIndex}
            onChange={(e) => setSectionIndex(e.target.value)}
            placeholder="Section Index"
            required
          />
          <button type="submit">Subscribe</button>
        </form>
        {message && <p className="message">{message}</p>}
      </main>
    </div>
  );
}

export default App;