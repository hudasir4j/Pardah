import React, { useState } from 'react';
import ImageCard from './ImageCard';

function ResultsPage({ matches, onReset, searchTerms }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleReport = () => {
    const match = matches[currentIndex];
    window.open(
      `https://www.google.com/webmasters/tools/url-removal?url=${encodeURIComponent(match.url)}`,
      '_blank'
    );
  };

  const handleNext = () => {
    if (currentIndex < matches.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Results for "{searchTerms}"</h2>
        <p>Found {matches.length} matching image(s)</p>

        {matches.length === 0 ? (
          <div>
            <p className="good-news">Great news! No matching images found.</p>
            <button className="btn btn-primary" onClick={onReset}>
              Search Again
            </button>
          </div>
        ) : (
          <div>
            <ImageCard
              match={matches[currentIndex]}
              index={currentIndex}
              total={matches.length}
              onReport={handleReport}
            />

            <div className="navigation">
              <button
                className="btn btn-secondary"
                onClick={handlePrev}
                disabled={currentIndex === 0}
              >
                ← Previous
              </button>
              <button
                className="btn btn-secondary"
                onClick={handleNext}
                disabled={currentIndex === matches.length - 1}
              >
                Next →
              </button>
            </div>

            <button className="btn btn-primary" onClick={onReset}>
              Search Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsPage;