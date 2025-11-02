import React, { useState } from 'react';
import { Upload, ChevronLeft, ChevronRight } from 'lucide-react';
import './App.css';

const getStackRotations = (photoIndex) => {
  const seed = photoIndex;
  const rotations = [];
  const angles = [-4, -2, -1, 1, 2, 3];
  for (let i = 0; i < 5; i++) {
    rotations.push(angles[(seed + i * 7) % angles.length]);
  }
  return rotations;
};

// LandingPage component
const LandingPage = ({ 
  photoPreview, 
  userName, 
  error, 
  isLoading, 
  uploadedPhoto,
  handlePhotoUpload, 
  setUserName, 
  handleSubmit 
}) => {
  return (
    <div className="landing-page">
      {/* Light Blue Section - Title and Subtitle */}
      <section className="hero-block">
        <div className="hero-content">
          <h1 className="hero-title">Pardah</h1>
          <p className="hero-subtitle">Reclaim your modesty.</p>
        </div>
      </section>

      {/* Dark Green Section - Upload Form */}
      <section className="upload-block">
        <div className="upload-content">
          <p className="upload-text">To get started, upload a photo of yourself in hijab.</p>

          <div className="upload-box">
            {photoPreview ? (
              <div className="upload-preview">
                <img src={photoPreview} alt="Uploaded" className="preview-image" />
                <br></br>
                <label htmlFor="photo-upload" className="change-photo-link">
                  Change photo →
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
            <label htmlFor="username-input" className="username-label">What is your name/username?</label>
            <input
              id="username-input"
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              className="username-input"
              placeholder="Enter your name or search term"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            onClick={handleSubmit}
            disabled={!uploadedPhoto || !userName || isLoading}
            className="submit-button"
          >
            {isLoading ? 'Searching...' : 'Submit'}
          </button>
        </div>
      </section>
    </div>
  );
};

// ReviewPage component
const ReviewPage = ({
  foundPhotos,
  currentPhotoIndex,
  showFeedbackCard,
  showRemoveSection,
  showExitWarning,
  handlePrevious,
  handleNext,
  handleRemoveButton,
  handleNotMe,
  handleRemove,
  handleGoHome,
  confirmGoHome,
  cancelGoHome
}) => {
  const currentPhoto = foundPhotos[currentPhotoIndex];
  const totalPhotos = foundPhotos.length;
  const stackRotations = getStackRotations(currentPhotoIndex);

  if (!currentPhoto) return null;

  return (
    <div className="review-page">
      {showExitWarning && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 className="modal-title">Are you sure?</h3>
            <p className="modal-text">Going back to home will erase your current image search. Do you want to continue?</p>
            <div className="modal-buttons">
              <button onClick={confirmGoHome} className="modal-button-primary">Yes, go home</button>
              <button onClick={cancelGoHome} className="modal-button-secondary">Cancel</button>
            </div>
          </div>
        </div>
      )}

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
                      transform: `rotate(${stackRotations[index]}deg)`,
                      zIndex: 10 - index,
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
                      <h2 className="feedback-title">Thank you!</h2>
                      <p className="feedback-text">We will not show this photo again.</p>
                    </div>
                  </div>
                ) : (
                  <div className="photo-card">
                    <img
                      src={currentPhoto.url}
                      alt={`Photo ${currentPhotoIndex + 1}`}
                      className="photo-image"
                    />
                    <div className="photo-info">
                      <p className="similarity-text">
                        Similarity: {(currentPhoto.similarity * 100).toFixed(0)}%
                      </p>
                      <p className="source-text">Source: {currentPhoto.source}</p>
                    </div>
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
                <img src={currentPhoto.url} alt="Preview" className="remove-image" />
              </div>
              <div className="remove-info">
                <h3 className="remove-title">
                  Report this photo to Google
                </h3>
                <p className="remove-text">
                  Click the button below to report this image to Google for removal. You'll need to be signed into your Google account.
                </p>
                <div className="remove-actions">
                  <button onClick={handleRemove} className="remove-link-button">
                    Report to Google →
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// CompletePage component
const CompletePage = ({ 
  foundPhotos, 
  handleGoHome,
  showExitWarning,
  confirmGoHome,
  cancelGoHome
}) => (
  <div className="complete-page">
    {showExitWarning && (
      <div className="modal-overlay">
        <div className="modal-content">
          <h3 className="modal-title">Are you sure?</h3>
          <p className="modal-text">Going back to home will erase your current image search. Do you want to continue?</p>
          <div className="modal-buttons">
            <button onClick={confirmGoHome} className="modal-button-primary">Yes, go home</button>
            <button onClick={cancelGoHome} className="modal-button-secondary">Cancel</button>
          </div>
        </div>
      </div>
    )}

    <nav className="navbar navbar-review">
      <div className="navbar-brand">Pardah</div>
      <button onClick={handleGoHome} className="home-button">Home</button>
    </nav>

    <div className="complete-content">
      <div className="complete-header">
        <div className="photo-counter">{foundPhotos.length}/{foundPhotos.length}</div>
        <h1 className="review-title">Pardah</h1>
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
                  <h2 className="feedback-title">You're all set!</h2>
                  <p className="feedback-text">
                    Thank you for protecting your digital privacy.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <button onClick={handleGoHome} className="nav-button">
            <span className="finish-text">Done</span>
          </button>
        </div>

        <div className="action-buttons">
          <button onClick={handleGoHome} className="remove-button">
            Back to Home
          </button>
        </div>
      </div>
    </div>
  </div>
);

// Main App component
export default function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [foundPhotos, setFoundPhotos] = useState([]);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [userName, setUserName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedbackCard, setShowFeedbackCard] = useState(false);
  const [showRemoveSection, setShowRemoveSection] = useState(false);
  const [showExitWarning, setShowExitWarning] = useState(false);
  const [error, setError] = useState(null);

  const searchGooglePhotos = async (photo) => {
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', photo);
    formData.append('search_terms', userName);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.matches && data.matches.length > 0) {
        const photosWithMetadata = data.matches.map((match, i) => ({
          id: i,
          url: match.url,
          source: match.source,
          sourceUrl: match.url,
          similarity: match.similarity_score,
          distance: match.distance,
          hash: match.image_hash,
          isReviewed: false,
          isApproved: null
        }));

        setFoundPhotos(photosWithMetadata);
        setCurrentPage('review');
      } else {
        setError('No matching photos found. Try a different search term.');
      }

      setIsLoading(false);
    } catch (err) {
      console.error('Error:', err);
      setError('Error connecting to backend. Make sure it\'s running on port 5000.');
      setIsLoading(false);
    }
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedPhoto(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setPhotoPreview(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = () => {
    if (uploadedPhoto && userName) {
      searchGooglePhotos(uploadedPhoto);
    }
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

  const handleRemoveButton = () => {
    setShowRemoveSection(true);
  };

  const handleRemove = () => {
    const currentPhoto = foundPhotos[currentPhotoIndex];
    const reportLink = `https://www.google.com/webmasters/tools/removals?hl=en&pli=1&url=${encodeURIComponent(currentPhoto.url)}`;
    window.open(reportLink, '_blank');

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
    setPhotoPreview(null);
    setFoundPhotos([]);
    setCurrentPhotoIndex(0);
    setUserName('');
    setShowExitWarning(false);
    setShowRemoveSection(false);
    setShowFeedbackCard(false);
    setError(null);
  };

  const cancelGoHome = () => {
    setShowExitWarning(false);
  };

  return (
    <>
      {currentPage === 'landing' && (
        <LandingPage
          photoPreview={photoPreview}
          userName={userName}
          error={error}
          isLoading={isLoading}
          uploadedPhoto={uploadedPhoto}
          handlePhotoUpload={handlePhotoUpload}
          setUserName={setUserName}
          handleSubmit={handleSubmit}
        />
      )}
      {currentPage === 'review' && (
        <ReviewPage
          foundPhotos={foundPhotos}
          currentPhotoIndex={currentPhotoIndex}
          showFeedbackCard={showFeedbackCard}
          showRemoveSection={showRemoveSection}
          showExitWarning={showExitWarning}
          handlePrevious={handlePrevious}
          handleNext={handleNext}
          handleRemoveButton={handleRemoveButton}
          handleNotMe={handleNotMe}
          handleRemove={handleRemove}
          handleGoHome={handleGoHome}
          confirmGoHome={confirmGoHome}
          cancelGoHome={cancelGoHome}
        />
      )}
      {currentPage === 'complete' && (
        <CompletePage
          foundPhotos={foundPhotos}
          handleGoHome={handleGoHome}
          showExitWarning={showExitWarning}
          confirmGoHome={confirmGoHome}
          cancelGoHome={cancelGoHome}
        />
      )}
    </>
  );
}
