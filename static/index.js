document.addEventListener("DOMContentLoaded", () => {
  let audioContext = null;
  let source = null;
  let processor = null;
  let isRecording = false;
  let socket = null;
  let heartbeatInterval = null;

  let audioQueue = [];
  let isPlaying = false;
  let currentAiMessageContentElement = null;
  let audioChunkIndex = 0;

  // NEW: Keep a reference to the current audio source to stop it gracefully
  let currentAudioSource = null;

  // NEW: Store API keys
  let apiKeys = {
    gemini: "",
    assemblyai: "",
    murf: "",
    tavily: "",
  };

  const recordBtn = document.getElementById("recordBtn");
  const statusDisplay = document.getElementById("statusDisplay");
  const chatDisplay = document.getElementById("chatDisplay");
  const chatContainer = document.getElementById("chatContainer");
  const clearBtnContainer = document.getElementById("clearBtnContainer");
  const clearBtn = document.getElementById("clearBtn");

  // NEW: Config elements
  const configBtn = document.getElementById("configBtn");
  const configModal = document.getElementById("configModal");
  const configOverlay = document.getElementById("configOverlay");
  const configSaveBtn = document.getElementById("configSaveBtn");
  const configCloseBtn = document.getElementById("configCloseBtn");

  // Enhanced status management
  const updateStatus = (status, message) => {
    statusDisplay.className = `status-indicator status-${status}`;
    statusDisplay.innerHTML = `
            <div class="w-2 h-2 bg-current rounded-full"></div>
            <span>${message}</span>
        `;
  };

  // NEW: API Configuration Management
  const openConfigModal = () => {
    // Load current values
    document.getElementById("geminiKey").value = apiKeys.gemini || "";
    document.getElementById("assemblyaiKey").value = apiKeys.assemblyai || "";
    document.getElementById("murfKey").value = apiKeys.murf || "";
    document.getElementById("tavilyKey").value = apiKeys.tavily || "";

    configModal.classList.remove("hidden");
    configModal.classList.add("flex");
    setTimeout(() => {
      configModal.classList.remove("opacity-0");
      configModal.querySelector(".transform").classList.remove("scale-95");
      configModal.querySelector(".transform").classList.add("scale-100");
    }, 10);
  };

  const closeConfigModal = () => {
    configModal.classList.add("opacity-0");
    configModal.querySelector(".transform").classList.remove("scale-100");
    configModal.querySelector(".transform").classList.add("scale-95");
    setTimeout(() => {
      configModal.classList.add("hidden");
      configModal.classList.remove("flex");
    }, 200);
  };

  const saveApiKeys = () => {
    const newKeys = {
      gemini: document.getElementById("geminiKey").value.trim(),
      assemblyai: document.getElementById("assemblyaiKey").value.trim(),
      murf: document.getElementById("murfKey").value.trim(),
      tavily: document.getElementById("tavilyKey").value.trim(),
    };

    // Update local storage
    Object.keys(newKeys).forEach((key) => {
      if (newKeys[key]) {
        localStorage.setItem(`api_key_${key}`, newKeys[key]);
        apiKeys[key] = newKeys[key];
      } else {
        localStorage.removeItem(`api_key_${key}`);
        apiKeys[key] = "";
      }
    });

    // Send to server if connected
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          type: "update_api_keys",
          keys: newKeys,
        })
      );
    }

    updateConfigStatus();
    closeConfigModal();

    // Show success notification
    showNotification(
      "Settings Saved",
      "API keys have been updated successfully",
      "success"
    );
  };

  const loadApiKeys = () => {
    // Load from localStorage
    Object.keys(apiKeys).forEach((key) => {
      const stored = localStorage.getItem(`api_key_${key}`);
      if (stored) {
        apiKeys[key] = stored;
      }
    });
    updateConfigStatus();
  };

  const updateConfigStatus = () => {
    const indicators = {
      gemini: document.getElementById("geminiStatus"),
      assemblyai: document.getElementById("assemblyaiStatus"),
      murf: document.getElementById("murStatus"),
      tavily: document.getElementById("tavilyStatus"),
    };

    Object.keys(indicators).forEach((key) => {
      if (indicators[key]) {
        const hasKey = !!apiKeys[key];
        indicators[key].className = `w-2 h-2 rounded-full ${
          hasKey ? "bg-green-400" : "bg-red-400"
        }`;
        indicators[key].title = hasKey
          ? `${key} configured`
          : `${key} not configured`;
      }
    });

    // Update config button state
    const configuredCount = Object.values(apiKeys).filter(
      (key) => !!key
    ).length;
    const configIcon = configBtn.querySelector("svg");
    if (configuredCount === 4) {
      configIcon.className = configIcon.className.replace(
        "text-gray-400",
        "text-green-400"
      );
    } else if (configuredCount > 0) {
      configIcon.className = configIcon.className.replace(
        "text-gray-400",
        "text-yellow-400"
      );
    } else {
      configIcon.className = configIcon.className.replace(
        /text-(green|yellow)-400/,
        "text-gray-400"
      );
    }
  };

  // NEW: Function to handle opening websites with multiple fallback methods
  const openWebsite = (url, websiteName) => {
    console.log(
      `🌐 Brevix: Attempting to open ${websiteName || "website"} at ${url}`
    );

    // Method 1: Try window.open() immediately
    let newWindow = null;
    try {
      newWindow = window.open(url, "_blank", "noopener,noreferrer");
      console.log("Window.open() result:", newWindow);
    } catch (error) {
      console.error("window.open() failed:", error);
    }

    // Check if popup was successful
    if (
      !newWindow ||
      newWindow.closed ||
      typeof newWindow.closed === "undefined"
    ) {
      console.warn("🚫 Popup blocked or failed, trying alternative methods...");

      // Method 2: Create a temporary clickable link and auto-click it
      try {
        const tempLink = document.createElement("a");
        tempLink.href = url;
        tempLink.target = "_blank";
        tempLink.rel = "noopener noreferrer";
        tempLink.style.display = "none";
        document.body.appendChild(tempLink);

        // Simulate click
        tempLink.click();
        document.body.removeChild(tempLink);
        console.log("✅ Alternative method: Auto-clicked temporary link");

        // Success notification
        showNotification("Website Opened", websiteName || "Website", "success");
        return;
      } catch (linkError) {
        console.error("Temporary link method failed:", linkError);

        // Method 3: Show interactive notification with manual click
        showInteractiveNotification(url, websiteName);
        return;
      }
    } else {
      console.log("✅ Website opened successfully via window.open()");
      // Success notification for normal popup
      showNotification("Website Opened", websiteName || "Website", "success");
    }
  };

  // Helper function for notifications
  const showNotification = (title, subtitle, type = "success") => {
    const colors = {
      success: "from-blue-500 to-cyan-500",
      warning: "from-yellow-500 to-orange-500",
      error: "from-red-500 to-pink-500",
    };

    const icons = {
      success:
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>',
      warning:
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>',
      error:
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>',
    };

    const notification = document.createElement("div");
    notification.className = `fixed top-4 right-4 bg-gradient-to-r ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full`;
    notification.innerHTML = `
      <div class="flex items-center gap-3">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          ${icons[type]}
        </svg>
        <div>
          <div class="font-medium">${title}</div>
          <div class="text-sm opacity-90">${subtitle}</div>
        </div>
      </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.classList.remove("translate-x-full");
      notification.classList.add("translate-x-0");
    }, 100);

    // Remove notification
    const duration = type === "warning" ? 5000 : 3000;
    setTimeout(() => {
      notification.classList.add("translate-x-full");
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, duration);
  };

  // Interactive notification for blocked popups
  const showInteractiveNotification = (url, websiteName) => {
    const notification = document.createElement("div");
    notification.className =
      "fixed top-4 right-4 bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full cursor-pointer hover:shadow-xl";
    notification.innerHTML = `
      <div class="flex items-center gap-3">
        <svg class="w-5 h-5 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
        <div>
          <div class="font-medium">Popup Blocked!</div>
          <div class="text-sm opacity-90">Click here to open ${
            websiteName || "website"
          }</div>
          <div class="text-xs opacity-75 mt-1">Or allow popups for this site</div>
        </div>
      </div>
    `;

    // Make it clickable
    notification.onclick = () => {
      window.open(url, "_blank", "noopener,noreferrer");
      document.body.removeChild(notification);
    };

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.classList.remove("translate-x-full");
      notification.classList.add("translate-x-0");
    }, 100);

    // Auto-remove after 8 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.classList.add("translate-x-full");
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification);
          }
        }, 300);
      }
    }, 8000);
  };

  // MODIFIED: This function now stops the specific sound source instead of destroying the context.
  const stopCurrentPlayback = () => {
    console.log(
      "🤫 Brevix: Oops, you interrupted me! Stopping my current response."
    );
    if (currentAudioSource) {
      currentAudioSource.stop();
      currentAudioSource = null;
    }
    audioQueue = [];
    isPlaying = false;
  };

  const playNextChunk = () => {
    if (
      !audioQueue.length ||
      !audioContext ||
      audioContext.state === "closed"
    ) {
      if (isPlaying) {
        console.log(
          "✅ Brevix: That's everything from me for now! All audio chunks have been played."
        );
      }
      isPlaying = false;
      currentAudioSource = null;
      return;
    }

    console.log(
      `➡️ Brevix: Playing audio chunk. ${
        audioQueue.length - 1
      } remaining in the queue.`
    );
    isPlaying = true;
    const chunk = audioQueue.shift();

    audioContext.decodeAudioData(
      chunk,
      (buffer) => {
        const sourceNode = audioContext.createBufferSource();
        sourceNode.buffer = buffer;
        sourceNode.connect(audioContext.destination);
        sourceNode.start();

        // MODIFIED: Store reference to the new source and clear it onended
        currentAudioSource = sourceNode;
        sourceNode.onended = () => {
          currentAudioSource = null;
          playNextChunk();
        };
      },
      (error) => {
        console.error("Error decoding audio data:", error);
        playNextChunk();
      }
    );
  };

  const startRecording = async () => {
    console.log("🎤 Brevix: Let's talk! Initializing the audio session.");

    // Check if required API keys are available
    if (!apiKeys.assemblyai) {
      showNotification(
        "Missing API Key",
        "AssemblyAI API key is required for transcription",
        "error"
      );
      openConfigModal();
      return;
    }

    if (!apiKeys.gemini) {
      showNotification(
        "Missing API Key",
        "Gemini API key is required for AI responses",
        "error"
      );
      openConfigModal();
      return;
    }

    if (!apiKeys.murf) {
      showNotification(
        "Missing API Key",
        "Murf API key is required for text-to-speech",
        "error"
      );
      openConfigModal();
      return;
    }

    // MODIFIED: Initialize AudioContext only once.
    if (!audioContext) {
      try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      } catch (e) {
        alert("Web Audio API is not supported in this browser.");
        console.error("Error creating AudioContext", e);
        return;
      }
    }

    if (audioContext.state === "suspended") {
      await audioContext.resume();
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      alert("Audio recording is not supported in this browser.");
      return;
    }

    isRecording = true;
    updateUIForRecording(true);

    try {
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

      socket.onopen = async () => {
        console.log(
          "🔌 Brevix: WebSocket connection established. I'm all ears!"
        );
        updateStatus("connecting", "Establishing Connection...");

        // Send API keys to server
        socket.send(
          JSON.stringify({
            type: "update_api_keys",
            keys: apiKeys,
          })
        );

        heartbeatInterval = setInterval(() => {
          if (socket?.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "ping" }));
          }
        }, 25000);

        // Send start transcription signal
        socket.send(JSON.stringify({ type: "start_transcription" }));

        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            audio: true,
          });
          source = audioContext.createMediaStreamSource(stream);
          processor = audioContext.createScriptProcessor(4096, 1, 1);

          processor.onaudioprocess = (event) => {
            const inputData = event.inputBuffer.getChannelData(0);
            const targetSampleRate = 16000;
            const sourceSampleRate = audioContext.sampleRate;
            const ratio = sourceSampleRate / targetSampleRate;
            const newLength = Math.floor(inputData.length / ratio);
            const downsampledData = new Float32Array(newLength);
            for (let i = 0; i < newLength; i++) {
              downsampledData[i] = inputData[Math.floor(i * ratio)];
            }
            const pcmData = new Int16Array(downsampledData.length);
            for (let i = 0; i < pcmData.length; i++) {
              const sample = Math.max(-1, Math.min(1, downsampledData[i]));
              pcmData[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
            }
            if (socket?.readyState === WebSocket.OPEN) {
              socket.send(pcmData.buffer);
            }
          };

          source.connect(processor);
          processor.connect(audioContext.destination);
          recordBtn.mediaStream = stream;

          updateStatus("listening", "Listening...");
        } catch (micError) {
          alert(
            "Could not access the microphone. Please check your browser permissions."
          );
          console.error(
            "Microphone access error:",
            micError.name,
            micError.message
          );
          await stopRecording();
        }
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type !== "audio" && data.type !== "pong") {
            console.log(
              `📬 Brevix: Message from server -> Type: ${data.type}`,
              data
            );
          }

          switch (data.type) {
            case "pong":
              break;
            case "status":
              updateStatus("connecting", data.message);
              break;
            case "api_keys_status":
              // Handle default keys status from server
              if (data.default_keys) {
                console.log("Server default keys status:", data.default_keys);
              }
              break;
            case "api_keys_updated":
              console.log("API keys updated on server");
              break;
            case "transcription":
              if (data.end_of_turn && data.text) {
                addToChatLog(data.text, "user");
                updateStatus("thinking", "Processing...");
                currentAiMessageContentElement = null;
              }
              break;
            case "llm_chunk":
              if (data.data) {
                if (!currentAiMessageContentElement) {
                  currentAiMessageContentElement = addToChatLog("", "ai");
                }
                currentAiMessageContentElement.textContent += data.data;
                chatContainer.scrollTop = chatContainer.scrollHeight;
              }
              break;
            case "open_url":
              // Handle website opening
              console.log("🌐 Brevix: Received open_url command:", data);
              if (data.url) {
                openWebsite(data.url, data.website_name);
              } else {
                console.error("❌ No URL provided in open_url command");
              }
              break;
            case "audio_start":
              updateStatus("speaking", "Generating Response...");
              console.log(
                "🎶 Brevix: Okay, I've started receiving the audio stream. Getting ready to speak!"
              );

              if (audioContext.state === "suspended") {
                audioContext.resume();
              }

              audioQueue = [];
              audioChunkIndex = 0;
              break;
            case "audio_interrupt":
              stopCurrentPlayback();
              updateStatus("listening", "Listening...");
              break;
            case "audio": {
              if (data.data) {
                const audioData = atob(data.data);
                const byteNumbers = new Array(audioData.length);
                for (let i = 0; i < audioData.length; i++) {
                  byteNumbers[i] = audioData.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);

                console.log(
                  `🎵 Brevix: Processing audio chunk ${
                    audioChunkIndex + 1
                  }. Size: ${
                    byteArray.buffer.byteLength
                  } bytes. Queueing it up!`
                );
                audioChunkIndex++;

                audioQueue.push(byteArray.buffer);

                if (!isPlaying) {
                  console.log(
                    `▶️ Brevix: Let's play the first chunk! I have ${audioQueue.length} pieces of my response ready.`
                  );
                  playNextChunk();
                }
              }
              break;
            }
            case "audio_end":
              updateStatus("listening", "Listening...");
              console.log(
                "🏁 Brevix: The server has confirmed the audio stream is complete."
              );
              break;
            case "error":
              updateStatus("error", `Error: ${data.message}`);
              showNotification("Error", data.message, "error");
              break;
          }
        } catch (err) {
          console.error("Error parsing message:", err);
        }
      };

      socket.onclose = () => {
        updateStatus("ready", "Connection Closed");
        console.log(
          "💔 Brevix: Connection closed. Hope we can talk again soon!"
        );
        stopRecording(false);
      };
      socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        updateStatus("error", "Connection Error");
        stopRecording();
      };
    } catch (err) {
      alert("Failed to start the recording session.");
      console.error("Session start error:", err);
      await stopRecording();
    }
  };

  // MODIFIED: This function now only disconnects nodes, it does not destroy the AudioContext.
  const stopRecording = async (sendEOF = true) => {
    if (!isRecording) return;
    console.log(
      "🛑 Brevix: Recording stopped. Closing the connection now. Talk to you later!"
    );
    isRecording = false;

    stopCurrentPlayback();

    if (heartbeatInterval) {
      clearInterval(heartbeatInterval);
      heartbeatInterval = null;
    }

    if (processor) processor.disconnect();
    if (source) source.disconnect();
    if (recordBtn.mediaStream) {
      recordBtn.mediaStream.getTracks().forEach((track) => track.stop());
      recordBtn.mediaStream = null;
    }

    // This line is intentionally removed to preserve the AudioContext
    // if (audioContext) { audioContext.close(); audioContext = null; }

    if (socket?.readyState === WebSocket.OPEN) {
      socket.close();
    }
    socket = null;
    updateUIForRecording(false);
  };

  const updateUIForRecording = (isRec) => {
    if (isRec) {
      recordBtn.classList.add("recording");
      chatDisplay.classList.remove("hidden");
    } else {
      recordBtn.classList.remove("recording");
      updateStatus("ready", "Ready to Connect");
    }
  };

  const addToChatLog = (text, sender) => {
    const messageElement = document.createElement("div");
    messageElement.className = `chat-message ${
      sender === "user" ? "user-message" : "ai-message"
    }`;

    const prefixDiv = document.createElement("div");
    prefixDiv.className = `message-prefix ${
      sender === "user" ? "user-prefix" : "ai-prefix"
    }`;
    prefixDiv.textContent = sender === "user" ? "YOU" : "BREVIX";

    const contentSpan = document.createElement("div");
    contentSpan.className = "message-content";
    contentSpan.textContent = text;

    messageElement.appendChild(prefixDiv);
    messageElement.appendChild(contentSpan);
    chatContainer.appendChild(messageElement);

    // Show clear button when there are messages
    if (chatContainer.children.length > 0) {
      clearBtn.style.display = "inline-flex";
    }

    chatContainer.scrollTop = chatContainer.scrollHeight;

    return contentSpan;
  };

  // Event Listeners
  clearBtn.addEventListener("click", () => {
    chatContainer.innerHTML = "";
    clearBtn.style.display = "none";
  });

  recordBtn.addEventListener("click", () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  });

  // NEW: Config modal event listeners
  configBtn.addEventListener("click", openConfigModal);
  configCloseBtn.addEventListener("click", closeConfigModal);
  configSaveBtn.addEventListener("click", saveApiKeys);
  configOverlay.addEventListener("click", closeConfigModal);

  // Prevent modal from closing when clicking inside it
  configModal.querySelector(".bg-white").addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // Handle Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !configModal.classList.contains("hidden")) {
      closeConfigModal();
    }
  });

  window.addEventListener("beforeunload", () => {
    if (isRecording) stopRecording();
  });

  // Initialize
  loadApiKeys();
  clearBtn.style.display = "none";
});
