import { createContext, useContext, useReducer, useCallback } from 'react'

// Initial state
const initialState = {
  // User state
  user: {
    id: null,
    name: '客服代表',
    role: 'customer_service',
    department: '客户关系部'
  },
  
  // UI state
  ui: {
    sidebarCollapsed: false,
    theme: 'light'
  },
  
  // Loading states
  loading: {
    global: false,
    page: false
  },
  
  // Notifications
  notifications: [],
  
  // System status
  systemStatus: {
    llmStatus: 'online', // online, degraded, offline
    lastHealthCheck: null
  }
}

// Action types
const ActionTypes = {
  SET_USER: 'SET_USER',
  CLEAR_USER: 'CLEAR_USER',
  TOGGLE_SIDEBAR: 'TOGGLE_SIDEBAR',
  SET_THEME: 'SET_THEME',
  SET_LOADING: 'SET_LOADING',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  SET_SYSTEM_STATUS: 'SET_SYSTEM_STATUS'
}

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_USER:
      return { ...state, user: { ...state.user, ...action.payload } }
    
    case ActionTypes.CLEAR_USER:
      return { ...state, user: initialState.user }
    
    case ActionTypes.TOGGLE_SIDEBAR:
      return { 
        ...state, 
        ui: { ...state.ui, sidebarCollapsed: !state.ui.sidebarCollapsed } 
      }
    
    case ActionTypes.SET_THEME:
      return { ...state, ui: { ...state.ui, theme: action.payload } }
    
    case ActionTypes.SET_LOADING:
      return { 
        ...state, 
        loading: { ...state.loading, [action.payload.key]: action.payload.value } 
      }
    
    case ActionTypes.ADD_NOTIFICATION:
      return { 
        ...state, 
        notifications: [...state.notifications, { 
          id: Date.now(), 
          ...action.payload 
        }] 
      }
    
    case ActionTypes.REMOVE_NOTIFICATION:
      return { 
        ...state, 
        notifications: state.notifications.filter(n => n.id !== action.payload) 
      }
    
    case ActionTypes.SET_SYSTEM_STATUS:
      return { 
        ...state, 
        systemStatus: { ...state.systemStatus, ...action.payload } 
      }
    
    default:
      return state
  }
}

// Context
const AppContext = createContext(null)

// Provider component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState)
  
  // Actions
  const setUser = useCallback((user) => {
    dispatch({ type: ActionTypes.SET_USER, payload: user })
  }, [])
  
  const clearUser = useCallback(() => {
    dispatch({ type: ActionTypes.CLEAR_USER })
  }, [])
  
  const toggleSidebar = useCallback(() => {
    dispatch({ type: ActionTypes.TOGGLE_SIDEBAR })
  }, [])
  
  const setTheme = useCallback((theme) => {
    dispatch({ type: ActionTypes.SET_THEME, payload: theme })
  }, [])
  
  const setLoading = useCallback((key, value) => {
    dispatch({ type: ActionTypes.SET_LOADING, payload: { key, value } })
  }, [])
  
  const addNotification = useCallback((notification) => {
    dispatch({ type: ActionTypes.ADD_NOTIFICATION, payload: notification })
    // Auto remove after 5 seconds
    setTimeout(() => {
      dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: notification.id })
    }, 5000)
  }, [])
  
  const removeNotification = useCallback((id) => {
    dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: id })
  }, [])
  
  const setSystemStatus = useCallback((status) => {
    dispatch({ type: ActionTypes.SET_SYSTEM_STATUS, payload: status })
  }, [])
  
  const value = {
    state,
    actions: {
      setUser,
      clearUser,
      toggleSidebar,
      setTheme,
      setLoading,
      addNotification,
      removeNotification,
      setSystemStatus
    }
  }
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}

// Custom hook
export function useAppContext() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider')
  }
  return context
}

// Simplified hook for just state or actions
export function useAppState() {
  const { state } = useAppContext()
  return state
}

export function useAppActions() {
  const { actions } = useAppContext()
  return actions
}
