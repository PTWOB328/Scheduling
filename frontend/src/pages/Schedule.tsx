import React, { useState, useEffect } from 'react'
import { Calendar, momentLocalizer, View } from 'react-big-calendar'
import moment from 'moment'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
} from '@mui/material'
import { Add, Delete } from '@mui/icons-material'
import { eventService } from '../services/api'
import { format } from 'date-fns'

const localizer = momentLocalizer(moment)

interface Event {
  id: number
  title: string
  start: Date
  end: Date
  event_type: 'flight' | 'simulator'
  status: 'scheduled' | 'effective' | 'cancelled'
}

const Schedule: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([])
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [view, setView] = useState<View>('month')
  const [date, setDate] = useState(new Date())

  useEffect(() => {
    loadEvents()
  }, [])

  const loadEvents = async () => {
    try {
      const response = await eventService.getAll()
      const formattedEvents = response.data.map((e: any) => ({
        id: e.id,
        title: e.title,
        start: new Date(e.start_time),
        end: new Date(e.end_time),
        event_type: e.event_type,
        status: e.status,
      }))
      setEvents(formattedEvents)
    } catch (error) {
      console.error('Error loading events:', error)
    }
  }

  const handleSelectEvent = (event: Event) => {
    setSelectedEvent(event)
    setOpenDialog(true)
  }

  const handleSelectSlot = ({ start, end }: { start: Date; end: Date }) => {
    setSelectedEvent({
      id: 0,
      title: '',
      start,
      end,
      event_type: 'flight',
      status: 'scheduled',
    })
    setOpenDialog(true)
  }

  const eventStyleGetter = (event: Event) => {
    let backgroundColor = '#3174ad'
    if (event.event_type === 'simulator') {
      backgroundColor = '#7cb342'
    }
    if (event.status === 'cancelled') {
      backgroundColor = '#d32f2f'
    }
    if (event.status === 'effective') {
      backgroundColor = '#388e3c'
    }
    return {
      style: {
        backgroundColor,
        borderRadius: '5px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block',
      },
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Schedule</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleSelectSlot({ start: new Date(), end: new Date() })}
        >
          New Event
        </Button>
      </Box>
      <Box height="600px">
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          onSelectEvent={handleSelectEvent}
          onSelectSlot={handleSelectSlot}
          selectable
          view={view}
          onView={setView}
          date={date}
          onNavigate={setDate}
          eventPropGetter={eventStyleGetter}
        />
      </Box>
      {openDialog && selectedEvent && (
        <EventDialog
          event={selectedEvent}
          open={openDialog}
          onClose={() => {
            setOpenDialog(false)
            setSelectedEvent(null)
          }}
          onSave={loadEvents}
        />
      )}
    </Box>
  )
}

interface EventDialogProps {
  event: Event
  open: boolean
  onClose: () => void
  onSave: () => void
}

const EventDialog: React.FC<EventDialogProps> = ({ event, open, onClose, onSave }) => {
  const [title, setTitle] = useState(event.title)
  const [startTime, setStartTime] = useState(format(event.start, "yyyy-MM-dd'T'HH:mm"))
  const [endTime, setEndTime] = useState(format(event.end, "yyyy-MM-dd'T'HH:mm"))
  const [eventType, setEventType] = useState(event.event_type)
  const [loading, setLoading] = useState(false)

  const handleSave = async () => {
    setLoading(true)
    try {
      const eventData = {
        title,
        start_time: startTime,
        end_time: endTime,
        event_type: eventType,
        status: 'scheduled',
      }
      if (event.id === 0) {
        await eventService.create(eventData)
      } else {
        await eventService.update(event.id, eventData)
      }
      onSave()
      onClose()
    } catch (error) {
      console.error('Error saving event:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (event.id === 0) {
      onClose()
      return
    }
    setLoading(true)
    try {
      await eventService.delete(event.id)
      onSave()
      onClose()
    } catch (error) {
      console.error('Error deleting event:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{event.id === 0 ? 'New Event' : 'Edit Event'}</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Start Time"
          type="datetime-local"
          value={startTime}
          onChange={(e) => setStartTime(e.target.value)}
          margin="normal"
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          fullWidth
          label="End Time"
          type="datetime-local"
          value={endTime}
          onChange={(e) => setEndTime(e.target.value)}
          margin="normal"
          InputLabelProps={{ shrink: true }}
        />
        <FormControl fullWidth margin="normal">
          <InputLabel>Event Type</InputLabel>
          <Select value={eventType} onChange={(e) => setEventType(e.target.value as 'flight' | 'simulator')}>
            <MenuItem value="flight">Flight</MenuItem>
            <MenuItem value="simulator">Simulator</MenuItem>
          </Select>
        </FormControl>
      </DialogContent>
      <DialogActions>
        {event.id !== 0 && (
          <Button onClick={handleDelete} color="error" disabled={loading}>
            <Delete /> Delete
          </Button>
        )}
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSave} variant="contained" disabled={loading}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default Schedule
