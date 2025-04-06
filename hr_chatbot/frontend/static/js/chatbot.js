document.addEventListener("DOMContentLoaded", () => {
  const chatbotToggle = document.getElementById("chatbot-toggle")
  const chatbotContainer = document.getElementById("chatbot-container")
  const chatbotClose = document.getElementById("chatbot-close")
  const chatbotInput = document.getElementById("chatbot-input")
  const chatbotSend = document.getElementById("chatbot-send")
  const chatbotMessages = document.getElementById("chatbot-messages")


  // Toggle chatbot visibility
  chatbotToggle.addEventListener("click", () => {
    if (!chatbotContainer.classList.contains("open")) {

      resetChatbot()
      chatbotContainer.classList.add("open")

      showInitialGreeting()
    } else {
    
      chatbotContainer.classList.remove("open")

      resetChatbot()
    }
  })

  // Close chatbot
  chatbotClose.addEventListener("click", () => {
    chatbotContainer.classList.remove("open")
    resetChatbot()
  })

  function resetChatbot() {

    chatbotMessages.innerHTML = ""

    chatbotInput.value = ""
  }

  function showInitialGreeting() {
    // Add bot welcome message
    const welcomeMessage = `Hi there! I'm the HR Assistant. How can I help you today?`
    addMessage(welcomeMessage, "bot")
    // Create options container
    const optionsContainer = document.createElement("div")
    optionsContainer.classList.add("initial-options")
    // Define the main options
    const options = [
      {
        text: "Show job vacancies",
        icon: "fas fa-list-ul",
        action: "show_vacancies",
      },
      {
        text: "Check application status",
        icon: "fas fa-search",
        action: "check_status",
      },
      {
        text: "About company",
        icon: "fas fa-suitcase",
        action: "about_company",
      },
      {
        text: "Employee benefits",
        icon: "fas fa-gift",
        action: "employee_benefits",
      },
      {
        text: "Schedule interview date",
        icon: "fas fa-calendar-alt",
        action: "schedule_interview",
      },
    ]
    options.forEach((option) => {
      const button = document.createElement("button")
      button.classList.add("option-button")
      button.innerHTML = `<i class="${option.icon}"></i> ${option.text}`
      button.addEventListener("click", () => {
        // Add user message to show what was selected
        addMessage(option.text, "user")
        // Handle different options
        handleOptionSelection(option.action)
      })
      optionsContainer.appendChild(button)
    })
    // Add options to chat
    chatbotMessages.appendChild(optionsContainer)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }
  async function handleOptionSelection(action) {
    // Show typing indicator
    showTypingIndicator()
    try {
      // Route to correct action
      switch (action) {
        case "show_vacancies":
          await sendMessageToRasa("/ask_job_openings")
          break
        case "check_status":
          await sendMessageToRasa("/ask_application_status")
          break
        case "about_company":
          await sendMessageToRasa("/ask_company_culture")
          break
        case "employee_benefits":
          await sendMessageToRasa("/ask_benefits")
          break
        case "schedule_interview":
          await sendMessageToRasa("/ask_interview_scheduling")
          break
        default:
          // Check if it's a direct payload
          if (action.startsWith("/")) {
            await sendMessageToRasa(action)
          } else {
            removeTypingIndicator()
            addMessage("Sorry, I'm not sure how to help with that yet.", "bot")
          }
      }
    } catch (error) {
      console.error("Error handling option:", error)
      removeTypingIndicator()
      addMessage("Sorry, I encountered an error. Please try again.", "bot")
    }
  }
  function showTypingIndicator() {
    const typingIndicator = document.createElement("div")
    typingIndicator.classList.add("typing-indicator")
    typingIndicator.id = "typing-indicator"
    chatbotMessages.appendChild(typingIndicator)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }
  function removeTypingIndicator() {
    document.getElementById("typing-indicator")?.remove()
  }
  async function sendMessage() {
    const messageText = chatbotInput.value.trim()
    if (messageText === "") return
    // Add user message to chat
    addMessage(messageText, "user")
    chatbotInput.value = ""
    // Show typing indicator
    showTypingIndicator()
    try {
      await sendMessageToRasa(messageText)
    } catch (error) {
      console.error("Error:", error)
      removeTypingIndicator()
      addMessage("Sorry, I'm having trouble connecting. Please try again.", "bot")
    }
  }
  async function sendMessageToRasa(message) {
    try {
      const response = await fetch("/webhook", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      })
      if (!response.ok) throw new Error("Network response was not ok")
      const data = await response.json()
      console.log("Received data from server:", data)
      // Remove typing indicator
      removeTypingIndicator()
      // Process all responses
      if (data.responses && Array.isArray(data.responses)) {
        data.responses.forEach((response) => {
          if (response.type === "text") {
            // Check if this is a job listing response
            if (response.content.includes("Current Job Openings:")) {
              addJobListings(response.content)
            } else {
              // Preserve newlines by converting them to <br>
              const formattedText = response.content.replace(/\n/g, "<br>")
              addMessage(formattedText, "bot", true)
            }
          } else if (response.type === "buttons") {
            addButtons(response.content)
          } else if (response.type === "custom") {
            // Handle custom payloads
            handleCustomPayload(response.content)
          }
        })
      } else {
        // Handle unexpected response format
        console.error("Unexpected response format:", data)
        addMessage("Sorry, I received an unexpected response format. Please try again.", "bot")
      }
    } catch (error) {
      console.error("Error:", error)
      removeTypingIndicator()
      throw error
    }
  }

  // New function to parse and display job listings as clickable items
  function addJobListings(content) {
    // Create a container for the job listings
    const jobListingsContainer = document.createElement("div")
    jobListingsContainer.classList.add("job-listings-container")

    // Add the header
    const header = document.createElement("div")
    header.classList.add("job-listings-header")
    header.innerHTML = "Current Job Openings:"
    jobListingsContainer.appendChild(header)

    // Parse the job titles from the content
    const lines = content.split("\n")
    const jobTitles = lines
      .filter((line) => line.trim().startsWith("*") || line.trim().startsWith("-"))
      .map((line) =>
        line
          .trim()
          .replace(/^[*-]\s*/, "")
          .trim(),
      )

    // Create a job list
    const jobList = document.createElement("div")
    jobList.classList.add("job-list")

    // Add each job as a clickable item
    jobTitles.forEach((jobTitle) => {
      const jobItem = document.createElement("div")
      jobItem.classList.add("job-item")

      const jobButton = document.createElement("button")
      jobButton.classList.add("job-button")
      jobButton.innerHTML = `
        <span class="job-title">${jobTitle}</span>
        <i class="fas fa-chevron-right job-arrow"></i>
      `

      // Create a container for job details (initially hidden)
      const jobDetailsContainer = document.createElement("div")
      jobDetailsContainer.classList.add("job-details-container")
      jobDetailsContainer.style.display = "none"

      // Add loading indicator for job details
      const loadingIndicator = document.createElement("div")
      loadingIndicator.classList.add("job-details-loading")
      loadingIndicator.innerHTML = "Loading job details..."
      jobDetailsContainer.appendChild(loadingIndicator)

      // Add click event to toggle job details
      jobButton.addEventListener("click", async () => {
        // Toggle the arrow direction
        const arrow = jobButton.querySelector(".job-arrow")
        arrow.classList.toggle("rotated")

        // Toggle the details container
        if (jobDetailsContainer.style.display === "none") {
          jobDetailsContainer.style.display = "block"

          // Fetch job details if not already loaded
          if (jobDetailsContainer.querySelector(".job-details-loading")) {
            try {
              // Send a message to get job requirements
              const jobRequirementMessage = `What are the requirements for ${jobTitle}?`

              // Add a temporary user message (will be hidden)
              const tempMessageId = `temp-${Date.now()}`
              const tempMessage = document.createElement("div")
              tempMessage.id = tempMessageId
              tempMessage.style.display = "none"
              chatbotMessages.appendChild(tempMessage)

              // Send the request to get job details
              const response = await fetch("/webhook", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: jobRequirementMessage }),
              })

              if (!response.ok) throw new Error("Failed to fetch job details")

              const data = await response.json()

              // Process the response to extract job details
              let jobDetailsHTML = ""
              if (data.responses && Array.isArray(data.responses)) {
                data.responses.forEach((response) => {
                  if (response.type === "text") {
                    jobDetailsHTML = response.content.replace(/\n/g, "<br>")
                  }
                })
              }

              // Remove the loading indicator
              jobDetailsContainer.innerHTML = ""

              // Create the job details card
              const jobDetailsCard = document.createElement("div")
              jobDetailsCard.classList.add("job-details-card")
              jobDetailsCard.innerHTML = jobDetailsHTML

              // Add an apply button
              const applyButton = document.createElement("button")
              applyButton.classList.add("job-apply-button")
              applyButton.innerHTML = "Apply for this position"
              applyButton.addEventListener("click", () => {
                // Add user message
                addMessage(`I want to apply for the ${jobTitle} position`, "user")
                // Send message to start application
                sendMessageToRasa(`/start_application_form{"job_title":"${jobTitle}"}`)
                // Close the job details
                jobDetailsContainer.style.display = "none"
                arrow.classList.remove("rotated")
              })

              jobDetailsCard.appendChild(applyButton)
              jobDetailsContainer.appendChild(jobDetailsCard)

              // Remove the temporary message
              document.getElementById(tempMessageId)?.remove()
            } catch (error) {
              console.error("Error fetching job details:", error)
              jobDetailsContainer.innerHTML = "Sorry, I couldn't load the job details. Please try again."
            }
          }
        } else {
          jobDetailsContainer.style.display = "none"
        }
      })

      jobItem.appendChild(jobButton)
      jobItem.appendChild(jobDetailsContainer)
      jobList.appendChild(jobItem)
    })

    jobListingsContainer.appendChild(jobList)
    chatbotMessages.appendChild(jobListingsContainer)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }

  // Handle custom payloads from Rasa
  function handleCustomPayload(payload) {
    console.log("Received custom payload:", payload)

    // Check if payload exists and has the expected structure
    if (payload && payload.payload === "application_form") {
      addApplicationForm(payload)
    } else if (payload && payload.interview_details) {
      // Handle the interview details payload
      addInterviewDetails(payload.interview_details)
    } else {
      console.warn("Unknown or malformed custom payload:", payload)
      addMessage("Sorry, I couldn't process the custom response. Please try again.", "bot")
    }
  }
  // Add interview details to chat
  function addInterviewDetails(interviewData) {
    console.log("Adding interview details with data:", interviewData)

    const detailsContainer = document.createElement("div")
    detailsContainer.classList.add("interview-details-container")
    detailsContainer.id = `interview-${interviewData.interview_id}`

    // Create details card
    const detailsCard = document.createElement("div")
    detailsCard.classList.add("interview-details-card")

    // Add header
    const header = document.createElement("div")
    header.classList.add("interview-header")
    header.innerHTML = `<h4>Interview Details</h4>`

    // Add details content
    const content = document.createElement("div")
    content.classList.add("interview-content")

    // Format date and time for display
    let formattedDate = interviewData.date
    if (typeof formattedDate === "string" && !formattedDate.includes(",")) {
      try {
        const dateObj = new Date(formattedDate)
        formattedDate = dateObj.toLocaleDateString("en-US", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      } catch (e) {
        console.error("Error formatting date:", e)
      }
    }

    content.innerHTML = `
      <div class="interview-info">
        <p><i class="fas fa-calendar-day"></i> <strong>Date:</strong> ${formattedDate}</p>
        <p><i class="fas fa-clock"></i> <strong>Time:</strong> ${interviewData.time}</p>
        <p><i class="fas fa-video"></i> <strong>Type:</strong> ${interviewData.type}</p>
        <p><i class="fas fa-user-tie"></i> <strong>Interviewer:</strong> ${interviewData.interviewer || "HR Team"}</p>
        <p><i class="fas fa-briefcase"></i> <strong>Position:</strong> ${interviewData.job_title || "Applied Position"}</p>
      </div>
    `

    // Add accept button
    const acceptButton = document.createElement("button")
    acceptButton.classList.add("interview-accept-button")
    acceptButton.innerHTML = `<i class="fas fa-check-circle"></i> Accept Interview`

    acceptButton.addEventListener("click", async () => {
      // Add user message
      addMessage("I'd like to accept this interview slot", "user")

      // Show typing indicator
      showTypingIndicator()

      try {
        // Call the direct endpoint instead of using Rasa
        const response = await fetch("/confirm-interview", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            interview_id: interviewData.interview_id,
            application_id: interviewData.application_id,
            date: formattedDate,
            time: interviewData.time,
          }),
        })

        const data = await response.json()

        // Remove typing indicator
        removeTypingIndicator()

        if (!response.ok) {
          throw new Error(data.message || "Failed to confirm interview")
        }

        // Show confirmation message
        addMessage(data.message, "bot")

        // Remove the accept button after clicking
        acceptButton.remove()
      } catch (error) {
        console.error("Error confirming interview:", error)
        removeTypingIndicator()
        addMessage(error.message || "Sorry, I encountered an error confirming your interview. Please try again.", "bot")
      }
    })

    // Assemble the card
    detailsCard.appendChild(header)
    detailsCard.appendChild(content)
    detailsCard.appendChild(acceptButton)
    detailsContainer.appendChild(detailsCard)

    // Add to chat
    chatbotMessages.appendChild(detailsContainer)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }

  // Add application form to chat
  function addApplicationForm(formData) {
    console.log("Adding application form with data:", formData)
    const formContainer = document.createElement("div")
    formContainer.classList.add("application-form-container")
    // Create form title
    const formTitle = document.createElement("h3")
    formTitle.textContent = formData.title || "Application Form"
    formContainer.appendChild(formTitle)
    // Create actual form
    const form = document.createElement("form")
    form.classList.add("application-form")
    form.id = "application-form"
    // Add form elements based on the formData.elements provided by Rasa
    if (Array.isArray(formData.elements)) {
      formData.elements.forEach((element) => {
        if (!element || typeof element !== "object") {
          console.warn("Invalid form element:", element)
          return
        }
        const formGroup = document.createElement("div")
        formGroup.classList.add("form-group")
        if (element.type === "text" || element.type === "email" || element.type === "tel") {
          const label = document.createElement("label")
          label.textContent = element.label || element.name
          label.setAttribute("for", element.name)
          const input = document.createElement("input")
          input.type = element.type
          input.id = element.name
          input.name = element.name
          input.required = element.required || false
          if (element.value) {
            input.value = element.value
          }
          if (element.pattern) {
            input.pattern = element.pattern
          }
          formGroup.appendChild(label)
          formGroup.appendChild(input)
        } else if (element.type === "file") {
          const label = document.createElement("label")
          label.textContent = element.label || element.name
          label.setAttribute("for", element.name)
          const fileInput = document.createElement("input")
          fileInput.type = "file"
          fileInput.id = element.name
          fileInput.name = element.name
          fileInput.accept = element.accept || ""
          fileInput.required = element.required || false
          const helpText = document.createElement("small")
          helpText.textContent = element.help || ""
          formGroup.appendChild(label)
          formGroup.appendChild(fileInput)
          formGroup.appendChild(helpText)
        } else if (element.type === "action" && element.element) {
          const button = document.createElement("button")
          button.type = "button"
          button.textContent = element.element.label || "Submit"
          button.classList.add("submit-button")
          button.dataset.action = element.element.action || "submit_form"
          button.addEventListener("click", () => {
            submitApplicationForm(form, element.element.action)
          })
          formGroup.appendChild(button)
        }
        form.appendChild(formGroup)
      })
    } else {
      console.error("Form elements missing or not an array")
      const errorMessage = document.createElement("p")
      errorMessage.textContent = "Sorry, the form structure is invalid. Please try again."
      errorMessage.classList.add("form-error")
      form.appendChild(errorMessage)
    }
    formContainer.appendChild(form)
    // Add form to chat
    chatbotMessages.appendChild(formContainer)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }
  // Submit application form
  async function submitApplicationForm(form, action) {
    const formData = new FormData(form)
    // Debug output what data is being submitted
    console.log("Submitting form with action:", action)
    for (const [key, value] of formData.entries()) {
      console.log(`${key}: ${value instanceof File ? value.name : value}`)
    }
    // Validate form
    const isValid = validateForm(form)
    if (!isValid) {
      addMessage("Please fill out all required fields.", "bot")
      return
    }
    // Show loading state
    const submitButton = form.querySelector(".submit-button")
    const originalText = submitButton.textContent
    submitButton.textContent = "Submitting..."
    submitButton.disabled = true
    try {
      // Send form data to backend
      const response = await fetch("/submit-application", {
        method: "POST",
        body: formData,
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || "Failed to submit application")
      }
      const data = await response.json()
      console.log("Submit application response:", data)

      form.parentElement.remove()

      const applicationId = data.application_id

      showTypingIndicator()

      try {
        const processResponse = await fetch("/process-application", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            application_id: applicationId,
          }),
        })
        const processData = await processResponse.json()

        removeTypingIndicator()

        if (!processResponse.ok) {
          throw new Error(processData.message || "Failed to process application")
        }

        addMessage(processData.message, "bot")
      } catch (processError) {
        console.error("Error processing application:", processError)
        removeTypingIndicator()
        addMessage(
          processError.message || "Sorry, I encountered an error processing your application. Please try again.",
          "bot",
        )
      }
    } catch (error) {
      console.error("Error submitting form:", error)
      addMessage(`There was an error submitting your application: ${error.message}. Please try again.`, "bot")
      // Reset button
      submitButton.textContent = originalText
      submitButton.disabled = false
    }
  }
  // Validate form
  function validateForm(form) {
    const requiredFields = form.querySelectorAll("[required]")
    let isValid = true
    requiredFields.forEach((field) => {
      if (!field.value) {
        field.classList.add("invalid")
        isValid = false
      } else {
        field.classList.remove("invalid")
      }
    })
    return isValid
  }
  // Add message to chat
  function addMessage(text, sender, isHTML = false) {
    const messageElement = document.createElement("div")
    messageElement.classList.add("message", `${sender}-message`)
    if (isHTML) {
      messageElement.innerHTML = text
    } else {
      messageElement.textContent = text
    }
    chatbotMessages.appendChild(messageElement)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }
  function addButtons(buttons) {
    const buttonContainer = document.createElement("div")
    buttonContainer.classList.add("button-container")
    buttons.forEach((button) => {
      const btn = document.createElement("button")
      btn.classList.add("chat-button")
      // Add icon based on button title
      let icon = "fas fa-angle-right"
      if (button.title.toLowerCase().includes("job") || button.title.toLowerCase().includes("apply")) {
        icon = "fas fa-briefcase"
      } else if (button.title.toLowerCase().includes("status") || button.title.toLowerCase().includes("check")) {
        icon = "fas fa-search"
      } else if (button.title.toLowerCase().includes("interview") || button.title.toLowerCase().includes("book")) {
        icon = "fas fa-calendar-alt"
      } else if (button.title.toLowerCase().includes("yes") || button.title.toLowerCase().includes("confirm")) {
        icon = "fas fa-check"
      } else if (button.title.toLowerCase().includes("no") || button.title.toLowerCase().includes("cancel")) {
        icon = "fas fa-times"
      }
      btn.innerHTML = `<i class="${icon}"></i> ${button.title}`
      btn.addEventListener("click", () => {
        // Add user message to show selection
        addMessage(button.title, "user")
        // Send button payload to backend
        handleOptionSelection(button.payload)
      })
      buttonContainer.appendChild(btn)
    })
    chatbotMessages.appendChild(buttonContainer)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }
  chatbotSend.addEventListener("click", sendMessage)
  // Send message when pressing Enter in input field
  chatbotInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault()
      sendMessage()
    }
  })
  function addAnimationEffects() {
    // Add animation to chatbot toggle button
    chatbotToggle.addEventListener("mouseover", () => {
      chatbotToggle.classList.add("pulse")
    })
    chatbotToggle.addEventListener("mouseout", () => {
      chatbotToggle.classList.remove("pulse")
    })
    // Sparkle animation when loading completed
    const sparkleEffect = document.createElement("div")
    sparkleEffect.classList.add("sparkle-effect")
    document.body.appendChild(sparkleEffect)
    setTimeout(() => {
      sparkleEffect.remove()
    }, 2000)
  }
  // Initialize animations
  addAnimationEffects()
})

