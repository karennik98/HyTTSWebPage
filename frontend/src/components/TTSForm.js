import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import axios from 'axios';

const TTSForm = () => {
  const [text, setText] = useState('');
  const [speaker, setSpeaker] = useState('');
  const [speakers, setSpeakers] = useState([]);
  const [audioUrl, setAudioUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch available speakers
    const fetchSpeakers = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/speakers');
        setSpeakers(response.data.speakers);
      } catch (err) {
        setError('Failed to load speakers');
      }
    };
    fetchSpeakers();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:8000/api/synthesize', {
        text,
        speaker_name: speaker
      });
      
      // Convert base64 to audio URL
      const blob = new Blob(
        [Uint8Array.from(atob(response.data.audio), c => c.charCodeAt(0))],
        { type: 'audio/wav' }
      );
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate speech');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Armenian Text-to-Speech
        </Typography>
        
        <form onSubmit={handleSubmit}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Speaker</InputLabel>
            <Select
              value={speaker}
              onChange={(e) => setSpeaker(e.target.value)}
              label="Speaker"
              required
            >
              {speakers.map((name) => (
                <MenuItem key={name} value={name}>
                  {name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            multiline
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
            label="Enter Armenian Text"
            variant="outlined"
            required
            sx={{ mb: 2 }}
          />

          <Button
            type="submit"
            variant="contained"
            disabled={loading || !text || !speaker}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : 'Generate Speech'}
          </Button>
        </form>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {audioUrl && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Generated Audio
            </Typography>
            <audio controls src={audioUrl} style={{ width: '100%' }}>
              Your browser does not support the audio element.
            </audio>
            <Button
              variant="outlined"
              href={audioUrl}
              download="generated_speech.wav"
              sx={{ mt: 1 }}
            >
              Download Audio
            </Button>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default TTSForm;