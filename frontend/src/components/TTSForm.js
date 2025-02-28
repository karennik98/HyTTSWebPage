import React, { useState, useEffect, useRef } from 'react';
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
  Alert,
  Tabs,
  Tab,
  Divider,
  Grid,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Chip,
  Snackbar,
  LinearProgress
} from '@mui/material';
import { 
  MicNone as MicIcon, 
  CloudUpload as UploadIcon, 
  TextFields as TextIcon,
  Refresh as RefreshIcon,
  ContentCopy as CopyIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import axios from 'axios';
// Import Tesseract.js for OCR
import Tesseract from 'tesseract.js';

// API endpoint - can be changed for production
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-render-app-name.onrender.com'  // Replace with your actual Render URL
  : 'http://localhost:8000';

// Styled components
const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const StyledDropzone = styled(Paper)(({ theme, isDragActive }) => ({
  padding: theme.spacing(6),
  textAlign: 'center',
  borderStyle: 'dashed',
  borderWidth: 2,
  borderColor: isDragActive ? theme.palette.primary.main : theme.palette.divider,
  backgroundColor: isDragActive ? theme.palette.primary.light : theme.palette.background.paper,
  opacity: isDragActive ? 0.6 : 1,
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  '&:hover': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.primary.light + '20',
  },
}));

const StyledAudioPlayer = styled(Box)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.grey[100],
  borderRadius: theme.shape.borderRadius,
  marginTop: theme.spacing(2),
}));

