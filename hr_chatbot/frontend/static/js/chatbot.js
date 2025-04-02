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

    if (chatbotContainer.classList.contains("open") && chatbotMessages.children.length === 0) {
      showInitialGreeting()
    }

  })

  // Close chatbot
  chatbotClose.addEventListener("click", () => {
    chatbotContainer.classList.remove("open")
  })

  function showInitialGreeting() {
    // Add bot welcome message
    const welcomeMessage = `Hi there! I'm the Faith HR Assistant. How can I help you today?`;
    addMessage(welcomeMessage, "bot");
    
    // Create options container
    const optionsContainer = document.createElement("div");
    optionsContainer.classList.add("initial-options");
    
    // Define the main options
    const options = [
      { 
        text: "Show job vacancies", 
        icon: "fas fa-list-ul", 
        action: "show_vacancies" 
      },
      { 
        text: "Check application status", 
        icon: "fas fa-search", 
        action: "check_status" 
      },
      { 
        text: "Apply for a job", 
        icon: "fas fa-file-alt", 
        action: "apply_job" 
      },
      { 
        text: "Schedule interview date", 
        icon: "fas fa-calendar-alt", 
        action: "schedule_interview" 
      }

    ];

    options.forEach(option => {
      const button = document.createElement("button");
      button.classList.add("option-button");
      button.innerHTML = `<i class="${option.icon}"></i> ${option.text}`;
      
      button.addEventListener("click", () => {
        // Add user message to show what was selected
        addMessage(option.text, "user");
        
        // Handle different options
        handleOptionSelection(option.action);
      });
      
      optionsContainer.appendChild(button);
    });
    
    // Add options to chat
    chatbotMessages.appendChild(optionsContainer);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

  }

  async function handleOptionSelection(action) {
    // Show typing indicator
    showTypingIndicator();
    
    try {
      // Route to correct action
      switch(action) {
        case "show_vacancies":
          await sendMessageToRasa("/ask_job_openings");
          break;
        case "check_status":
          await sendMessageToRasa("/ask_application_status");
          break;
        case "apply_job":
          await sendMessageToRasa("/ask_how_to_apply");
          break;
        case "book_interview":
          await sendMessageToRasa("/ask_interview_scheduling");
          break;
        default:
          removeTypingIndicator();
          addMessage("Sorry, I'm not sure how to help with that yet.", "bot");
      }
    } catch (error) {
      console.error("Error handling option:", error);
      removeTypingIndicator();
      addMessage("Sorry, I encountered an error. Please try again.", "bot");
    }
  }

  function showTypingIndicator() {
    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("typing-indicator");
    typingIndicator.id = "typing-indicator";
    chatbotMessages.appendChild(typingIndicator);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  function removeTypingIndicator() {
    document.getElementById("typing-indicator")?.remove();
  }


  async function sendMessage() {
    const messageText = chatbotInput.value.trim()
    if (messageText === "") return

    // Add user message to chat
    addMessage(messageText, "user")
    chatbotInput.value = ""

    // Show typing indicator
    showTypingIndicator();

    try {
      await sendMessageToRasa(messageText);
    } catch (error) {
      console.error("Error:", error)
      removeTypingIndicator();
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
      removeTypingIndicator();

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
      removeTypingIndicator();
      throw error; 
    }
  }

  // Handle custom payloads from Rasa
  function handleCustomPayload(payload) {
    console.log("Received custom payload:", payload)
    
    // Check if payload exists and has the expected structure
    if (payload && payload.payload === "application_form") {
      addApplicationForm(payload)
    } else {
      console.warn("Unknown or malformed custom payload:", payload)
      addMessage("Sorry, I couldn't process the custom response. Please try again.", "bot")
    }
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
        if (!element || typeof element !== 'object') {
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

      const applicationId = data.application_id;

      await sendMessageToRasa(`/submit_application_form{"application_id":"${applicationId}"}`);

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
      let icon = "fas fa-angle-right";
      if (button.title.toLowerCase().includes("job") || button.title.toLowerCase().includes("apply")) {
        icon = "fas fa-briefcase";
      } else if (button.title.toLowerCase().includes("status") || button.title.toLowerCase().includes("check")) {
        icon = "fas fa-search";
      } else if (button.title.toLowerCase().includes("interview") || button.title.toLowerCase().includes("book")) {
        icon = "fas fa-calendar-alt";
      } else if (button.title.toLowerCase().includes("yes") || button.title.toLowerCase().includes("confirm")) {
        icon = "fas fa-check";
      } else if (button.title.toLowerCase().includes("no") || button.title.toLowerCase().includes("cancel")) {
        icon = "fas fa-times";
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
      chatbotToggle.classList.add("pulse");
    });
    
    chatbotToggle.addEventListener("mouseout", () => {
      chatbotToggle.classList.remove("pulse");
    });
    
    // Sparkle animation when loading completed
    const sparkleEffect = document.createElement("div");
    sparkleEffect.classList.add("sparkle-effect");
    document.body.appendChild(sparkleEffect);
    
    setTimeout(() => {
      sparkleEffect.remove();
    }, 2000);
  }
  
  // Initialize animations
  addAnimationEffects();
})

 

  