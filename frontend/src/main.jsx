import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// 初始化深色模式為預設
if (!localStorage.getItem('theme')) {
  localStorage.setItem('theme', 'dark')
  document.documentElement.classList.add('dark')
} else if (localStorage.getItem('theme') === 'dark') {
  document.documentElement.classList.add('dark')
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
