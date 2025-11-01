import React from 'react';

function PrivacyMessage({ onAccept }) {
  return (
    <div className="container">
      <div className="card">
        <h2>Privacy & Consent</h2>
        <div className="privacy-content">
          <h3>How This Works</h3>
          <ul>
            <li>You upload a photo of yourself</li>
            <li>We search the web using your search terms</li>
            <li>We compare faces to find images of YOU</li>
            <li>You can report those images to Google</li>
          </ul>

          <h3>Your Privacy</h3>
          <ul>
            <li>✓ Images processed locally</li>
            <li>✓ Data NOT stored permanently</li>
            <li>✓ Data NOT shared with third parties</li>
            <li>✓ Reporting done through Google</li>
          </ul>

          <p className="consent-text">
            By clicking "I Agree", you consent to upload your image and have it
            processed for face recognition purposes.
          </p>
        </div>

        <button className="btn btn-primary" onClick={onAccept}>
          I Agree & Continue
        </button>
      </div>
    </div>
  );
}

export default PrivacyMessage;