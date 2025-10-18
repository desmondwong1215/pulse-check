import React, { useState } from 'react'

export default function App() {
  const [employeeIdInput, setEmployeeIdInput] = useState('')
  const [currentEmployee, setCurrentEmployee] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [currentSummary, setCurrentSummary] = useState(null)
  const [isSummary, setIsSummary] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleLogin(e) {
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
    setIsLoading(true)
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
      setIsLoading(false)
    }
  }

  async function handleSubmitAnswer(result) {
    if (!currentEmployee || !currentQuestion) return
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('http://127.0.0.1:5000/submit-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_id: currentEmployee.id,
          question: currentQuestion.question,
          result: result
        })
      })
      if (!res.ok) throw new Error('Failed to submit answer')
      await fetchQuestion(currentEmployee.id)
    } catch (err) {
      setError('Failed to submit answer.')
      setIsLoading(false)
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
        await fetchSummary(foundEmployee.id)
      } else {
        setError('Employee ID not found.')
        setIsLoading(false)
      }
    } catch (err) {
      setError('Unable to reach backend. Is it running on port 5000?')
      setIsLoading(false)
    }
  }

  async function fetchSummary(employeeId) {
    setIsLoading(true)
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
      setIsLoading(false)
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
    setError(null)
    setIsLoading(false)
  }

  const renderQuiz = (
    <div className="container">
      {!currentEmployee && (
        <form className="card" onSubmit={handleLogin}>
          <h1>PSA Employee Check In</h1>
          <h2>Enter Employee ID</h2>
          <input
            type="text"
            placeholder="e.g., EMP-20001"
            value={employeeIdInput}
            onChange={e => setEmployeeIdInput(e.target.value)}
            disabled={isLoading}
            aria-label="Employee ID"
            autoFocus
          />
          <button type="submit" disabled={isLoading || !employeeIdInput.trim()}>
            {isLoading ? 'Checking…' : 'Start Quiz'}
          </button>
          <button className="secondary" onClick={handleViewSummary}>View Summary</button>
          {error && <div className="error" role="alert">{error}</div>}
        </form>
      )}

      {currentEmployee && isLoading && (
        <div className="card">
          <h2>Loading question…</h2>
        </div>
      )}

      {currentEmployee && !isLoading && currentQuestion && (
        <div className="card">
          <div className="header">
            <h2>Check in Quiz for {currentEmployee.id}</h2>
            <button className="secondary" onClick={handleLogout}>Logout</button>
          </div>
          <h3 className="question-text">{currentQuestion.question}</h3>
          <div className="options">
            {currentQuestion.options?.map(opt => (
              <button
                key={String(opt)}
                onClick={() => handleSubmitAnswer(opt)}
                disabled={isLoading}
              >
                {String(opt)}
              </button>
            ))}
          </div>
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
          <h2>Enter Employee ID</h2>
          <input
            type="text"
            placeholder="e.g., EMP-20001"
            value={employeeIdInput}
            onChange={e => setEmployeeIdInput(e.target.value)}
            disabled={isLoading}
            aria-label="Employee ID"
            autoFocus
          />
          <button type="submit" disabled={isLoading || !employeeIdInput.trim()}>
            {isLoading ? 'Checking…' : 'Check Performance'}
          </button>
          <button className="secondary" onClick={handleViewMainPage}>Back</button>
          {error && <div className="error" role="alert">{error}</div>}
        </form>
      )}

      {currentEmployee && isLoading && (
        <div className="card">
          <h2>Loading summary…</h2>
        </div>
      )}

      {currentEmployee && !isLoading && currentSummary && (
        <div className="card">
          <div className="header">
            <h2>Performance summary for {currentEmployee.id}</h2>
            <button className="secondary" onClick={handleLogout}>Logout</button>
          </div>
          <h3 className="question-text">{currentSummary}</h3>
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
