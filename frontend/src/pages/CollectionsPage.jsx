import { useState, useEffect } from 'react';
import { FaPlus, FaFolder } from 'react-icons/fa';
import { collectionsAPI } from '../services/api';

function CollectionsPage() {
  const [collections, setCollections] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDesc, setNewCollectionDesc] = useState('');

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const response = await collectionsAPI.getAll();
      setCollections(response.data);
    } catch (error) {
      console.error('Failed to load collections:', error);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newCollectionName.trim()) return;

    try {
      await collectionsAPI.create({
        name: newCollectionName,
        description: newCollectionDesc,
      });
      setNewCollectionName('');
      setNewCollectionDesc('');
      setShowCreateForm(false);
      loadCollections();
    } catch (error) {
      alert('Failed to create collection: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 dark:text-slate-50">
            🗂️ Collections
          </h1>
        </div>
        <button
          className="btn-primary flex items-center gap-2 w-fit"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          <FaPlus />
          <span>New Collection</span>
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <form onSubmit={handleCreate} className="card space-y-4 animate-scale-in">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50">
            Create New Collection
          </h3>
          <input
            type="text"
            value={newCollectionName}
            onChange={(e) => setNewCollectionName(e.target.value)}
            placeholder="Collection name"
            className="input"
            autoFocus
            required
          />
          <textarea
            value={newCollectionDesc}
            onChange={(e) => setNewCollectionDesc(e.target.value)}
            placeholder="Description (optional)"
            className="input min-h-[80px] resize-y"
            rows={3}
          />
          <div className="flex gap-3">
            <button type="submit" className="btn-primary">
              Create
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Collections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {collections.map((collection) => (
          <div
            key={collection.id}
            className="card-hover group cursor-pointer"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-primary-200 dark:group-hover:bg-primary-900/50 transition-colors">
                <FaFolder size={24} className="text-primary-600 dark:text-primary-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50 truncate">
                  {collection.name}
                </h3>
                {collection.description && (
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                    {collection.description}
                  </p>
                )}
                <div className="mt-3 flex items-center gap-2">
                  <span className="badge bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300">
                    {collection.paper_count || 0} papers
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {collections.length === 0 && !showCreateForm && (
        <div className="flex flex-col items-center justify-center py-16 space-y-4 text-center">
          <div className="w-20 h-20 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center">
            <FaFolder size={40} className="text-slate-400 dark:text-slate-600" />
          </div>
          <div className="space-y-1">
            <p className="text-lg font-semibold text-slate-900 dark:text-slate-50">
              No collections yet
            </p>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Create a collection to organize your papers
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default CollectionsPage;
