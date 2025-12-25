import { useState, useEffect } from 'react';
import { Bell, Plus, Trash2, Power, CheckCircle, XCircle, Send, Settings as SettingsIcon } from 'lucide-react';

interface Recipient {
  id: number;
  name: string;
  telegram_chat_id: string;
  email?: string;
  phone?: string;
  role: string;
  is_active: boolean;
  channels: string[];
  created_at: string;
}

interface AlertConfig {
  tds_threshold: number;
  warning_threshold: number;
  cooldown_minutes: number;
  enable_telegram: boolean;
  enable_email: boolean;
  enable_sms: boolean;
}

interface AlertStatus {
  telegram_enabled: boolean;
  tds_threshold: number;
  temp_threshold: number;
  cooldown_minutes: number;
  last_alert: string | null;
  cooldown_remaining: number;
  can_send_alert: boolean;
  bot_configured: boolean;
  bot_username: string | null;
  active_recipients: number;
  total_alerts_sent: number;
}

export default function Alerts() {
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [config, setConfig] = useState<AlertConfig | null>(null);
  const [status, setStatus] = useState<AlertStatus | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showConfigForm, setShowConfigForm] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [newRecipient, setNewRecipient] = useState({
    name: '',
    telegram_chat_id: '',
    email: '',
    phone: '',
    role: 'viewer',
    channels: ['telegram']
  });

  const API_BASE = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/alerts`;

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [recipientsRes, configRes, statusRes] = await Promise.all([
        fetch(`${API_BASE}/recipients`),
        fetch(`${API_BASE}/config`),
        fetch(`${API_BASE}/status`)
      ]);

      if (recipientsRes.ok) setRecipients(await recipientsRes.json());
      if (configRes.ok) setConfig(await configRes.json());
      if (statusRes.ok) setStatus(await statusRes.json());
    } catch (error) {
      console.error('Error fetching alert data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRecipient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/recipients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newRecipient,
          is_active: true,
          created_by: 'admin'
        })
      });

      if (response.ok) {
        setNewRecipient({
          name: '',
          telegram_chat_id: '',
          email: '',
          phone: '',
          role: 'viewer',
          channels: ['telegram']
        });
        setShowAddForm(false);
        fetchData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to add recipient');
      }
    } catch (error) {
      console.error('Error adding recipient:', error);
      alert('Failed to add recipient');
    }
  };

  const handleToggleRecipient = async (id: number) => {
    try {
      const response = await fetch(`${API_BASE}/recipients/${id}/toggle`, {
        method: 'PATCH'
      });
      if (response.ok) fetchData();
    } catch (error) {
      console.error('Error toggling recipient:', error);
    }
  };

  const handleDeleteRecipient = async (id: number) => {
    if (!confirm('Are you sure you want to delete this recipient?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/recipients/${id}`, {
        method: 'DELETE'
      });
      if (response.ok) fetchData();
    } catch (error) {
      console.error('Error deleting recipient:', error);
    }
  };

  const handleSendTestAlert = async () => {
    try {
      const response = await fetch(`${API_BASE}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'This is a test alert from Evara TDS Platform. If you receive this, your alerts are working perfectly! 🎉'
        })
      });

      const result = await response.json();
      if (response.ok) {
        alert(`✅ Test alert sent!\n\nSent: ${result.sent_successfully}/${result.recipients_total}\nBot: @${result.bot_username}`);
      } else {
        alert(`❌ Failed to send test alert\n\n${result.detail}`);
      }
    } catch (error) {
      console.error('Error sending test alert:', error);
      alert('Failed to send test alert');
    }
  };

  const handleUpdateConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;

    try {
      const response = await fetch(`${API_BASE}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        setShowConfigForm(false);
        fetchData();
        alert('✅ Configuration updated successfully');
      }
    } catch (error) {
      console.error('Error updating config:', error);
      alert('Failed to update configuration');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Bell className="text-blue-400" size={32} />
            Alert Management
          </h1>
          <p className="text-gray-400 mt-1">Configure recipients and alert settings</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSendTestAlert}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            <Send size={18} />
            Send Test Alert
          </button>
          <button
            onClick={() => setShowConfigForm(true)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            <SettingsIcon size={18} />
            Configure
          </button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            {status?.bot_configured ? (
              <CheckCircle className="text-green-400" size={24} />
            ) : (
              <XCircle className="text-red-400" size={24} />
            )}
            <div>
              <p className="text-gray-400 text-sm">Telegram Bot</p>
              <p className="text-white font-semibold">
                {status?.bot_configured ? `@${status.bot_username}` : 'Not Configured'}
              </p>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <Bell className="text-blue-400" size={24} />
            <div>
              <p className="text-gray-400 text-sm">Active Recipients</p>
              <p className="text-white font-semibold text-2xl">{status?.active_recipients || 0}</p>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-green-400" size={24} />
            <div>
              <p className="text-gray-400 text-sm">Alerts Sent</p>
              <p className="text-white font-semibold text-2xl">{status?.total_alerts_sent || 0}</p>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <SettingsIcon className="text-purple-400" size={24} />
            <div>
              <p className="text-gray-400 text-sm">TDS Threshold</p>
              <p className="text-white font-semibold text-2xl">{status?.tds_threshold || 150}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recipients Section */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Alert Recipients</h2>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            <Plus size={18} />
            Add Recipient
          </button>
        </div>

        {recipients.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="mx-auto text-gray-600 mb-4" size={48} />
            <p className="text-gray-400">No recipients configured yet</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="mt-4 text-blue-400 hover:text-blue-300"
            >
              Add your first recipient →
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Name</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Telegram ID</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Role</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Channels</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {recipients.map((recipient) => (
                  <tr key={recipient.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                    <td className="py-3 px-4 text-white">{recipient.name}</td>
                    <td className="py-3 px-4 text-gray-300 font-mono text-sm">{recipient.telegram_chat_id}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs ${
                        recipient.role === 'admin' ? 'bg-purple-500/20 text-purple-300' : 'bg-blue-500/20 text-blue-300'
                      }`}>
                        {recipient.role}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`flex items-center gap-2 ${recipient.is_active ? 'text-green-400' : 'text-gray-500'}`}>
                        {recipient.is_active ? <CheckCircle size={16} /> : <XCircle size={16} />}
                        {recipient.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1">
                        {recipient.channels.map((channel) => (
                          <span key={channel} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                            {channel}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleToggleRecipient(recipient.id)}
                          className="p-2 hover:bg-gray-700 rounded transition-colors"
                          title={recipient.is_active ? 'Deactivate' : 'Activate'}
                        >
                          <Power size={18} className={recipient.is_active ? 'text-green-400' : 'text-gray-500'} />
                        </button>
                        <button
                          onClick={() => handleDeleteRecipient(recipient.id)}
                          className="p-2 hover:bg-red-900/50 rounded transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={18} className="text-red-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Recipient Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h3 className="text-xl font-bold text-white mb-4">Add New Recipient</h3>
            <form onSubmit={handleAddRecipient} className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">Name</label>
                <input
                  type="text"
                  value={newRecipient.name}
                  onChange={(e) => setNewRecipient({ ...newRecipient, name: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Telegram Chat ID</label>
                <input
                  type="text"
                  value={newRecipient.telegram_chat_id}
                  onChange={(e) => setNewRecipient({ ...newRecipient, telegram_chat_id: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 font-mono"
                  placeholder="123456789"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">Send /start to your bot, then get ID from getUpdates</p>
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Role</label>
                <select
                  value={newRecipient.role}
                  onChange={(e) => setNewRecipient({ ...newRecipient, role: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="viewer">Viewer</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Add Recipient
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Config Modal */}
      {showConfigForm && config && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h3 className="text-xl font-bold text-white mb-4">Alert Configuration</h3>
            <form onSubmit={handleUpdateConfig} className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">TDS Threshold (ppm)</label>
                <input
                  type="number"
                  step="0.1"
                  value={config.tds_threshold}
                  onChange={(e) => setConfig({ ...config, tds_threshold: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Warning Threshold (ppm)</label>
                <input
                  type="number"
                  step="0.1"
                  value={config.warning_threshold}
                  onChange={(e) => setConfig({ ...config, warning_threshold: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Cooldown (minutes)</label>
                <input
                  type="number"
                  value={config.cooldown_minutes}
                  onChange={(e) => setConfig({ ...config, cooldown_minutes: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowConfigForm(false)}
                  className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Cooldown Status */}
      {status && status.cooldown_remaining > 0 && (
        <div className="glass-card p-4 border-l-4 border-yellow-500">
          <p className="text-yellow-300">
            ⏳ Alert cooldown active: {status.cooldown_remaining.toFixed(1)} minutes remaining
          </p>
        </div>
      )}
    </div>
  );
}
