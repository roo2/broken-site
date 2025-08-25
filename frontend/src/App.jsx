import React, { useState, useRef, useEffect } from 'react'
import { Search, AlertCircle, CheckCircle, Clock, Shield, Globe, Server, Mail, AlertTriangle, Info, Brain, Zap } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.scss'

function App() {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false)
  const [diagnosisMode, setDiagnosisMode] = useState('openai') // Default to OpenAI mode
  const [streamingUpdates, setStreamingUpdates] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [accumulatedTextContent, setAccumulatedTextContent] = useState('')
  const updatesListRef = useRef(null)

  // Auto-scroll to bottom when new streaming updates are added
  useEffect(() => {
    if (updatesListRef.current) {
      updatesListRef.current.scrollTop = updatesListRef.current.scrollHeight
    }
  }, [streamingUpdates])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    // Normalize URL - add https:// if no protocol is provided
    let normalizedUrl = url.trim()
    if (!normalizedUrl.startsWith('http://') && !normalizedUrl.startsWith('https://')) {
      normalizedUrl = `https://${normalizedUrl}`
    }

    console.log(`Starting diagnosis for: ${normalizedUrl} (original: ${url}) with mode: ${diagnosisMode}`)
    
    setIsLoading(true)
    setError(null)
    setResult(null)
    setShowTechnicalDetails(false)
    setStreamingUpdates([])
    setIsStreaming(false)
    setAccumulatedTextContent('')

    try {
      // Always use streaming endpoint - it handles both AI and offline modes
      await handleStreamingDiagnosis(normalizedUrl)
    } catch (err) {
      console.error('Error during diagnosis:', err)
      
      // Handle specific OpenAI API key error
      if (err.message.includes('OPENAI_API_KEY') || err.message.includes('400')) {
        const errorMsg = 'OpenAI API key is required for AI-powered diagnosis. Please set your API key or use Fast Check mode.'
        console.error(errorMsg)
        setError(errorMsg)
      } else {
        console.error('Unexpected error:', err.message)
        setError(err.message)
      }
    } finally {
      setIsLoading(false)
      setIsStreaming(false)
      console.log('Diagnosis request completed')
    }
  }

  const handleStreamingDiagnosis = async (normalizedUrl) => {
    console.log('Starting streaming diagnosis...')
    setIsStreaming(true)
    
    const response = await fetch(`/api/diagnose/stream?mode=${diagnosisMode}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ target: normalizedUrl }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`Streaming API error response: ${errorText}`)
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6) // Remove 'data: ' prefix
            
            if (data === '[DONE]') {
              console.log('Streaming completed')
              return
            }

            try {
              const update = JSON.parse(data)
              console.log('Streaming update:', update)
              
              if (update.type === 'text_content') {
                // Accumulate text content for markdown rendering
                setAccumulatedTextContent(prev => prev + update.content)
              } else if (update.type === 'result') {
                setResult(update.data)
                return
              } else if (update.type === 'error') {
                setError(update.message)
                return
              } else {
                // Add other updates to the streaming updates list
                setStreamingUpdates(prev => [...prev, update])
              }
            } catch (e) {
              console.error('Error parsing streaming data:', e)
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }



  const getUrgencyIcon = (urgency) => {
    switch (urgency) {
      case 'critical': return <AlertCircle size={24} />
      case 'important': return <AlertTriangle size={24} />
      case 'minor': return <Info size={24} />
      default: return <Info size={24} />
    }
  }

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'critical': return 'error'
      case 'important': return 'warning'
      case 'minor': return 'info'
      default: return 'info'
    }
  }

  const renderStreamingUpdate = (update) => {
    switch (update.type) {
      case 'status':
        return (
          <div key={update.message} className="streaming-update status">
            <Clock size={16} />
            <span>{update.message}</span>
          </div>
        )
      case 'tool_call':
        return (
          <div key={`${update.tool}-${update.message}`} className="streaming-update tool-call">
            <Search size={16} />
            <span>{update.message}</span>
          </div>
        )
      case 'tool_result':
        return (
          <div key={`${update.tool}-result`} className="streaming-update tool-result">
            <CheckCircle size={16} />
            <span>{update.message}</span>
          </div>
        )
      case 'tool_error':
        return (
          <div key={`${update.tool}-error`} className="streaming-update tool-error">
            <AlertCircle size={16} />
            <span>{update.message}</span>
          </div>
        )
      case 'thinking':
        return (
          <div key={`thinking-${update.content}`} className="streaming-update thinking">
            <Brain size={16} />
            <span>AI is analyzing: {update.content}</span>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <h1>BrokenSite</h1>
          <p>Quickly diagnose and fix your broken site using our powerful AI assistant.</p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <form onSubmit={handleSubmit} className="diagnosis-form">
            <div className="input-group">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter your website URL (e.g., example.com or https://example.com)"
                className="url-input"
                disabled={isLoading}
              />
              <div className="button-group">
                <button 
                  type="submit" 
                  className="submit-btn secondary"
                  disabled={isLoading || !url.trim()}
                  onClick={() => setDiagnosisMode('offline')}
                >
                  {isLoading && diagnosisMode === 'offline' ? (
                    <>
                      <Clock size={18} />
                      Checking...
                    </>
                  ) : (
                    <>
                      <Zap size={18} />
                      Fast Check
                    </>
                  )}
                </button>
                <button 
                  type="submit" 
                  className="submit-btn primary"
                  disabled={isLoading || !url.trim()}
                  onClick={() => setDiagnosisMode('openai')}
                >
                  {isLoading && diagnosisMode === 'openai' ? (
                    <>
                      <Clock size={18} />
                      AI Analyzing...
                    </>
                  ) : (
                    <>
                      <Brain size={18} />
                      AI-Powered Check
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>

          {error && (
            <div className="error-message">
              <AlertCircle size={20} />
              <span>Error: {error}</span>
            </div>
          )}

          {/* Streaming Updates */}
          {(streamingUpdates.length > 0) && (
            <div className="streaming-updates">
              <h3>Live Analysis Progress</h3>
              
                             {/* Tool Updates */}
               {streamingUpdates.length > 0 && (
                 <div className="updates-list" ref={updatesListRef}>
                   {streamingUpdates.map((update, index) => renderStreamingUpdate(update))}
                 </div>
               )}
            </div>
          )}

          {(result || accumulatedTextContent) && (
            <div className="results">
              <div className="status-card">
                <div className="status-content">
                  {/* <h2>Diagnostic Results</h2> */}
                  
                  {(result?.mode === 'openai' || accumulatedTextContent) ? (
                    // OpenAI mode: Render markdown
                    <>
                      <div className="markdown-content">
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            h1: ({node, ...props}) => <h1 className="markdown-h1" {...props} />,
                            h2: ({node, ...props}) => <h2 className="markdown-h2" {...props} />,
                            h3: ({node, ...props}) => <h3 className="markdown-h3" {...props} />,
                            p: ({node, ...props}) => <p className="markdown-p" {...props} />,
                            ul: ({node, ...props}) => <ul className="markdown-ul" {...props} />,
                            ol: ({node, ...props}) => <ol className="markdown-ol" {...props} />,
                            li: ({node, ...props}) => <li className="markdown-li" {...props} />,
                            strong: ({node, ...props}) => <strong className="markdown-strong" {...props} />,
                            em: ({node, ...props}) => <em className="markdown-em" {...props} />,
                            code: ({node, ...props}) => <code className="markdown-code" {...props} />,
                            a: ({node, ...props}) => <a className="markdown-link" target="_blank" rel="noopener noreferrer" {...props} />,
                          }}
                        >
                          {result?.details || accumulatedTextContent}
                        </ReactMarkdown>
                      </div>
                      
                    </>
                  ) : (
                    // Offline mode: Use structured format
                    <>
                      <div className="summary-section">
                        <h3>Summary</h3>
                        <p>{result.summary}</p>
                      </div>
                      
                      <div className="details-section">
                        <h3>Details</h3>
                        <div className="details-content">
                          {result.details.split('\n').map((line, index) => (
                            <p key={index} className={line.startsWith('✅') ? 'success-line' : line.startsWith('🔴') ? 'error-line' : line.startsWith('🟡') ? 'warning-line' : line.startsWith('🟢') ? 'info-line' : 'normal-line'}>
                              {line}
                            </p>
                          ))}
                        </div>
                      </div>
                      
                      <div className="recommendations-section">
                        <h3>Recommendations</h3>
                        <div className="recommendations-content">
                          {result.recommendations.split('\n').map((line, index) => {
                            // Skip empty lines and "Recommendations:" header
                            if (!line.trim() || line === 'Recommendations:') return null;
                            
                            // Handle different line types
                            let className = 'normal-line';
                            let displayText = line;
                            
                            if (line.startsWith('🎉')) {
                              className = 'success-line';
                            } else if (line.startsWith('🏢') || line.startsWith('🔗') || line.startsWith('📋') || line.startsWith('🆘')) {
                              className = 'info-line';
                            } else if (line.match(/^\d+\./)) {
                              // Check if this is the first numbered step
                              const isFirstStep = index > 0 && result.recommendations.split('\n').slice(0, index).every(l => !l.trim() || l === 'Recommendations:');
                              
                              if (isFirstStep) {
                                // Remove the numbering from the first step
                                displayText = line.replace(/^\d+\.\s*/, '');
                                className = 'recommendation-intro';
                              } else {
                                className = 'recommendation-step';
                              }
                            }
                            
                            return (
                              <p key={index} className={className}>
                                {displayText}
                              </p>
                            );
                          })}
                        </div>
                      </div>
                    </>
                  )}
                  
                  <div className="mode-info">
                    <small>Analysis mode: {result?.mode === 'openai' ? 'AI-Powered' : 'Fast Check'}</small>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tool Results Section - Moved outside main results */}
          {(result?.tool_data && Object.keys(result.tool_data).length > 0) && (
            <div className="tool-results-section" style={{ marginTop: '300px' }}>
              <h3>Diagnostic Data</h3>
              <div className="tool-results-content">
                {Object.entries(result.tool_data).map(([tool_id, data], index) => (
                  <div key={index} className="tool-result">
                    <h4>Tool Call {index + 1}</h4>
                    <pre className="tool-data">
                      {JSON.stringify(data, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}

         
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 BrokenSite. Built for everyone, not just tech experts.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
