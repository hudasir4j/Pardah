// App.js
import React, { useState } from 'react';
import { Upload, ChevronLeft, ChevronRight } from 'lucide-react';
import './App.css';

const App = () => {
  const [currentPage, setCurrentPage] = useState('landing');
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [foundPhotos, setFoundPhotos] = useState([]);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [userName, setUserName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedbackCard, setShowFeedbackCard] = useState(false);
  const [showRemoveSection, setShowRemoveSection] = useState(false);
  const [showExitWarning, setShowExitWarning] = useState(false);
  const [showUsernameModal, setShowUsernameModal] = useState(false);
  const [usernameInput, setUsernameInput] = useState('');

  // Placeholder API call to backend
  const searchGooglePhotos = async (photo) => {
    setIsLoading(true);
    
    // Simulating API call to backend
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock response - 25 placeholder photos
    const mockPhotos = Array(25).fill(null).map((_, i) => ({
      id: i,
      url: uploadedPhoto,
      source: i % 3 === 0 ? "Instagram" : i % 3 === 1 ? "Facebook" : "Google Photos",
      sourceUrl: i % 2 === 0 ? `https://example.com/photo/${i}` : null,
      posterEmail: i % 2 === 1 ? `poster${i}@example.com` : null,
      isReviewed: false,
      isApproved: null
    }));
    
    setFoundPhotos(mockPhotos);
    setIsLoading(false);
    setCurrentPage('review');
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const photoUrl = URL.createObjectURL(file);
      setUploadedPhoto(photoUrl);
    }
  };

  const handleSubmit = () => {
    if (uploadedPhoto && userName) {
      searchGooglePhotos(uploadedPhoto);
    }
  };

  const handleRemoveButton = () => {
    setShowRemoveSection(true);
  };

  const handleNotMe = () => {
    const updatedPhotos = [...foundPhotos];
    updatedPhotos[currentPhotoIndex].isApproved = false;
    updatedPhotos[currentPhotoIndex].isReviewed = true;
    setFoundPhotos(updatedPhotos);
    
    setShowFeedbackCard(true);
    
    setTimeout(() => {
      setShowFeedbackCard(false);
      if (currentPhotoIndex < foundPhotos.length - 1) {
        setCurrentPhotoIndex(currentPhotoIndex + 1);
      } else {
        setCurrentPage('complete');
      }
    }, 2000);
  };

  const handlePrevious = () => {
    if (currentPhotoIndex > 0) {
      setCurrentPhotoIndex(currentPhotoIndex - 1);
      setShowFeedbackCard(false);
      setShowRemoveSection(false);
    }
  };

  const handleNext = () => {
    if (currentPhotoIndex < foundPhotos.length - 1) {
      setCurrentPhotoIndex(currentPhotoIndex + 1);
      setShowFeedbackCard(false);
      setShowRemoveSection(false);
    }
  };

  const handleRemove = () => {
    const updatedPhotos = [...foundPhotos];
    updatedPhotos[currentPhotoIndex].isApproved = true;
    updatedPhotos[currentPhotoIndex].isReviewed = true;
    setFoundPhotos(updatedPhotos);
    
    setShowRemoveSection(false);
    
    if (currentPhotoIndex < foundPhotos.length - 1) {
      setCurrentPhotoIndex(currentPhotoIndex + 1);
    } else {
      setCurrentPage('complete');
    }
  };

  const handleGoHome = () => {
    setShowExitWarning(true);
  };

  const confirmGoHome = () => {
    setCurrentPage('landing');
    setUploadedPhoto(null);
    setFoundPhotos([]);
    setCurrentPhotoIndex(0);
    setUserName('');
    setShowExitWarning(false);
    setShowRemoveSection(false);
    setShowFeedbackCard(false);
  };

  const cancelGoHome = () => {
    setShowExitWarning(false);
  };

  // Landing Page Component
  const LandingPage = () => (
    <div className="page-container">
      <header className="header">
        <div className="header-content">
          <div className="site-name">Pardah</div>
        </div>
      </header>

      <div className="hero-section">
        <h1 className="hero-title">Pardah</h1>
        <p className="hero-subtitle">Reclaim your modesty.</p>
      </div>

      <div className="upload-section-container">
        <div className="upload-section">
          <p className="upload-text">
            To get started, upload a photo of yourself in hijab.
          </p>
          
          <div className="upload-box">
            {uploadedPhoto ? (
              <div className="upload-preview">
                <img src={uploadedPhoto} alt="Uploaded" className="preview-image" />
                <label htmlFor="photo-upload" className="change-photo-link">
                  Change photo
                </label>
              </div>
            ) : (
              <label htmlFor="photo-upload" className="upload-label">
                <Upload className="upload-icon" />
                <p className="upload-instruction">Drag photos here</p>
                <p className="upload-divider">— or —</p>
                <p className="upload-instruction-small">Select photos from your computer</p>
              </label>
            )}
            <input
              id="photo-upload"
              type="file"
              accept="image/*"
              onChange={handlePhotoUpload}
              className="file-input"
            />
          </div>

          <div className="username-container">
            <label htmlFor="username-input" className="username-label">
              What is your name/username?
            </label>
            <input
              id="username-input"
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              className="username-input"
              placeholder="Enter your name"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!uploadedPhoto || !userName || isLoading}
            className="submit-button"
          >
            {isLoading ? 'Searching...' : 'Submit'}
          </button>
        </div>
      </div>
    </div>
  );

  // Review Page Component
  const ReviewPage = () => {
    const currentPhoto = foundPhotos[currentPhotoIndex];
    const totalPhotos = foundPhotos.length;

    return (
      <div className="page-container">
        {showExitWarning && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h3 className="modal-title">Are you sure?</h3>
              <p className="modal-text">
                Going back to home will erase your current image search. Do you want to continue?
              </p>
              <div className="modal-buttons">
                <button onClick={confirmGoHome} className="modal-button-primary">
                  Yes, go home
                </button>
                <button onClick={cancelGoHome} className="modal-button-secondary">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        <header className="header">
          <div className="header-content header-with-button">
            <div className="site-name">Pardah</div>
            <button onClick={handleGoHome} className="home-button">
              Home
            </button>
          </div>
        </header>

        <div className="review-content">
          <div className="review-header">
            <h1 className="review-title">Pardah</h1>
            <button onClick={handleGoHome} className="upload-different-link">
              I would like to upload a different photo.
            </button>
          </div>

          <div className="photo-review-section">
            <div className="photo-counter">
              {currentPhotoIndex + 1}/{totalPhotos}
            </div>
            
            <div className="photo-navigation">
              <button
                onClick={handlePrevious}
                disabled={currentPhotoIndex === 0}
                className="nav-button"
              >
                <ChevronLeft className="nav-icon" />
              </button>

              <div className="photo-stack-container">
                {foundPhotos.slice(currentPhotoIndex, currentPhotoIndex + 5).map((photo, index) => {
                  if (index === 0) return null;
                  return (
                    <div
                      key={index}
                      className="photo-stack"
                      style={{
                        top: `${index * 8}px`,
                        left: `${index * 4}px`,
                        transform: `rotate(${index * 1}deg)`,
                        zIndex: 10 - index,
                        opacity: 1 - (index * 0.15)
                      }}
                    >
                      <img
                        src={photo.url}
                        alt={`Photo ${currentPhotoIndex + index + 1}`}
                        className="stack-image"
                      />
                    </div>
                  );
                })}

                <div className="current-photo">
                  {showFeedbackCard ? (
                    <div className="feedback-card">
                      <div className="feedback-content">
                        <h2 className="feedback-title">Thank you for your feedback!</h2>
                        <p className="feedback-text">We will not be showing this photo again.</p>
                      </div>
                    </div>
                  ) : (
                    <div className="photo-card">
                      <img
                        src={currentPhoto?.url}
                        alt={`Photo ${currentPhotoIndex + 1}`}
                        className="photo-image"
                      />
                    </div>
                  )}
                </div>
              </div>

              <button
                onClick={handleNext}
                disabled={currentPhotoIndex === totalPhotos - 1}
                className="nav-button"
              >
                <ChevronRight className="nav-icon" />
              </button>
            </div>

            {!showFeedbackCard && !showRemoveSection && (
              <div className="action-buttons">
                <button onClick={handleRemoveButton} className="remove-button">
                  Remove
                </button>
                <button onClick={handleNotMe} className="not-me-button">
                  This isn't me
                </button>
              </div>
            )}

            {showRemoveSection && (
              <div className="remove-section">
                <div className="remove-preview">
                  <img src={currentPhoto?.url} alt="Preview" className="remove-image" />
                </div>
                <div className="remove-info">
                  <h3 className="remove-title">
                    This photo is uploaded to {currentPhoto?.source || "Unknown source"}.
                  </h3>
                  <p className="remove-text">
                    You can report this photo to have it removed, or send an email to the poster asking to be removed.
                  </p>
                  <div className="remove-actions">
                    {currentPhoto?.sourceUrl && (
                      <a
                        href={currentPhoto.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="remove-link-button"
                      >
                        Remove
                      </a>
                    )}
                    {currentPhoto?.posterEmail && (
                      <a
                        href={`mailto:${currentPhoto.posterEmail}`}
                        className="remove-link-button"
                      >
                        Send email to {currentPhoto.posterEmail}
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Complete Page Component
  const CompletePage = () => (
    <div className="page-container">
      {showExitWarning && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 className="modal-title">Are you sure?</h3>
            <p className="modal-text">
              Going back to home will erase your current image search. Do you want to continue?
            </p>
            <div className="modal-buttons">
              <button onClick={confirmGoHome} className="modal-button-primary">
                Yes, go home
              </button>
              <button onClick={cancelGoHome} className="modal-button-secondary">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="header">
        <div className="header-content header-with-button">
          <div className="site-name">Pardah</div>
          <button onClick={handleGoHome} className="home-button">
            Home
          </button>
        </div>
      </header>

      <div className="review-content">
        <div className="review-header">
          <div className="photo-counter">25/25</div>
          <h1 className="review-title">Pardah</h1>
          <button onClick={handleGoHome} className="upload-different-link">
            I would like to upload a different photo.
          </button>
        </div>

        <div className="photo-review-section">
          <div className="photo-navigation">
            <button className="nav-button nav-button-disabled">
              <ChevronLeft className="nav-icon" />
            </button>

            <div className="photo-stack-container">
              <div className="current-photo">
                <div className="feedback-card">
                  <div className="feedback-content">
                    <h2 className="feedback-title">Thank you for your feedback!</h2>
                    <p className="feedback-text">We will not be showing this photo again.</p>
                  </div>
                </div>
              </div>
            </div>

            <button className="nav-button">
              <span className="finish-text">Finish</span>
            </button>
          </div>

          <div className="action-buttons">
            <button className="remove-button button-disabled">
              Remove
            </button>
            <button className="not-me-button button-disabled">
              This isn't me
            </button>
          </div>
        </div>

        <div className="remove-section">
          <div className="remove-preview">
            <img src={uploadedPhoto} alt="Preview" className="remove-image" />
          </div>
          <div className="remove-info">
            <h3 className="remove-title">
              This photo is uploaded to {foundPhotos[foundPhotos.length - 1]?.source || "Unknown source"}.
            </h3>
            <p className="remove-text">
              You can report this photo to have it removed, or send an email to the poster asking to be removed.
            </p>
            <div className="remove-actions">
              {foundPhotos[foundPhotos.length - 1]?.sourceUrl && (
                <a
                  href={foundPhotos[foundPhotos.length - 1].sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="remove-link-button"
                >
                  Remove
                </a>
              )}
              {foundPhotos[foundPhotos.length - 1]?.posterEmail && (
                <a
                  href={`mailto:${foundPhotos[foundPhotos.length - 1].posterEmail}`}
                  className="remove-link-button"
                >
                  Send email to {foundPhotos[foundPhotos.length - 1].posterEmail}
                </a>
              )}
            </div>
          </div>
        </div>

        <div className="back-to-beginning">
          <button onClick={handleGoHome} className="back-button">
            Back to beginning → ✕
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {currentPage === 'landing' && <LandingPage />}
      {currentPage === 'review' && <ReviewPage />}
      {currentPage === 'complete' && <CompletePage />}
    </>
  );
};

export default App;