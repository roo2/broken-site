import React, { useState } from 'react'
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

    try {
      console.log(`Making API request to: /api/diagnose/textual?mode=${diagnosisMode}`)
      
      const response = await fetch(`/api/diagnose/textual?mode=${diagnosisMode}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target: normalizedUrl }),
      })

      console.log(`API response status: ${response.status}`)

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`API error response: ${errorText}`)
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('API response data:', data)
      setResult(data)
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
      console.log('Diagnosis request completed')
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

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <h1>Site Diagnostics Pro</h1>
          <p>Simple website health checks for everyone</p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <form onSubmit={handleSubmit} className="diagnosis-form">
            <div className="mode-toggle">
              <label className="mode-label">
                <input
                  type="radio"
                  name="mode"
                  value="openai"
                  checked={diagnosisMode === 'openai'}
                  onChange={(e) => setDiagnosisMode(e.target.value)}
                  disabled={isLoading}
                />
                <span className="mode-option">
                  <Brain size={16} />
                  AI-Powered (Recommended)
                </span>
              </label>
              <label className="mode-label">
                <input
                  type="radio"
                  name="mode"
                  value="offline"
                  checked={diagnosisMode === 'offline'}
                  onChange={(e) => setDiagnosisMode(e.target.value)}
                  disabled={isLoading}
                />
                <span className="mode-option">
                  <Zap size={16} />
                  Fast Check
                </span>
              </label>
            </div>
            
            <div className="input-group">
              <Search className="search-icon" size={20} />
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter your website URL (e.g., example.com or https://example.com)"
                className="url-input"
                disabled={isLoading}
              />
              <button 
                type="submit" 
                className="submit-btn"
                disabled={isLoading || !url.trim()}
              >
                {isLoading ? (
                  <>
                    <Clock size={16} />
                    {diagnosisMode === 'openai' ? 'AI Analyzing...' : 'Checking...'}
                  </>
                ) : (
                  <>
                    <Search size={16} />
                    Check Website
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="error-message">
              <AlertCircle size={20} />
              <span>Error: {error}</span>
            </div>
          )}

          <div className="mode-info">
            <p>
              <strong>AI-Powered:</strong> Uses advanced AI to provide detailed analysis and recommendations.
              <br />
              <strong>Fast Check:</strong> Quick automated checks for common issues.
            </p>
          </div>

          {result && (
            <div className="results">
              <div className="status-card">
                <div className="status-content">
                  <h2>Diagnostic Results</h2>
                  
                  {result.mode === 'openai' ? (
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
                          {result.details}
                        </ReactMarkdown>
                      </div>
                      
                      {/* Tool Results Section */}
                      {result.tool_data && Object.keys(result.tool_data).length > 0 && (
                        <div className="tool-results-section">
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
                    <small>Analysis mode: {result.mode === 'openai' ? 'AI-Powered' : 'Fast Check'}</small>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 Site Diagnostics Pro. Built for everyone, not just tech experts.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
