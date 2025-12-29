import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';

interface Recipient {
  id: string;
  name: string;
  email: string;
  addedAt: string;
}

const Recipients: React.FC = () => {
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  const loadRecipients = async () => {
    try {
      const response = await axios.get('/api/v1/recipients');
      setRecipients(response.data);
    } catch (error) {
      console.error('Failed to load recipients:', error);
    }
  };

  useEffect(() => {
    loadRecipients();
  }, []);

  const handleAddRecipient = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim() || !email.trim()) {
      toast.error('Please enter both name and email');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/api/v1/recipients', { name, email });
      toast.success(`Added ${name} to recipients list`);
      setName('');
      setEmail('');
      loadRecipients();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add recipient');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRecipient = async (id: string, name: string) => {
    if (!confirm(`Remove ${name} from recipients list?`)) return;

    try {
      await axios.delete(`/api/v1/recipients/${id}`);
      toast.success(`Removed ${name} from recipients list`);
      loadRecipients();
    } catch (error) {
      toast.error('Failed to remove recipient');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Email Recipients</h1>
          <p className="text-gray-400">Manage email recipients for automated TDS alerts</p>
        </div>

        {/* Add Recipient Form */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 mb-6 border border-purple-500/20">
          <h2 className="text-2xl font-bold text-white mb-4">Add New Recipient</h2>
          <form onSubmit={handleAddRecipient} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter recipient name"
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="recipient@example.com"
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold rounded-xl shadow-lg shadow-purple-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Adding...' : 'Add Recipient'}
            </button>
          </form>
        </div>

        {/* Recipients List */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20">
          <h2 className="text-2xl font-bold text-white mb-4">Current Recipients ({recipients.length})</h2>
          
          {recipients.length === 0 ? (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <p className="text-gray-400">No recipients added yet</p>
              <p className="text-sm text-gray-500 mt-2">Add recipients above to receive email alerts</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recipients.map((recipient) => (
                <div
                  key={recipient.id}
                  className="flex items-center justify-between p-4 bg-gray-900/50 rounded-xl border border-gray-700 hover:border-purple-500/50 transition-all"
                >
                  <div className="flex-1">
                    <h3 className="text-white font-semibold">{recipient.name}</h3>
                    <p className="text-gray-400 text-sm">{recipient.email}</p>
                    <p className="text-gray-600 text-xs mt-1">
                      Added: {new Date(recipient.addedAt).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteRecipient(recipient.id, recipient.name)}
                    className="px-4 py-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded-lg border border-red-500/30 transition-all"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-500/10 border border-blue-500/30 rounded-2xl p-4">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-blue-400 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="text-blue-300 font-semibold mb-1">Email Alert Information</h4>
              <p className="text-blue-200/70 text-sm">
                Recipients will receive automated email alerts when TDS or Temperature exceeds the configured thresholds. 
                Alerts are throttled to prevent spam (maximum 1 email per 15 minutes per alert type).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Recipients;
