import React, { useState } from 'react'

export default function App() {
  const [employeeIdInput, setEmployeeIdInput] = useState('')
  const [currentEmployee, setCurrentEmployee] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false)
  const [isLoadingSubmission, setIsLoadingSubmission] = useState(false)
  const [error, setError] = useState(null)

  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

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
      setError('Failed to fetch next question.')
    } finally {
      setIsLoadingQuestion(false)
    }
  }

  async function handleSubmitAnswer(result) {
    if (!currentEmployee || !currentQuestion) return
    setIsLoadingSubmission(true)

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
      setFeedback("Thank for answering the question")
      await write_summary(result)
    } catch (err) {
      setError('Failed to submit answer.')
    } finally {
      setIsLoadingSubmission(false)
    }
  }

  async function write_summary(result) {
    try {
      const res = await fetch('http://127.0.0.1:5000/write-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_id: currentEmployee.id,
          question: currentQuestion.question,
          result: result
        })
      }) 
      if (!res.ok) throw new Error('Failed to submit answer')
    } catch (err) {
      setError('Failed to submit answer.')
    }
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

  return (
    <div className="container">
      {!currentEmployee && (
        <form className="card" onSubmit={handleLogin}>
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
            {isLoadingQuestion ? 'Checking…' : 'Start Quiz'}
          </button>
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
            {isLoadingSubmission && <button className="secondary" disabled>Loading...</button>}
            {!isLoadingSubmission && <button className="secondary" onClick={handleLogout}>❌</button>}
          </div>
          <h3 className="question-text">{feedback}</h3>
          {error && <div className="error" role="alert">{error}</div>}
        </div>
      )}
    </div>
  )
}
