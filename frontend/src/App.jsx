import React, { useState } from 'react'
import CircularProgress from '@mui/material/CircularProgress';

export default function App() {
  const [employeeIdInput, setEmployeeIdInput] = useState('')
  const [currentEmployee, setCurrentEmployee] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false)
  const [isLoadingSubmission, setIsLoadingSubmission] = useState(false)
  const [currentSummary, setCurrentSummary] = useState(null)
  const [isSummary, setIsSummary] = useState(false)
  const [error, setError] = useState(null)

  async function handleLogin(e) {
    e?.preventDefault?.()
    setIsLoadingQuestion(true)
    setError(null)

    try {
      const res = await fetch('http://127.0.0.1:5000/get-employees')
      if (!res.ok) throw new Error('Failed to fetch employees')
      const employees = await res.json()
      const trimmed = employeeIdInput.trim()
      const foundEmployee = employees.find(emp => emp.id === trimmed)

      if (foundEmployee) {
        setCurrentEmployee(foundEmployee)
        await fetchQuestion(foundEmployee.id)
      } else {
        setError('Employee ID not found.')
        setIsLoadingQuestion(false)
      }
    } catch (err) {
      setError('Unable to reach backend. Is it running on port 5000?')
      setIsLoadingQuestion(false)
    }
  }

  async function handleSummaryLogin(e) {
    e?.preventDefault?.()
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('http://127.0.0.1:5000/get-employees')
      if (!res.ok) throw new Error('Failed to fetch employees')
      const employees = await res.json()
      const trimmed = employeeIdInput.trim()
      const foundEmployee = employees.find(emp => emp.id === trimmed)

      if (foundEmployee) {
        setCurrentEmployee(foundEmployee)
        await fetchQuestion(foundEmployee.id)
      } else {
        setError('Employee ID not found.')
        setIsLoading(false)
      }
    } catch (err) {
      setError('Unable to reach backend. Is it running on port 5000?')
      setIsLoading(false)
    }
  }

  async function fetchQuestion(employeeId) {
    setIsLoadingQuestion(true)
    setError(null)
    try {
      const res = await fetch('http://127.0.0.1:5000/get-question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ employee_id: employeeId })
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || 'Failed to fetch question')
      }
      const question = await res.json()
      setCurrentQuestion(question)
    } catch (err) {
      setError('Failed to fetch question.')
    } finally {
      setIsLoadingQuestion(false)
    }
  }

  async function handleSubmitAnswer(answer) {
    if (!currentEmployee || !currentQuestion) return
    setIsLoadingSubmission(true)

    try {
      const res = await fetch('http://127.0.0.1:5000/get-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_id: currentEmployee.id,
          question: currentQuestion.question,
          answer: answer,
          options: currentQuestion.options
        })
      })
      if (!res.ok) throw new Error('Failed to submit answer')
      const feedback = await res.json()
      setFeedback(feedback.text)
      await write_summary(answer)
    } catch (err) {
      setError('Failed to submit answer.')
    } finally {
      setIsLoadingSubmission(false)
    }
  }

  async function write_summary(answer) {
    try {
      const res = await fetch('http://127.0.0.1:5000/write-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_id: currentEmployee.id,
          question: currentQuestion.question,
          answer: answer
        })
      }) 
      if (!res.ok) throw new Error('Failed to submit answer')
    } catch (err) {
      setError('Failed to submit answer.')
    }
  }

  async function handleSummaryLogin(e) {
    e?.preventDefault?.()
    setIsLoadingQuestion(true)
    setError(null)

    try {
      const res = await fetch('http://127.0.0.1:5000/get-employees')
      if (!res.ok) throw new Error('Failed to fetch employees')
      const employees = await res.json()
      const trimmed = employeeIdInput.trim()
      const foundEmployee = employees.find(emp => emp.id === trimmed)

      if (foundEmployee) {
        setCurrentEmployee(foundEmployee)
        await fetchSummary(foundEmployee.id)
      } else {
        setError('Employee ID not found.')
        setIsLoadingQuestion(false)
      }
    } catch (err) {
      setError('Unable to reach backend. Is it running on port 5000?')
      setIsLoadingQuestion(false)
    }
  }

  async function fetchSummary(employeeId) {
    setIsLoadingQuestion(true)
    setError(null)
    try {
      const res = await fetch('http://127.0.0.1:5000/get-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ employee_id: employeeId })
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || 'Failed to fetch summary')
      }
      const summary = await res.json()
      setCurrentSummary(summary.text)
    } catch (err) {
      setError('Failed to fetch summary.')
    } finally {
      setIsLoadingQuestion(false)
    }
  }

  function handleViewSummary() {
    setIsSummary(true)
    setCurrentQuestion(null)
  }

  function handleViewMainPage() {
    setIsSummary(false)
    setCurrentSummary(null)
  }

  function handleLogout() {
    setCurrentEmployee(null)
    setCurrentQuestion(null)
    setEmployeeIdInput('')
    setFeedback(null)
    setError(null)
    setIsLoadingQuestion(false)
    setIsLoadingSubmission(false)
  }

  const renderQuiz = (
    <div className="container">
      {!currentEmployee && (
        <form className="card" onSubmit={handleLogin}>
          <h1>PSA Check In</h1>
          <h1>Enter Employee ID</h1>
          <input
            type="text"
            placeholder="e.g., EMP-20001"
            value={employeeIdInput}
            onChange={e => setEmployeeIdInput(e.target.value)}
            disabled={isLoadingQuestion}
            aria-label="Employee ID"
            autoFocus
          />
          <button type="submit" disabled={isLoadingQuestion || !employeeIdInput.trim()}>
            {isLoadingQuestion ? 'Checking…' : 'Check In'}
          </button>
          <button className="secondary" onClick={handleViewSummary}>View Performance</button>
          {error && <div className="error" role="alert">{error}</div>}
        </form>
      )}

      {currentEmployee && isLoadingQuestion && (
        <div className="card">
          <h2>Loading Question ......</h2>
        </div>
      )}

      {!feedback && currentEmployee && isLoadingSubmission && (
        <div className="card">
          <h2>Submitting Answer ......</h2>
        </div>
      )}

      {currentEmployee && !isLoadingQuestion && !isLoadingSubmission && currentQuestion && !feedback && (
        <div className="card">
          <div className="header">
            <h2>Quiz for {currentEmployee.name}</h2>
          </div>
          <h3 className="question-text">{currentQuestion.question}</h3>
          <div className="options">
            {currentQuestion.options?.map(opt => (
              <button
                key={String(opt)}
                onClick={() => handleSubmitAnswer(opt)}
                disabled={isLoadingQuestion}
              >
                {String(opt)}
              </button>
            ))}
          </div>
          {error && <div className="error" role="alert">{error}</div>}
        </div>
      )}

      {feedback && (
        <div className="card">
          <div className="header">
            <h2>Feedback for {currentEmployee.name}</h2>
            {isLoadingSubmission && <button className="secondary" disabled><CircularProgress size="1.5rem" /></button>}
            {!isLoadingSubmission && <button className="secondary" onClick={handleLogout}>Leave</button>}
          </div>
          <h3 className="question-text">{feedback}</h3>
          {error && <div className="error" role="alert">{error}</div>}
        </div>
      )}
    </div>
  )

  const renderSummary = (
    <div className="container">
      {!currentEmployee && (
        <form className="card" onSubmit={handleSummaryLogin}>
          <h1>Performance Summary</h1>
          <h1>Enter Employee ID</h1>
          <input
            type="text"
            placeholder="e.g., EMP-20001"
            value={employeeIdInput}
            onChange={e => setEmployeeIdInput(e.target.value)}
            disabled={isLoadingQuestion}
            aria-label="Employee ID"
            autoFocus
          />
          <button type="submit" disabled={isLoadingQuestion || !employeeIdInput.trim()}>
            {isLoadingQuestion ? 'Checking…' : 'Check Performance'}
          </button>
          <button className="secondary" onClick={handleViewMainPage}>Back</button>
          {error && <div className="error" role="alert">{error}</div>}
        </form>
      )}

      {currentEmployee && isLoadingQuestion && (
        <div className="card">
          <h2>Loading performance…</h2>
        </div>
      )}

      {currentEmployee && !isLoadingQuestion && currentSummary && (
        <div className="card">
          <div className="header">
            <h2>Performance summary for {currentEmployee.name}</h2>
            <button className="secondary" onClick={handleLogout}>Logout</button>
          </div>
          <h3 className="summary-content">{currentSummary}</h3>
          {error && <div className="error" role="alert">{error}</div>}
        </div>
      )}
    </div>
  )

  return (
    <div className="container">
      {!isSummary && renderQuiz}
      {isSummary && renderSummary}
    </div>
  );
}