// Tab panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tts-tabpanel-${index}`}
      aria-labelledby={`tts-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const TTSForm = () => {
  // Safe audio play helper function
  const safePlayAudio = (audioUrl) => {
    const audio = new Audio();
    
    audio.onerror = (e) => {
      console.error('Error playing audio:', e);
    };
    
    audio.oncanplaythrough = () => {
      audio.play().catch(err => {
        console.error('Failed to play audio:', err);
      });
    };
    
    audio.src = audioUrl;
    return audio;
  };

  // Display name mapping
  const speakerDisplayNames = {
    'aram': 'Gor',
    'narek': 'Narek'  // Keep this the same or change as needed
  };

  // State variables
  const [text, setText] = useState('');
  const [speaker, setSpeaker] = useState('');
  const [speakers, setSpeakers] = useState([]);
  const [audioUrl, setAudioUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [imagePreview, setImagePreview] = useState('');
  const [isDragActive, setIsDragActive] = useState(false);
  const [ocrProgress, setOcrProgress] = useState(0);
  const [ocrStatus, setOcrStatus] = useState('');
  const [audioHistory, setAudioHistory] = useState([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const fileInputRef = useRef(null);
  const audioRef = useRef(null);

  // Fetch speakers on component mount
  useEffect(() => {
    const fetchSpeakers = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/speakers`);
        setSpeakers(response.data.speakers);
        if (response.data.speakers.length > 0) {
          setSpeaker(response.data.speakers[0]); // Set default speaker
        }
      } catch (err) {
        setError('Failed to load speakers. Please check your connection and try again.');
        console.error('Error fetching speakers:', err);
      }
    };
    fetchSpeakers();
  }, []);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle text submission
  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim() || !speaker) return;
    
    await generateSpeech(text);
  };

  // Generate speech from text
  const generateSpeech = async (textToConvert) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/synthesize`, {
        text: textToConvert,
        speaker_name: speaker
      });
      
      // Convert base64 to audio URL
      const blob = new Blob(
        [Uint8Array.from(atob(response.data.audio), c => c.charCodeAt(0))],
        { type: 'audio/wav' }
      );
      const url = URL.createObjectURL(blob);
      
      // Store in history
      const newHistoryItem = {
        id: Date.now(),
        text: textToConvert.substring(0, 50) + (textToConvert.length > 50 ? '...' : ''),
        speaker: speaker,
        audioUrl: url,
        fullText: textToConvert,
        date: new Date().toLocaleString()
      };
      
      setAudioHistory(prev => [newHistoryItem, ...prev].slice(0, 10)); // Keep last 10 items
      setAudioUrl(url);
      
      // Show success message
      setSnackbarMessage('Speech generated successfully!');
      setSnackbarOpen(true);
      
      // Auto-play audio safely
      if (audioRef.current) {
        audioRef.current.play().catch(err => {
          console.error('Failed to auto-play audio:', err);
        });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate speech. Please try again.');
      console.error('Error generating speech:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload for OCR
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    processImage(file);
  };

  // Handle drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processImage(e.dataTransfer.files[0]);
    }
  };

  // Process image with Tesseract OCR
  const processImage = (file) => {
    setImagePreview(URL.createObjectURL(file));
    setOcrStatus('Processing image...');
    setOcrProgress(0);
    setText(''); // Clear previous text
    
    Tesseract.recognize(
      file,
      'hye', // Armenian language code
      {
        logger: data => {
          if (data.status === 'recognizing text') {
            setOcrProgress(parseInt(data.progress * 100));
          }
        }
      }
    ).then(({ data: { text: recognizedText } }) => {
      setOcrStatus('Text extraction complete!');
      setOcrProgress(100);
      setText(recognizedText);
    }).catch(err => {
      setOcrStatus('Error processing image');
      setError('Failed to extract text from image. Please try again or enter text manually.');
      console.error('OCR Error:', err);
    });
  };

  // Copy text to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(text).then(() => {
      setSnackbarMessage('Text copied to clipboard!');
      setSnackbarOpen(true);
    });
  };

  // Clear text
  const clearText = () => {
    setText('');
    setImagePreview('');
    setOcrStatus('');
    setOcrProgress(0);
  };

  // Handle history item click
  const handleHistoryItemClick = (item) => {
    setText(item.fullText);
    setSpeaker(item.speaker);
    setAudioUrl(item.audioUrl);
  };

  // Close snackbar
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: { xs: 2, md: 4 }, mt: 4, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom align="center" sx={{ mb: 3, fontWeight: 500 }}>
          Armenian Text-to-Speech
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="TTS input methods"
            variant="fullWidth"
          >
            <Tab icon={<TextIcon />} label="Text Input" id="tts-tab-0" />
            <Tab icon={<UploadIcon />} label="Image to Text" id="tts-tab-1" />
            <Tab icon={<MicIcon />} label="History" id="tts-tab-2" />
          </Tabs>
        </Box>

        {/* Text Input Tab */}
        <TabPanel value={tabValue} index={0}>
          <form onSubmit={handleTextSubmit}>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel id="speaker-select-label">Speaker</InputLabel>
              <Select
                labelId="speaker-select-label"
                id="speaker-select"
                value={speaker}
                onChange={(e) => setSpeaker(e.target.value)}
                label="Speaker"
                required
              >
                {speakers.map((name) => (
                  <MenuItem key={name} value={name}>
                    {speakerDisplayNames[name] || name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              multiline
              rows={6}
              value={text}
              onChange={(e) => setText(e.target.value)}
              label="Enter Armenian Text"
              variant="outlined"
              required
              sx={{ mb: 3 }}
              InputProps={{
                endAdornment: text && (
                  <Box sx={{ display: 'flex' }}>
                    <Tooltip title="Copy text">
                      <IconButton onClick={copyToClipboard} edge="end">
                        <CopyIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Clear text">
                      <IconButton onClick={clearText} edge="end">
                        <RefreshIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                ),
              }}
            />

            <Button
              type="submit"
              variant="contained"
              disabled={loading || !text.trim() || !speaker}
              fullWidth
              size="large"
              sx={{ py: 1.5, borderRadius: 2 }}
              startIcon={loading ? <CircularProgress size={24} color="inherit" /> : null}
            >
              {loading ? 'Generating...' : 'Generate Speech'}
            </Button>
          </form>
        </TabPanel>

        {/* Image Upload Tab */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3 }}>
            <StyledDropzone
              isDragActive={isDragActive}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
            >
              {imagePreview ? (
                <Box>
                  <img 
                    src={imagePreview} 
                    alt="Uploaded" 
                    style={{ maxWidth: '100%', maxHeight: '200px', marginBottom: '16px' }} 
                  />
                  <Typography variant="body2">
                    Click or drag to replace image
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="h6">
                    Drag and drop an image or click to upload
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supports JPG, PNG files containing Armenian text
                  </Typography>
                </Box>
              )}
              <VisuallyHiddenInput
                type="file"
                accept="image/*"
                ref={fileInputRef}
                onChange={handleFileUpload}
              />
            </StyledDropzone>
          </Box>

          {ocrStatus && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                {ocrStatus} {ocrProgress > 0 && ocrProgress < 100 ? `(${ocrProgress}%)` : ''}
              </Typography>
              {ocrProgress > 0 && (
                <Box sx={{ width: '100%' }}>
                  <LinearProgress variant="determinate" value={ocrProgress} />
                </Box>
              )}
            </Box>
          )}

          {text && tabValue === 1 && (
            <>
              <Typography variant="h6" gutterBottom>
                Extracted Text
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                value={text}
                onChange={(e) => setText(e.target.value)}
                variant="outlined"
                sx={{ mb: 3 }}
              />

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="ocr-speaker-select-label">Speaker</InputLabel>
                <Select
                  labelId="ocr-speaker-select-label"
                  value={speaker}
                  onChange={(e) => setSpeaker(e.target.value)}
                  label="Speaker"
                  required
                >
                  {speakers.map((name) => (
                    <MenuItem key={name} value={name}>
                      {speakerDisplayNames[name] || name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="contained"
                disabled={loading || !text.trim() || !speaker}
                fullWidth
                size="large"
                sx={{ py: 1.5, borderRadius: 2 }}
                onClick={() => generateSpeech(text)}
                startIcon={loading ? <CircularProgress size={24} color="inherit" /> : null}
              >
                {loading ? 'Generating...' : 'Generate Speech from Extracted Text'}
              </Button>
            </>
          )}
        </TabPanel>

        {/* History Tab */}
        <TabPanel value={tabValue} index={2}>
          {audioHistory.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No history yet. Generate some speech to see it here.
              </Typography>
            </Box>
          ) : (
            <Box>
              <Typography variant="h6" gutterBottom>
                Recent Generations
              </Typography>
              {audioHistory.map((item) => (
                <Card key={item.id} sx={{ mb: 2, cursor: 'pointer' }} onClick={() => handleHistoryItemClick(item)}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        {item.date}
                      </Typography>
                      <Chip 
                        label={speakerDisplayNames[item.speaker] || item.speaker} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body1" gutterBottom noWrap>
                      {item.text}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <Button
                        size="small"
                        startIcon={<VisibilityIcon />}
                        onClick={(e) => {
                          e.stopPropagation();
                          setText(item.fullText);
                          setSpeaker(item.speaker);
                          setTabValue(0);
                        }}
                      >
                        View
                      </Button>
                      <Button
                        size="small"
                        color="secondary"
                        startIcon={<MicIcon />}
                        onClick={(e) => {
                          e.stopPropagation();
                          // Use the safe play method
                          safePlayAudio(item.audioUrl);
                        }}
                      >
                        Play
                      </Button>
                      <Button
                        size="small"
                        startIcon={<DownloadIcon />}
                        component="a"
                        href={item.audioUrl}
                        download={`armenian-tts-${item.id}.wav`}
                        onClick={(e) => e.stopPropagation()}
                      >
                        Download
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </TabPanel>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {/* Audio Player */}
        {audioUrl && (
          <StyledAudioPlayer>
            <Typography variant="h6" gutterBottom>
              Generated Audio
            </Typography>
            <audio 
              ref={audioRef}
              controls 
              src={audioUrl} 
              style={{ width: '100%' }}
            >
              Your browser does not support the audio element.
            </audio>
            <Button
              variant="outlined"
              href={audioUrl}
              download="armenian_speech.wav"
              sx={{ mt: 2 }}
              startIcon={<DownloadIcon />}
            >
              Download Audio
            </Button>
          </StyledAudioPlayer>
        )}
      </Paper>

      {/* Snackbar notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default TTSForm;