import { useState, useEffect } from 'react';
import { FaPlus, FaFolder } from 'react-icons/fa';
import { collectionsAPI } from '../services/api';
import './CollectionsPage.css';

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
    <div className="collections-page">
      <div className="page-header">
        <h1>🗂️ Collections</h1>
        <button
          className="btn-create"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          <FaPlus /> New Collection
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreate} className="create-form">
          <input
            type="text"
            value={newCollectionName}
            onChange={(e) => setNewCollectionName(e.target.value)}
            placeholder="Collection name"
            className="form-input"
          />
          <textarea
            value={newCollectionDesc}
            onChange={(e) => setNewCollectionDesc(e.target.value)}
            placeholder="Description (optional)"
            className="form-textarea"
            rows={3}
          />
          <div className="form-actions">
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

      <div className="collections-grid">
        {collections.map((collection) => (
          <div key={collection.id} className="collection-card">
            <div className="collection-icon">
              <FaFolder size={32} />
            </div>
            <h3>{collection.name}</h3>
            {collection.description && <p>{collection.description}</p>}
            <div className="collection-meta">
              <span>{collection.paper_count || 0} papers</span>
            </div>
          </div>
        ))}
      </div>

      {collections.length === 0 && !showCreateForm && (
        <div className="no-collections">
          <FaFolder size={64} color="#ccc" />
          <p>No collections yet</p>
          <p>Create a collection to organize your papers</p>
        </div>
      )}
    </div>
  );
}

export default CollectionsPage;
