import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import PrivacyMessage from './components/PrivacyMessage';
import UploadForm from './components/UploadForm';
import ResultsPage from './components/ResultsPage';

function App() {
  const [step, setStep] = useState('privacy'); // privacy -> upload -> results
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerms, setSearchTerms] = useState('');

  const handlePrivacyAccept = () => {
    setStep('upload');
  };

  const handleUpload = async (file, terms) => {
    setLoading(true);
    setError(null);
    setSearchTerms(terms);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('search_terms', terms);

    try {
      console.log('Uploading to http://localhost:5000/upload');
      const response = await axios.post(
        'http://localhost:5000/upload',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );

      console.log('Response:', response.data);
      setMatches(response.data.matches || []);
      setStep('results');
    } catch (err) {
      console.error('Error:', err);
      setError(
        err.response?.data?.error || 'Error uploading image. Make sure backend is running on port 5000!'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep('upload');
    setMatches([]);
    setError(null);
    setSearchTerms('');
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Reclaim</h1>
        <p>Take back control of your digital image</p>
      </header>

      {step === 'privacy' && (
        <PrivacyMessage onAccept={handlePrivacyAccept} />
      )}

      {step === 'upload' && (
        <UploadForm
          onUpload={handleUpload}
          loading={loading}
          error={error}
        />
      )}

      {step === 'results' && (
        <ResultsPage
          matches={matches}
          onReset={handleReset}
          searchTerms={searchTerms}
        />
      )}
    </div>
  );
}

export default App;