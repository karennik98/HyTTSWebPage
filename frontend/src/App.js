import React from 'react';
import { createTheme, ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import TTSForm from './components/TTSForm';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#4a6da7',  // Updated to a nicer blue shade
    },
    secondary: {
      main: '#d81b60',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',  // Prevents ALL CAPS in buttons
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,  // More rounded corners
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 6px 20px rgba(0, 0, 0, 0.08)',  // Softer shadow
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.12)',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <TTSForm />
    </ThemeProvider>
  );
}

export default App;