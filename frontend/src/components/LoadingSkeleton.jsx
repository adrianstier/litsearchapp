export function PaperCardSkeleton() {
  return (
    <div className="card animate-pulse">
      {/* Header */}
      <div className="space-y-3">
        <div className="h-6 w-3/4 bg-slate-200 dark:bg-slate-700 rounded"></div>
        <div className="h-6 w-1/2 bg-slate-200 dark:bg-slate-700 rounded"></div>
        <div className="flex gap-2">
          <div className="h-5 w-16 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
          <div className="h-5 w-16 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
        </div>
      </div>

      {/* Authors */}
      <div className="h-4 w-2/3 bg-slate-200 dark:bg-slate-700 rounded"></div>

      {/* Abstract */}
      <div className="space-y-2">
        <div className="h-4 w-full bg-slate-200 dark:bg-slate-700 rounded"></div>
        <div className="h-4 w-full bg-slate-200 dark:bg-slate-700 rounded"></div>
        <div className="h-4 w-3/4 bg-slate-200 dark:bg-slate-700 rounded"></div>
      </div>

      {/* Metadata */}
      <div className="flex gap-4">
        <div className="h-3 w-20 bg-slate-200 dark:bg-slate-700 rounded"></div>
        <div className="h-3 w-24 bg-slate-200 dark:bg-slate-700 rounded"></div>
        <div className="h-3 w-20 bg-slate-200 dark:bg-slate-700 rounded"></div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-2">
        <div className="flex-1 h-10 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
        <div className="h-10 w-24 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
      </div>
    </div>
  );
}

export function CollectionCardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="flex flex-col items-center space-y-3">
        <div className="h-16 w-16 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
        <div className="h-6 w-32 bg-slate-200 dark:bg-slate-700 rounded"></div>
        <div className="h-4 w-24 bg-slate-200 dark:bg-slate-700 rounded"></div>
      </div>
    </div>
  );
}

export function SearchBarSkeleton() {
  return (
    <div className="flex gap-3 animate-pulse">
      <div className="flex-1 h-12 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
      <div className="h-12 w-32 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
    </div>
  );
}

export function StatBoxSkeleton() {
  return (
    <div className="card animate-pulse flex flex-col items-center space-y-2">
      <div className="h-12 w-24 bg-slate-200 dark:bg-slate-700 rounded"></div>
      <div className="h-4 w-32 bg-slate-200 dark:bg-slate-700 rounded"></div>
    </div>
  );
}

export function PaperGridSkeleton({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <PaperCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function CollectionGridSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <CollectionCardSkeleton key={i} />
      ))}
    </div>
  );
}
