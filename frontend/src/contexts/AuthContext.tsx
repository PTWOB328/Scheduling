import React, { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/api'

interface User {
  id: number
  username: string
  email: string
  full_name: string | null
  role: 'admin' | 'scheduler' | 'pilot'
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for stored token
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      authService.setToken(storedToken)
      // Fetch user info
      authService.getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('token')
          setToken(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    const response = await authService.login(username, password)
    setToken(response.access_token)
    localStorage.setItem('token', response.access_token)
    authService.setToken(response.access_token)
    const userData = await authService.getCurrentUser()
    setUser(userData)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    authService.setToken(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!user,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
