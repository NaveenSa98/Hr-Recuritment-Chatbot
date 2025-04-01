document.addEventListener("DOMContentLoaded", () => {
  const chatbotToggle = document.getElementById("chatbot-toggle")
  const chatbotContainer = document.getElementById("chatbot-container")
  const chatbotClose = document.getElementById("chatbot-close")
  const chatbotInput = document.getElementById("chatbot-input")
  const chatbotSend = document.getElementById("chatbot-send")
  const chatbotMessages = document.getElementById("chatbot-messages")

  // Toggle chatbot visibility
  chatbotToggle.addEventListener("click", () => {
    chatbotContainer.classList.toggle("open")
  })

  // Close chatbot
  chatbotClose.addEventListener("click", () => {
    chatbotContainer.classList.remove("open")
  })

  // Send message function
  async function sendMessage() {
    const messageText = chatbotInput.value.trim()
    if (messageText === "") return

    // Add user message to chat
    addMessage(messageText, "user")
    chatbotInput.value = ""

    // Show typing indicator
    const typingIndicator = document.createElement("div")
    typingIndicator.classList.add("message", "bot-message")
    typingIndicator.textContent = "..."
    typingIndicator.id = "typing-indicator"
    chatbotMessages.appendChild(typingIndicator)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight

    try {
      const response = await fetch("/webhook", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: messageText }),
      })

      if (!response.ok) throw new Error("Network response was not ok")

      const data = await response.json()
      console.log("Received data from server:", data) // Debug

      // Remove typing indicator
      document.getElementById("typing-indicator")?.remove()

      // Process all responses
      if (data.responses && Array.isArray(data.responses)) {
        data.responses.forEach((response) => {
          if (response.type === "text") {
            // Preserve newlines by converting them to <br>
            const formattedText = response.content.replace(/\n/g, "<br>")
            addMessage(formattedText, "bot", true)
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
      document.getElementById("typing-indicator")?.remove()
      addMessage("Sorry, I'm having trouble connecting. Please try again.", "bot")
    }
  }

  // Handle custom payloads from Rasa
  function handleCustomPayload(payload) {
    console.log("Received custom payload:", payload)
    if (payload && payload.payload === "application_form") {
      addApplicationForm(payload)
    } else {
      console.warn("Unknown custom payload type:", payload)
    }
    // Add more custom payload handlers as needed
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
    formData.elements.forEach((element) => {
      const formGroup = document.createElement("div")
      formGroup.classList.add("form-group")

      if (element.type === "text" || element.type === "email" || element.type === "tel") {
        const label = document.createElement("label")
        label.textContent = element.label
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
        label.textContent = element.label
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
      } else if (element.type === "action") {
        const button = document.createElement("button")
        button.type = "button"
        button.textContent = element.element.label
        button.classList.add("submit-button")
        button.dataset.action = element.element.action

        button.addEventListener("click", () => {
          submitApplicationForm(form, element.element.action)
        })

        formGroup.appendChild(button)
      }

      form.appendChild(formGroup)
    })

    formContainer.appendChild(form)

    // Add form to chat
    chatbotMessages.appendChild(formContainer)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }

  // Submit application form
  async function submitApplicationForm(form, action) {
    // Create FormData object
    const formData = new FormData(form)

    // Debug output what data is being submitted
    console.log("Submitting form with action:", action)
    for (let [key, value] of formData.entries()) {
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

      // Remove form from chat
      form.parentElement.remove()

      // Add processing message
      addMessage("Processing your application...", "bot")

      // Send action to Rasa to continue conversation
      await sendMessageToRasa(action)

      // Display application ID
      if (data.application_id) {
        addMessage(
          `Your application has been submitted successfully! Your application ID is: <strong>${data.application_id}</strong>. Please save this ID for future reference.`,
          "bot",
          true,
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

  // Send message to Rasa
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

      // Process all responses
      if (data.responses && Array.isArray(data.responses)) {
        data.responses.forEach((response) => {
          if (response.type === "text") {
            const formattedText = response.content.replace(/\n/g, "<br>")
            addMessage(formattedText, "bot", true)
          } else if (response.type === "buttons") {
            addButtons(response.content)
          } else if (response.type === "custom") {
            handleCustomPayload(response.content)
          }
        })
      }
    } catch (error) {
      console.error("Error:", error)
      addMessage("Sorry, I'm having trouble connecting. Please try again.", "bot")
    }
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
      btn.textContent = button.title
      btn.onclick = () => {
        addMessage(button.title, "user")
        sendMessageToRasa(button.payload)
      }
      buttonContainer.appendChild(btn)
    })

    chatbotMessages.appendChild(buttonContainer)
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight
  }

  // Event listeners for sending messages
  chatbotSend.addEventListener("click", sendMessage)
  chatbotInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  })

  // Add an initial greeting message from the bot
  const initialMessage = "Hi there! I'm the Faith HR Assistant. How can I help you with your job application today?"
  addMessage(initialMessage, "bot")
})