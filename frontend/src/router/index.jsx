import { lazy } from 'react'
import { MainLayout } from '../components'

// Lazy load pages for better performance
const Dashboard = lazy(() => import('../pages/Dashboard'))
const QAChat = lazy(() => import('../pages/CustomerService/QAChat'))
const Knowledge = lazy(() => import('../pages/CustomerService/Knowledge'))
const Complaint = lazy(() => import('../pages/CustomerService/Complaint'))
const Script = lazy(() => import('../pages/CustomerService/Script'))
const Quality = lazy(() => import('../pages/CustomerService/Quality'))
const Training = lazy(() => import('../pages/CustomerService/Training'))
const HNWService = lazy(() => import('../pages/HNWService'))
const Analytics = lazy(() => import('../pages/Analytics'))
const Education = lazy(() => import('../pages/Education'))
const Market = lazy(() => import('../pages/Market'))
const NotFound = lazy(() => import('../pages/NotFound'))

// Route configuration
export const routes = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      // Dashboard
      {
        index: true,
        element: <Dashboard />
      },
      // F1: Customer Service Management
      {
        path: 'cs/qa',
        element: <QAChat />
      },
      {
        path: 'cs/knowledge',
        element: <Knowledge />
      },
      {
        path: 'cs/complaint',
        element: <Complaint />
      },
      {
        path: 'cs/script',
        element: <Script />
      },
      {
        path: 'cs/quality',
        element: <Quality />
      },
      {
        path: 'cs/training',
        element: <Training />
      },
      // F2: High Net Worth Service
      {
        path: 'hnw',
        element: <HNWService />
      },
      // F3: Data Analytics
      {
        path: 'analytics',
        element: <Analytics />
      },
      // F4: Education & Compliance
      {
        path: 'education',
        element: <Education />
      },
      // F5: Market Monitoring
      {
        path: 'market',
        element: <Market />
      },
      // 404 Not Found
      {
        path: '*',
        element: <NotFound />
      }
    ]
  }
]
