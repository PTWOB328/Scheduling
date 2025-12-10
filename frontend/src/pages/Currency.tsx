import React, { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  LinearProgress,
} from '@mui/material'
import { Upload } from '@mui/icons-material'
import { currencyService } from '../services/api'

const Currency: React.FC = () => {
  const [file, setFile] = useState<File | null>(null)
  const [fileType, setFileType] = useState<'excel' | 'csv'>('excel')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      const fileName = e.target.files[0].name.toLowerCase()
      if (fileName.endsWith('.csv')) {
        setFileType('csv')
      } else {
        setFileType('excel')
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'Please select a file' })
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      await currencyService.import(file, fileType)
      setMessage({ type: 'success', text: 'Currency data imported successfully' })
      setFile(null)
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Error importing currency data',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Currency Import
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1" paragraph>
          Upload a spreadsheet (Excel or CSV) containing currency data. The system will parse the
          file and import currency records for pilots.
        </Typography>
        <Box sx={{ mt: 3 }}>
          <input
            accept=".xlsx,.xls,.csv"
            style={{ display: 'none' }}
            id="currency-file-upload"
            type="file"
            onChange={handleFileChange}
          />
          <label htmlFor="currency-file-upload">
            <Button variant="outlined" component="span" startIcon={<Upload />}>
              Select File
            </Button>
          </label>
          {file && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected: {file.name}
            </Typography>
          )}
        </Box>
        {loading && <LinearProgress sx={{ mt: 2 }} />}
        {message && (
          <Alert severity={message.type} sx={{ mt: 2 }}>
            {message.text}
          </Alert>
        )}
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || loading}
          sx={{ mt: 2 }}
        >
          Upload and Import
        </Button>
      </Paper>
    </Box>
  )
}

export default Currency
