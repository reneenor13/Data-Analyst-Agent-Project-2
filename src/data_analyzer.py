import React, { useState } from 'react';

export default function App() {
  const [questionFile, setQuestionFile] = useState(null);
  const [otherFiles, setOtherFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleQuestionChange = (e) => {
    setQuestionFile(e.target.files[0]);
  };

  const handleOtherFilesChange = (e) => {
    setOtherFiles([...e.target.files]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!questionFile) {
      alert('Please upload questions.txt file.');
      return;
    }
    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    formData.append('questions.txt', questionFile);
    otherFiles.forEach((file) => formData.append(file.name, file));

    try {
      const res = await fetch('/api/', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Data Analyst Agent</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <label>
          Upload questions.txt (required):
          <input type="file" accept=".txt" onChange={handleQuestionChange} />
        </label>

        <label>
          Upload additional files (optional):
          <input type="file" multiple onChange={handleOtherFilesChange} />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {error && <div className="error">Error: {error}</div>}

      {response && (
        <div className="response">
          <h2>Response</h2>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
