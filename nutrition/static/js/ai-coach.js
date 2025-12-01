// AI Coach JavaScript functionality

class AICoach {
  constructor() {
    this.baseUrl = "/api/coach"
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
  }

  async getDailyTip() {
    const cacheKey = "daily-tip"
    const cached = this.getFromCache(cacheKey)

    if (cached) {
      return cached
    }

    try {
      const response = await fetch(`${this.baseUrl}/daily-tip`)
      const data = await response.json()

      if (data.success) {
        this.setCache(cacheKey, data)
        return data
      } else {
        throw new Error(data.error || "Failed to get daily tip")
      }
    } catch (error) {
      console.error("Error getting daily tip:", error)
      return {
        success: false,
        tip: "Stay hydrated and eat a variety of colorful foods today!",
        error: error.message,
      }
    }
  }

  async getWeeklyInsights() {
    try {
      const response = await fetch(`${this.baseUrl}/weekly-insights`)
      const data = await response.json()
      return data
    } catch (error) {
      console.error("Error getting weekly insights:", error)
      return {
        success: false,
        insights: "Keep up the great work with your nutrition journey!",
        error: error.message,
      }
    }
  }

  async getGoalCoaching() {
    try {
      const response = await fetch(`${this.baseUrl}/goal-coaching`)
      const data = await response.json()
      return data
    } catch (error) {
      console.error("Error getting goal coaching:", error)
      return {
        success: false,
        coaching: "Focus on consistent, small changes to reach your health goals!",
        error: error.message,
      }
    }
  }

  async getMealFeedback(mealId) {
    try {
      const response = await fetch(`${this.baseUrl}/meal-feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCSRFToken(),
        },
        body: JSON.stringify({ meal_id: mealId }),
      })

      const data = await response.json()
      return data
    } catch (error) {
      console.error("Error getting meal feedback:", error)
      return {
        success: false,
        analysis: "This meal looks nutritious! Keep up the good work.",
        error: error.message,
      }
    }
  }

  getFromCache(key) {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data
    }
    return null
  }

  setCache(key, data) {
    this.cache.set(key, {
      data: data,
      timestamp: Date.now(),
    })
  }

  getCSRFToken() {
    const token = document.querySelector("meta[name=csrf-token]")
    return token ? token.getAttribute("content") : ""
  }

  // UI Helper Methods
  displayTip(tip, containerId) {
    const container = document.getElementById(containerId)
    if (container) {
      container.innerHTML = `
                <div class="ai-tip">
                    <div class="tip-icon">💡</div>
                    <div class="tip-content">${tip}</div>
                </div>
            `
    }
  }

  displayInsights(insights, stats, containerId) {
    const container = document.getElementById(containerId)
    if (container) {
      let content = `
                <div class="ai-insights">
                    <div class="insights-text">${insights}</div>
            `

      if (stats) {
        content += `
                    <div class="insights-stats">
                        <h4>Weekly Summary</h4>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-value">${stats.days_logged}/7</span>
                                <span class="stat-label">Days Logged</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${stats.total_meals}</span>
                                <span class="stat-label">Total Meals</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${stats.avg_calories}</span>
                                <span class="stat-label">Avg Calories</span>
                            </div>
                        </div>
                    </div>
                `
      }

      content += "</div>"
      container.innerHTML = content
    }
  }

  displayCoaching(coaching, goals, containerId) {
    const container = document.getElementById(containerId)
    if (container) {
      let content = `
                <div class="ai-coaching">
                    <div class="coaching-text">${coaching}</div>
            `

      if (goals && goals.length > 0) {
        content += `
                    <div class="coaching-goals">
                        <h4>Your Goals</h4>
                        <ul class="goals-list">
                            ${goals
                              .map(
                                (goal) => `
                                <li class="goal-item">
                                    <span class="goal-icon">🎯</span>
                                    <span class="goal-text">${goal.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}</span>
                                </li>
                            `,
                              )
                              .join("")}
                        </ul>
                    </div>
                `
      }

      content += "</div>"
      container.innerHTML = content
    }
  }

  showLoadingState(containerId) {
    const container = document.getElementById(containerId)
    if (container) {
      container.innerHTML = `
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Getting personalized insights...</div>
                </div>
            `
    }
  }

  showErrorState(containerId, message = "Unable to load AI insights at this time.") {
    const container = document.getElementById(containerId)
    if (container) {
      container.innerHTML = `
                <div class="error-state">
                    <div class="error-icon">⚠️</div>
                    <div class="error-text">${message}</div>
                    <button onclick="location.reload()" class="btn btn-secondary btn-sm">Try Again</button>
                </div>
            `
    }
  }
}

// Global AI Coach instance
window.aiCoach = new AICoach()

// Helper functions for global use
async function loadDailyTip(containerId = "daily-tip-container") {
  window.aiCoach.showLoadingState(containerId)

  const result = await window.aiCoach.getDailyTip()

  if (result.success) {
    window.aiCoach.displayTip(result.tip, containerId)
  } else {
    window.aiCoach.showErrorState(containerId, result.error)
  }
}

async function loadWeeklyInsights(containerId = "weekly-insights-container") {
  window.aiCoach.showLoadingState(containerId)

  const result = await window.aiCoach.getWeeklyInsights()

  if (result.success) {
    window.aiCoach.displayInsights(result.insights, result.stats, containerId)
  } else {
    window.aiCoach.showErrorState(containerId, result.error)
  }
}

async function loadGoalCoaching(containerId = "goal-coaching-container") {
  window.aiCoach.showLoadingState(containerId)

  const result = await window.aiCoach.getGoalCoaching()

  if (result.success) {
    window.aiCoach.displayCoaching(result.coaching, result.goals, containerId)
  } else {
    window.aiCoach.showErrorState(containerId, result.error)
  }
}

async function getMealFeedback(mealId, containerId = "meal-feedback-container") {
  window.aiCoach.showLoadingState(containerId)

  const result = await window.aiCoach.getMealFeedback(mealId)

  if (result.success) {
    const container = document.getElementById(containerId)
    if (container) {
      container.innerHTML = `
                <div class="meal-feedback">
                    <div class="feedback-icon">🤖</div>
                    <div class="feedback-text">${result.analysis}</div>
                </div>
            `
    }
  } else {
    window.aiCoach.showErrorState(containerId, result.error)
  }
}
