import React from 'react';

function ImageCard({ match, index, total, onReport }) {
  return (
    <div className="image-card">
      <div className="card-header">
        <span>{index + 1} of {total}</span>
        <span className="similarity">
          {(match.similarity_score * 100).toFixed(0)}% Match
        </span>
      </div>

      <img src={match.url} alt="match" className="card-image" />

      <div className="card-info">
        <p>
          <strong>Similarity:</strong> {(match.distance).toFixed(3)}
        </p>
        <p>
          <strong>Source:</strong> {match.source}
        </p>
        <a href={match.url} target="_blank" rel="noopener noreferrer">
          View Image →
        </a>
      </div>

      <button className="btn btn-report" onClick={onReport}>
        Report This Image
      </button>
    </div>
  );
}

export default ImageCard;