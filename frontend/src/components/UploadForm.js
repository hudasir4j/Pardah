import React, { useState } from 'react';

function UploadForm({ onUpload, loading, error }) {
  const [file, setFile] = useState(null);
  const [searchTerms, setSearchTerms] = useState('');
  const [preview, setPreview] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreview(event.target.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (file && searchTerms.trim()) {
      onUpload(file, searchTerms);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Find Your Photos</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Step 1: Upload a photo of yourself</label>
            <p className="form-help">
              (preferably with your hijab)
            </p>
            <input
              type="file"
              onChange={handleFileChange}
              accept="image/*"
              disabled={loading}
            />
            {preview && (
              <img src={preview} alt="preview" className="preview" />
            )}
          </div>

          <div className="form-group">
            <label>Step 2: How do you go by online?</label>
            <input
              type="text"
              placeholder="e.g., 'Bob Smith', 'bob.sm1th'"
              value={searchTerms}
              onChange={(e) => setSearchTerms(e.target.value)}
              disabled={loading}
            />
            <p className="form-help">
              Try your full name, username, or name + location
            </p>
          </div>

          {error && <div className="error">{error}</div>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={!file || !searchTerms.trim() || loading}
          >
            {loading ? 'Searching...' : 'Search for My Photos'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default UploadForm;