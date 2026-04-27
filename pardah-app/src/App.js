import React, { useState, useEffect, useCallback } from 'react';
import { Upload, ChevronLeft, ChevronRight } from 'lucide-react';
import './App.css';
import flowerMotifSrc from './Flower.svg';

const PARDAH_THEME_STORAGE_KEY = 'pardah-theme';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

const getHostFromUrl = (urlString) => {
  try {
    return new URL(urlString).hostname.replace(/^www\./, '');
  } catch {
    return '';
  }
};

const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return true;
  } catch {
    return false;
  }
};

const STATUS_LABELS = {
  pending: 'Not reported',
  submitted: 'Reported',
  removed: 'Removed',
};

const RemovalWizard = ({ photo, plan, loading, error, onMarkReported, onCancel }) => {
  const [copiedKey, setCopiedKey] = useState(null);
  const [showDmca, setShowDmca] = useState(false);

  const handleCopy = async (key, text) => {
    const ok = await copyToClipboard(text);
    if (ok) {
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 1800);
    }
  };

  if (loading) {
    return (
      <div className="remove-section wizard-section">
        <div className="remove-preview">
          <img src={photo.url} alt="Preview" className="remove-image" />
        </div>
        <div className="remove-info">
          <h3 className="remove-title">Building your takedown plan…</h3>
          <p className="remove-text">
            Scanning the source site for a real contact address and drafting
            a message you can send.
          </p>
          <div className="processing-bars">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="remove-section wizard-section">
        <div className="remove-preview">
          <img src={photo.url} alt="Preview" className="remove-image" />
        </div>
        <div className="remove-info">
          <h3 className="remove-title">We couldn't build a plan.</h3>
          <p className="remove-text">
            {error || 'Something went wrong. You can still open the source page directly.'}
          </p>
          <div className="remove-actions">
            <button
              className="remove-link-button"
              onClick={() => window.open(photo.pageUrl || photo.url, '_blank', 'noopener')}
            >
              Open source page →
            </button>
            <button className="not-me-button" onClick={onCancel}>Back</button>
          </div>
        </div>
      </div>
    );
  }

  const { steps = [], escalation, platform_label, host } = plan;

  const renderEmailBlock = (key, contactEmail, subject, template, contactMeta) => {
    const source = contactMeta?.source;
    const pageUrl = contactMeta?.pageUrl;
    let badge = null;
    if (source === 'mailto' || source === 'text') {
      badge = (
        <span className="wizard-contact-badge wizard-contact-badge-verified">
          Found on site
        </span>
      );
    } else if (source === 'hunter') {
      badge = (
        <span className="wizard-contact-badge wizard-contact-badge-verified">
          Verified
        </span>
      );
    } else if (source === 'guess') {
      badge = (
        <span className="wizard-contact-badge wizard-contact-badge-guess">
          Best guess
        </span>
      );
    }
    return (
    <>
      {contactEmail && (
        <>
          <div className="wizard-contact">
            <span className="wizard-contact-label">Send to</span>
            <code className="wizard-contact-email">{contactEmail}</code>
            {badge}
            <button
              type="button"
              className="wizard-contact-copy"
              onClick={() => handleCopy(`${key}-to`, contactEmail)}
            >
              {copiedKey === `${key}-to` ? 'Copied ✓' : 'Copy address'}
            </button>
          </div>
          {pageUrl && (source === 'mailto' || source === 'text') && (
            <a
              className="wizard-contact-source"
              href={pageUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              View on the site →
            </a>
          )}
        </>
      )}
      {subject && (
        <div className="wizard-template-meta">
          <span><strong>Subject:</strong> {subject}</span>
        </div>
      )}
      <textarea
        className="wizard-template"
        readOnly
        value={template}
        rows={Math.min(14, Math.max(6, (template.match(/\n/g) || []).length + 2))}
      />
      <div className="wizard-step-actions">
        <button
          type="button"
          className="remove-link-button wizard-primary"
          onClick={() => handleCopy(`${key}-msg`, template)}
        >
          {copiedKey === `${key}-msg` ? 'Message copied ✓' : 'Copy message'}
        </button>
        <a
          className="wizard-link-button wizard-link-subtle"
          href="https://mail.google.com/mail/u/0/#inbox?compose=new"
          target="_blank"
          rel="noopener noreferrer"
        >
          Open Gmail
        </a>
      </div>
    </>
    );
  };

  return (
    <div className="remove-section wizard-section">
      <div className="wizard-header">
        <div className="remove-preview">
          <img src={photo.url} alt="Preview" className="remove-image" />
        </div>
        <div className="wizard-header-text">
          <h3 className="remove-title">Take it down from {platform_label || host || 'this site'}</h3>
          <p className="remove-text">
            Two quick steps. Copy the address and the message, paste them into Gmail
            (or your favourite mail app), and send.
          </p>
        </div>
      </div>

      <ol className="wizard-steps">
        {steps.map((s) => (
          <li key={s.step} className="wizard-step">
            <div className="wizard-step-number">{s.step}</div>
            <div className="wizard-step-body">
              <h4 className="wizard-step-title">{s.title}</h4>
              {s.description && <p className="wizard-step-desc">{s.description}</p>}

              {s.kind === 'email' && s.template
                ? renderEmailBlock(
                    `step-${s.step}`,
                    s.contact_email,
                    s.subject,
                    s.template,
                    { source: s.contact_source, pageUrl: s.contact_page_url },
                  )
                : null}

              {s.primary && s.primary.url && (
                <div className="wizard-step-actions">
                  <button
                    type="button"
                    className="remove-link-button wizard-primary"
                    onClick={() => window.open(s.primary.url, '_blank', 'noopener')}
                  >
                    {s.primary.label} →
                  </button>
                </div>
              )}
            </div>
          </li>
        ))}
      </ol>

      {escalation && escalation.template && (
        <details
          className="wizard-escalation"
          open={showDmca}
          onToggle={(e) => setShowDmca(e.currentTarget.open)}
        >
          <summary className="wizard-escalation-summary">
            <span className="wizard-escalation-tag">Worst case</span>
            {escalation.title}
          </summary>
          <div className="wizard-escalation-body">
            {escalation.description && (
              <p className="wizard-step-desc">{escalation.description}</p>
            )}
            {renderEmailBlock(
              'esc',
              escalation.contact_email,
              escalation.subject,
              escalation.template,
              { source: plan.contact_source, pageUrl: plan.contact_page_url },
            )}
          </div>
        </details>
      )}

      <div className="wizard-footer">
        <button className="remove-link-button wizard-primary" onClick={onMarkReported}>
          I've submitted this report
        </button>
        <button className="not-me-button" onClick={onCancel}>
          Back to photo
        </button>
      </div>
    </div>
  );
};

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
  userEmail,
  error,
  isLoading,
  uploadedPhoto,
  handlePhotoUpload,
  setUserName,
  setUserEmail,
  handleSubmit,
  onToggleHiddenTheme,
}) => {
  return (
    <div className="landing-page">
      {/* Left: full-height Mughal arch — floral frame, plain interior with title */}
      <section className="hero-block">
        <svg className="hero-arch-clip-svg" width="0" height="0" aria-hidden="true" focusable="false">
          <defs>
            {/*
              Arch shape from project Arch.svg (center cell of the tile grid, top-middle arch).
              Path coords are in the source file space; matrix maps bbox to 0–1 for clipPathUnits.
            */}
            <clipPath id="heroMughalArchClip" clipPathUnits="objectBoundingBox">
              <path
                fill="#000"
                fillRule="evenodd"
                transform="matrix(0.0016799 0 0 0.000916 -2.5734 -0.19574)"
                d="M 2127.179688 1305.398438 L 1531.910156 1305.398438 L 1531.910156 463.511719 C 1531.910156 285.421875 1779.621094 400.019531 1829.550781 213.691406 C 1879.46875 400.019531 2127.179688 285.421875 2127.179688 463.511719 L 2127.179688 1305.398438 L 1531.910156 1305.398438 Z"
              />
            </clipPath>
          </defs>
        </svg>
        <div className="hero-arch-panel">
          <div className="hero-arch-floral" aria-hidden="true" />
          <div className="hero-arch-inner">
            <div className="hero-arch-cream">
            <div className="hero-arch-motif-wrap" aria-hidden="true">
              <img
                src={flowerMotifSrc}
                alt=""
                className="hero-mughal-motif"
                decoding="async"
                aria-hidden
              />
            </div>
            <div className="hero-content">
              <h1 className="hero-title" aria-label="Pardah">
                <span aria-hidden="true">
                  Parda
                  <span
                    className="hero-title-h-hit"
                    role="presentation"
                    tabIndex={-1}
                    onClick={(e) => {
                      e.preventDefault();
                      onToggleHiddenTheme();
                    }}
                  >
                    h
                  </span>
                </span>
              </h1>
              <p className="hero-subtitle">Reclaim your modesty.</p>
            </div>
            </div>
          </div>
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

          <div className="username-container">
            <label htmlFor="email-input" className="username-label">
              Your email <span className="username-label-hint">(optional, used in takedown messages)</span>
            </label>
            <input
              id="email-input"
              type="email"
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              className="username-input"
              placeholder="you@example.com"
              autoComplete="email"
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

          {isLoading && (
            <div className="processing-panel" aria-live="polite">
              <div className="processing-header">
                <span className="processing-title">Scanning the web for matches</span>
                <span className="processing-dots">
                  <i></i><i></i><i></i>
                </span>
              </div>
              <div className="processing-bars">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <p className="processing-subtext">
                Searching across sources and comparing facial embeddings.
              </p>
            </div>
          )}
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
  removalPlan,
  removalLoading,
  removalError,
  handlePrevious,
  handleNext,
  handleRemoveButton,
  handleNotMe,
  handleMarkReported,
  handleCloseRemoveSection,
  handleGoHome,
  confirmGoHome,
  cancelGoHome,
}) => {
  const currentPhoto = foundPhotos[currentPhotoIndex];
  const totalPhotos = foundPhotos.length;
  const stackRotations = getStackRotations(currentPhotoIndex);
  const reviewProgress = totalPhotos > 0 ? ((currentPhotoIndex + 1) / totalPhotos) * 100 : 0;

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
          <div className="review-progress-track" aria-hidden="true">
            <div className="review-progress-fill" style={{ width: `${reviewProgress}%` }} />
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
                      alt={`Result ${currentPhotoIndex + index + 1}`}
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
                      alt={`Result ${currentPhotoIndex + 1}`}
                      className="photo-image"
                    />
                    <div className="photo-info">
                      <div className="source-chip-row">
                        <span className="source-chip">{currentPhoto.source}</span>
                        <span className="source-chip source-chip-muted">
                          {getHostFromUrl(currentPhoto.pageUrl || currentPhoto.url) || 'Unknown host'}
                        </span>
                        {currentPhoto.status && currentPhoto.status !== 'pending' && (
                          <span className={`source-chip status-chip status-chip-${currentPhoto.status}`}>
                            {STATUS_LABELS[currentPhoto.status] || currentPhoto.status}
                          </span>
                        )}
                      </div>
                      <p className="similarity-text">
                        Similarity: {(currentPhoto.similarity * 100).toFixed(0)}%
                      </p>
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
            <RemovalWizard
              photo={currentPhoto}
              plan={removalPlan}
              loading={removalLoading}
              error={removalError}
              onMarkReported={handleMarkReported}
              onCancel={handleCloseRemoveSection}
            />
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
  const applyStoredTheme = useCallback(() => {
    try {
      if (localStorage.getItem(PARDAH_THEME_STORAGE_KEY) === 'mauve') {
        document.documentElement.setAttribute('data-theme', 'mauve');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
    } catch {
      document.documentElement.removeAttribute('data-theme');
    }
  }, []);

  useEffect(() => {
    applyStoredTheme();
  }, [applyStoredTheme]);

  const handleToggleHiddenTheme = useCallback(() => {
    try {
      const isMauve = document.documentElement.getAttribute('data-theme') === 'mauve';
      if (isMauve) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem(PARDAH_THEME_STORAGE_KEY, 'ember');
      } else {
        document.documentElement.setAttribute('data-theme', 'mauve');
        localStorage.setItem(PARDAH_THEME_STORAGE_KEY, 'mauve');
      }
    } catch {
      /* private mode / blocked storage */
    }
  }, []);

  const [currentPage, setCurrentPage] = useState('landing');
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [foundPhotos, setFoundPhotos] = useState([]);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedbackCard, setShowFeedbackCard] = useState(false);
  const [showRemoveSection, setShowRemoveSection] = useState(false);
  const [showExitWarning, setShowExitWarning] = useState(false);
  const [error, setError] = useState(null);
  const [searchDebug, setSearchDebug] = useState(null);
  const [removalPlan, setRemovalPlan] = useState(null);
  const [removalLoading, setRemovalLoading] = useState(false);
  const [removalError, setRemovalError] = useState(null);

  const searchGooglePhotos = async (photo) => {
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', photo);
    formData.append('search_terms', userName);

    try {
      const response = await fetch(`${BACKEND_URL}/upload`, {
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
          pageUrl: match.page_url || match.url,
          similarity: match.similarity_score,
          distance: match.distance,
          hash: match.image_hash,
          isReviewed: false,
          isApproved: null,
          status: 'pending',
        }));

        setFoundPhotos(photosWithMetadata);
        setSearchDebug(data.search_debug || null);
        setCurrentPage('review');
      } else {
        setError('No matching photos found. Try a different search term.');
        setSearchDebug(data.search_debug || null);
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

  const resetWizardState = () => {
    setShowRemoveSection(false);
    setRemovalPlan(null);
    setRemovalError(null);
    setRemovalLoading(false);
  };

  const handlePrevious = () => {
    if (currentPhotoIndex > 0) {
      setCurrentPhotoIndex(currentPhotoIndex - 1);
      setShowFeedbackCard(false);
      resetWizardState();
    }
  };

  const handleNext = () => {
    if (currentPhotoIndex < foundPhotos.length - 1) {
      setCurrentPhotoIndex(currentPhotoIndex + 1);
      setShowFeedbackCard(false);
      resetWizardState();
    }
  };

  const handleRemoveButton = async () => {
    const currentPhoto = foundPhotos[currentPhotoIndex];
    if (!currentPhoto) return;
    setShowRemoveSection(true);
    setRemovalLoading(true);
    setRemovalError(null);
    setRemovalPlan(null);

    try {
      const response = await fetch(`${BACKEND_URL}/removal-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_url: currentPhoto.url,
          page_url: currentPhoto.pageUrl || currentPhoto.url,
          image_hash: currentPhoto.hash,
          user_name: userName,
          user_email: userEmail,
        }),
      });
      const data = await response.json();
      if (!response.ok || !data.plan) {
        throw new Error(data.error || 'Could not build plan');
      }
      setRemovalPlan(data.plan);
    } catch (err) {
      console.error('removal-plan error:', err);
      setRemovalError(
        err.message || 'Could not connect to backend to build the takedown plan.'
      );
    } finally {
      setRemovalLoading(false);
    }
  };

  const handleCloseRemoveSection = () => {
    resetWizardState();
  };

  const handleMarkReported = () => {
    const updatedPhotos = [...foundPhotos];
    updatedPhotos[currentPhotoIndex] = {
      ...updatedPhotos[currentPhotoIndex],
      isApproved: true,
      isReviewed: true,
      status: 'submitted',
    };
    setFoundPhotos(updatedPhotos);

    resetWizardState();

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
    setShowExitWarning(false);
    setShowFeedbackCard(false);
    resetWizardState();
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
          userEmail={userEmail}
          error={error}
          isLoading={isLoading}
          uploadedPhoto={uploadedPhoto}
          handlePhotoUpload={handlePhotoUpload}
          setUserName={setUserName}
          setUserEmail={setUserEmail}
          handleSubmit={handleSubmit}
          onToggleHiddenTheme={handleToggleHiddenTheme}
        />
      )}
      {currentPage === 'review' && (
        <>
          {searchDebug && (
            <div className="error-message" style={{ margin: '12px auto', maxWidth: 900 }}>
              Sources this run: {Object.entries(searchDebug.source_counts || {}).map(([k, v]) => `${k}: ${v}`).join(' | ')}
              {searchDebug.source_notes?.length ? ` | ${searchDebug.source_notes.join(' ')}` : ''}
            </div>
          )}
          <ReviewPage
            foundPhotos={foundPhotos}
            currentPhotoIndex={currentPhotoIndex}
            showFeedbackCard={showFeedbackCard}
            showRemoveSection={showRemoveSection}
            showExitWarning={showExitWarning}
            removalPlan={removalPlan}
            removalLoading={removalLoading}
            removalError={removalError}
            handlePrevious={handlePrevious}
            handleNext={handleNext}
            handleRemoveButton={handleRemoveButton}
            handleNotMe={handleNotMe}
            handleMarkReported={handleMarkReported}
            handleCloseRemoveSection={handleCloseRemoveSection}
            handleGoHome={handleGoHome}
            confirmGoHome={confirmGoHome}
            cancelGoHome={cancelGoHome}
          />
        </>
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
