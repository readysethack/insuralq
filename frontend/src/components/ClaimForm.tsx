import React, { useState } from 'react';

interface ClaimFormProps {
  onSubmit?: (data: any) => void;
}

const ClaimForm: React.FC<ClaimFormProps> = ({ onSubmit }) => {
  const [claimText, setClaimText] = useState('');
  const [incidentDate, setIncidentDate] = useState('');
  const [policyNumber, setPolicyNumber] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    const formData = new FormData();
    formData.append('claim_text', claimText);
    formData.append('incident_date', incidentDate);
    formData.append('policy_number', policyNumber);
    if (files) {
      Array.from(files).forEach((file) => {
        formData.append('files', file);
      });
    }
    try {
      const res = await fetch('/api/claims', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Submission failed');
      setResult(data);
      if (onSubmit) onSubmit(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="max-w-lg mx-auto p-6 bg-white rounded shadow" onSubmit={handleSubmit}>
      <h2 className="text-2xl font-bold mb-4">Submit a New Claim</h2>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Claim Text</label>
        <textarea
          className="w-full border rounded p-2"
          value={claimText}
          onChange={e => setClaimText(e.target.value)}
          required
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Incident Date</label>
        <input
          type="date"
          className="w-full border rounded p-2"
          value={incidentDate}
          onChange={e => setIncidentDate(e.target.value)}
          required
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Policy Number</label>
        <input
          type="text"
          className="w-full border rounded p-2"
          value={policyNumber}
          onChange={e => setPolicyNumber(e.target.value)}
          required
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Attach Files (optional)</label>
        <input
          type="file"
          className="w-full"
          multiple
          onChange={e => setFiles(e.target.files)}
        />
      </div>
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        disabled={loading}
      >
        {loading ? 'Submitting...' : 'Submit Claim'}
      </button>
      {error && <div className="mt-4 text-red-600">{error}</div>}
      {result && (
        <div className="mt-4 p-3 bg-green-100 rounded">
          <div className="font-semibold">Claim submitted!</div>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </form>
  );
};

export default ClaimForm;
