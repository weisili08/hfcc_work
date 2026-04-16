import { Suspense } from 'react'
import { useRoutes } from 'react-router-dom'
import { routes } from './router'
import { Loading } from './components/common'

function App() {
  const element = useRoutes(routes)

  return (
    <Suspense fallback={<Loading fullScreen />}>{element}</Suspense>
  )
}

export default App
