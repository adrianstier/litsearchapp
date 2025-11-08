import './LoadingSkeleton.css';

export function PaperCardSkeleton() {
  return (
    <div className="paper-card skeleton-card">
      <div className="skeleton-header">
        <div className="skeleton skeleton-title"></div>
        <div className="skeleton skeleton-title short"></div>
        <div className="skeleton-badges">
          <div className="skeleton skeleton-badge"></div>
          <div className="skeleton skeleton-badge"></div>
        </div>
      </div>
      <div className="skeleton skeleton-text"></div>
      <div className="skeleton skeleton-text short"></div>
      <div className="skeleton skeleton-abstract"></div>
      <div className="skeleton-meta">
        <div className="skeleton skeleton-meta-item"></div>
        <div className="skeleton skeleton-meta-item"></div>
        <div className="skeleton skeleton-meta-item"></div>
      </div>
      <div className="skeleton-actions">
        <div className="skeleton skeleton-button"></div>
        <div className="skeleton skeleton-button small"></div>
      </div>
    </div>
  );
}

export function CollectionCardSkeleton() {
  return (
    <div className="collection-card skeleton-card">
      <div className="skeleton skeleton-icon"></div>
      <div className="skeleton skeleton-title centered"></div>
      <div className="skeleton skeleton-text centered short"></div>
    </div>
  );
}

export function SearchBarSkeleton() {
  return (
    <div className="search-skeleton">
      <div className="skeleton skeleton-search-bar"></div>
      <div className="skeleton skeleton-button"></div>
    </div>
  );
}

export function StatBoxSkeleton() {
  return (
    <div className="stat-box skeleton-card">
      <div className="skeleton skeleton-stat-number"></div>
      <div className="skeleton skeleton-text centered"></div>
    </div>
  );
}

export function PaperGridSkeleton({ count = 6 }) {
  return (
    <div className="papers-grid">
      {Array.from({ length: count }).map((_, i) => (
        <PaperCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function CollectionGridSkeleton({ count = 4 }) {
  return (
    <div className="collections-grid">
      {Array.from({ length: count }).map((_, i) => (
        <CollectionCardSkeleton key={i} />
      ))}
    </div>
  );
}
