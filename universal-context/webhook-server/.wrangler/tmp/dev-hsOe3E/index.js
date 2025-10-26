var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/utils/audioConverter.ts
var AudioConverter = class {
  static {
    __name(this, "AudioConverter");
  }
  /**
   * Convert raw PCM audio bytes to WAV format
   * @param rawAudio - Raw audio bytes (PCM 16-bit)
   * @param sampleRate - Sample rate in Hz (default: 16000 for Omi DevKit2)
   * @param numChannels - Number of audio channels (1 = mono, 2 = stereo)
   * @param bitsPerSample - Bits per sample (default: 16)
   * @returns WAV audio as ArrayBuffer
   */
  static rawToWAV(rawAudio, sampleRate = 16e3, numChannels = 1, bitsPerSample = 16) {
    const audioData = rawAudio instanceof ArrayBuffer ? new Uint8Array(rawAudio) : rawAudio;
    const dataSize = audioData.length;
    const byteRate = sampleRate * numChannels * bitsPerSample / 8;
    const blockAlign = numChannels * bitsPerSample / 8;
    const wavSize = 44 + dataSize;
    const wavBuffer = new ArrayBuffer(wavSize);
    const view = new DataView(wavBuffer);
    this.writeString(view, 0, "RIFF");
    view.setUint32(4, wavSize - 8, true);
    this.writeString(view, 8, "WAVE");
    this.writeString(view, 12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);
    this.writeString(view, 36, "data");
    view.setUint32(40, dataSize, true);
    const wavData = new Uint8Array(wavBuffer);
    wavData.set(audioData, 44);
    return wavBuffer;
  }
  /**
   * Convert multiple audio chunks to a single WAV file
   * @param chunks - Array of audio chunks
   * @param sampleRate - Sample rate in Hz
   * @returns Combined WAV audio as ArrayBuffer
   */
  static combineChunksToWAV(chunks, sampleRate = 16e3) {
    const totalSize = chunks.reduce((sum, chunk) => {
      const size = chunk instanceof ArrayBuffer ? chunk.byteLength : chunk.length;
      return sum + size;
    }, 0);
    const combined = new Uint8Array(totalSize);
    let offset = 0;
    for (const chunk of chunks) {
      const data = chunk instanceof ArrayBuffer ? new Uint8Array(chunk) : chunk;
      combined.set(data, offset);
      offset += data.length;
    }
    return this.rawToWAV(combined, sampleRate);
  }
  /**
   * Parse WAV header from audio data
   * @param wavData - WAV audio data
   * @returns Parsed WAV header information
   */
  static parseWAVHeader(wavData) {
    const view = new DataView(wavData);
    return {
      riff: this.readString(view, 0, 4),
      fileSize: view.getUint32(4, true) + 8,
      wave: this.readString(view, 8, 4),
      fmt: this.readString(view, 12, 4),
      fmtSize: view.getUint32(16, true),
      audioFormat: view.getUint16(20, true),
      numChannels: view.getUint16(22, true),
      sampleRate: view.getUint32(24, true),
      byteRate: view.getUint32(28, true),
      blockAlign: view.getUint16(32, true),
      bitsPerSample: view.getUint16(34, true),
      data: this.readString(view, 36, 4),
      dataSize: view.getUint32(40, true)
    };
  }
  /**
   * Validate if audio data is a valid WAV file
   * @param audioData - Audio data to validate
   * @returns True if valid WAV file
   */
  static isValidWAV(audioData) {
    if (audioData.byteLength < 44) return false;
    const view = new DataView(audioData);
    const riff = this.readString(view, 0, 4);
    const wave = this.readString(view, 8, 4);
    return riff === "RIFF" && wave === "WAVE";
  }
  /**
   * Get audio duration in seconds
   * @param audioData - WAV audio data
   * @returns Duration in seconds
   */
  static getAudioDuration(audioData) {
    if (!this.isValidWAV(audioData)) {
      throw new Error("Invalid WAV file");
    }
    const header = this.parseWAVHeader(audioData);
    return header.dataSize / header.byteRate;
  }
  /**
   * Write string to DataView
   */
  static writeString(view, offset, str) {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  }
  /**
   * Read string from DataView
   */
  static readString(view, offset, length) {
    let str = "";
    for (let i = 0; i < length; i++) {
      str += String.fromCharCode(view.getUint8(offset + i));
    }
    return str;
  }
  /**
   * Convert base64 string to ArrayBuffer
   * @param base64 - Base64 encoded string
   * @returns ArrayBuffer
   */
  static base64ToArrayBuffer(base64) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }
  /**
   * Convert ArrayBuffer to base64 string
   * @param buffer - ArrayBuffer to convert
   * @returns Base64 encoded string
   */
  static arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }
};

// src/services/groqClient.ts
var GroqClient = class {
  static {
    __name(this, "GroqClient");
  }
  apiKey;
  baseUrl = "https://api.groq.com/openai/v1";
  constructor(apiKey) {
    this.apiKey = apiKey;
  }
  /**
   * Transcribe audio using Groq Whisper-large-v3
   * @param audioData - Audio data as ArrayBuffer (WAV format recommended)
   * @param options - Transcription options
   * @returns Transcription result
   */
  async transcribe(audioData, options) {
    try {
      const formData = new FormData();
      const audioBlob = new Blob([audioData], { type: "audio/wav" });
      formData.append("file", audioBlob, "audio.wav");
      formData.append("model", "whisper-large-v3");
      if (options?.language) {
        formData.append("language", options.language);
      }
      if (options?.prompt) {
        formData.append("prompt", options.prompt);
      }
      if (options?.temperature !== void 0) {
        formData.append("temperature", options.temperature.toString());
      }
      formData.append("response_format", "verbose_json");
      const response = await fetch(`${this.baseUrl}/audio/transcriptions`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${this.apiKey}`
        },
        body: formData
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Groq API error (${response.status}): ${errorText}`
        );
      }
      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Groq transcription error:", error);
      throw new Error(
        `Failed to transcribe audio: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }
  /**
   * Transcribe audio with automatic language detection
   * @param audioData - Audio data as ArrayBuffer
   * @returns Transcription result with detected language
   */
  async transcribeWithLanguageDetection(audioData) {
    return this.transcribe(audioData, {
      timestamp_granularities: ["segment"]
    });
  }
  /**
   * Batch transcribe multiple audio chunks
   * @param audioChunks - Array of audio data chunks
   * @param options - Transcription options
   * @returns Array of transcription results
   */
  async batchTranscribe(audioChunks, options) {
    const promises = audioChunks.map(
      (chunk) => this.transcribe(chunk, options)
    );
    try {
      return await Promise.all(promises);
    } catch (error) {
      console.error("Batch transcription error:", error);
      throw error;
    }
  }
  /**
   * Transcribe with retry logic
   * @param audioData - Audio data as ArrayBuffer
   * @param maxRetries - Maximum number of retry attempts
   * @param retryDelay - Delay between retries in milliseconds
   * @returns Transcription result
   */
  async transcribeWithRetry(audioData, maxRetries = 3, retryDelay = 1e3) {
    let lastError = null;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await this.transcribe(audioData, {
          temperature: 0
        });
      } catch (error) {
        lastError = error instanceof Error ? error : new Error("Unknown error");
        console.warn(
          `Transcription attempt ${attempt + 1} failed:`,
          lastError.message
        );
        if (attempt < maxRetries - 1) {
          await new Promise(
            (resolve) => setTimeout(resolve, retryDelay * Math.pow(2, attempt))
          );
        }
      }
    }
    throw new Error(
      `Failed to transcribe after ${maxRetries} attempts: ${lastError?.message}`
    );
  }
  /**
   * Estimate audio duration from WAV data
   * @param audioData - WAV audio data
   * @returns Estimated duration in seconds
   */
  estimateAudioDuration(audioData) {
    if (audioData.byteLength < 44) return 0;
    const view = new DataView(audioData);
    const sampleRate = view.getUint32(24, true);
    const byteRate = view.getUint32(28, true);
    const dataSize = audioData.byteLength - 44;
    return byteRate > 0 ? dataSize / byteRate : 0;
  }
  /**
   * Check if audio is long enough to transcribe (minimum 0.1 seconds)
   * @param audioData - Audio data to check
   * @returns True if audio is long enough
   */
  isAudioValid(audioData) {
    const duration = this.estimateAudioDuration(audioData);
    return duration >= 0.1 && audioData.byteLength > 44;
  }
};

// src/services/supermemoryClient.ts
var SupermemoryClient = class {
  static {
    __name(this, "SupermemoryClient");
  }
  apiKey;
  baseUrl;
  sessionId = null;
  sessionInitPromise = null;
  constructor(apiKey, baseUrl = "https://api.supermemory.ai/") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
  }
  /**
   * Initialize MCP session
   * @returns Promise that resolves when session is initialized
   */
  async initializeSession() {
    if (this.sessionId) {
      return;
    }
    if (this.sessionInitPromise) {
      return this.sessionInitPromise;
    }
    this.sessionInitPromise = (async () => {
      try {
        const payload = {
          jsonrpc: "2.0",
          id: 1,
          method: "initialize",
          params: {
            protocolVersion: "2024-11-05",
            capabilities: {
              roots: { listChanged: true },
              sampling: {}
            },
            clientInfo: {
              name: "never-be-alone-webhook",
              version: "1.0.0"
            }
          }
        };
        const response = await fetch(`${this.baseUrl}mcp`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${this.apiKey}`,
            "Accept": "application/json, text/event-stream"
          },
          body: JSON.stringify(payload)
        });
        if (!response.ok) {
          throw new Error(`MCP init failed (${response.status}): ${await response.text()}`);
        }
        this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        console.log("MCP session initialized:", this.sessionId);
      } catch (error) {
        console.error("Failed to initialize MCP session:", error);
        this.sessionInitPromise = null;
        throw error;
      }
    })();
    return this.sessionInitPromise;
  }
  /**
   * Ensure session is initialized before making requests
   */
  async ensureSession() {
    if (!this.sessionId) {
      await this.initializeSession();
    }
    return this.sessionId;
  }
  /**
   * Add content to Supermemory using MCP protocol
   * @param content - Content to store
   * @returns Response with success status and ID
   */
  async addMemory(content) {
    try {
      const sessionId = await this.ensureSession();
      const payload = {
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: {
          name: "addMemory",
          arguments: {
            thingToRemember: content.text,
            ...content.metadata && Object.keys(content.metadata).length > 0 ? { metadata: JSON.stringify(content.metadata) } : {}
          }
        }
      };
      const response = await fetch(`${this.baseUrl}mcp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.apiKey}`,
          "Accept": "application/json, text/event-stream",
          "Mcp-Session-Id": sessionId
        },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Supermemory API error (${response.status}): ${errorText}`
        );
      }
      const result = await response.json();
      if (result.error) {
        throw new Error(`MCP error: ${result.error.message || JSON.stringify(result.error)}`);
      }
      return {
        success: true,
        id: result.result?.id || result.id || `memory_${Date.now()}`
      };
    } catch (error) {
      console.error("Supermemory add error:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }
  /**
   * Search Supermemory for relevant content using MCP protocol
   * @param query - Search query
   * @param options - Search options
   * @returns Search results
   */
  async search(query, options) {
    try {
      const payload = {
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: {
          name: "search",
          arguments: {
            informationToGet: query,
            ...options?.maxResults && { max_results: options.maxResults }
          }
        }
      };
      const response = await fetch(`${this.baseUrl}mcp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.apiKey}`,
          "Accept": "application/json, text/event-stream"
        },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Supermemory API error (${response.status}): ${errorText}`
        );
      }
      const result = await response.json();
      if (result.error) {
        console.error("MCP search error:", result.error);
        return { results: [] };
      }
      const content = result.result?.content || [];
      const results = content.map((item) => ({
        content: item.text || item.content || "",
        score: 1,
        metadata: item.metadata || {}
      }));
      return { results };
    } catch (error) {
      console.error("Supermemory search error:", error);
      return { results: [] };
    }
  }
  /**
   * Store transcription in Supermemory
   * @param transcription - Transcription text
   * @param metadata - Additional metadata
   * @returns Response with success status
   */
  async storeTranscription(transcription, metadata) {
    return this.addMemory({
      text: transcription,
      metadata: {
        ...metadata,
        type: "transcription",
        createdAt: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
  }
  /**
   * Store audio metadata in Supermemory
   * @param audioInfo - Audio chunk information
   * @returns Response with success status
   */
  async storeAudioMetadata(audioInfo) {
    return this.addMemory({
      text: `Audio chunk ${audioInfo.chunkId} from user ${audioInfo.uid}`,
      metadata: {
        ...audioInfo,
        type: "audio_metadata",
        createdAt: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
  }
  /**
   * Batch store multiple transcriptions
   * @param transcriptions - Array of transcriptions to store
   * @returns Array of responses
   */
  async batchStoreTranscriptions(transcriptions) {
    const promises = transcriptions.map(
      (t) => this.addMemory({ text: t.text, metadata: t.metadata })
    );
    try {
      return await Promise.all(promises);
    } catch (error) {
      console.error("Batch store error:", error);
      throw error;
    }
  }
  /**
   * Get transcription history for a user
   * @param uid - User ID
   * @param maxResults - Maximum number of results
   * @returns Search results with user's transcription history
   */
  async getTranscriptionHistory(uid, maxResults = 50) {
    return this.search(`transcriptions for user ${uid}`, {
      maxResults,
      uid
    });
  }
  /**
   * Store with retry logic
   * @param content - Content to store
   * @param maxRetries - Maximum number of retry attempts
   * @param retryDelay - Delay between retries in milliseconds
   * @returns Response with success status
   */
  async addMemoryWithRetry(content, maxRetries = 3, retryDelay = 1e3) {
    let lastError = null;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const result = await this.addMemory(content);
      if (result.success) {
        return result;
      }
      lastError = result.error || null;
      console.warn(
        `Store attempt ${attempt + 1} failed:`,
        lastError
      );
      if (attempt < maxRetries - 1) {
        await new Promise(
          (resolve) => setTimeout(resolve, retryDelay * Math.pow(2, attempt))
        );
      }
    }
    return {
      success: false,
      error: `Failed to store after ${maxRetries} attempts: ${lastError}`
    };
  }
  /**
   * Create a session summary from multiple transcriptions
   * @param uid - User ID
   * @param sessionId - Session identifier
   * @param startTime - Session start time
   * @param endTime - Session end time
   * @returns Response with session summary ID
   */
  async createSessionSummary(uid, sessionId, startTime, endTime) {
    const transcriptions = await this.search(
      `transcriptions for user ${uid} between ${startTime} and ${endTime}`,
      { uid, maxResults: 100 }
    );
    if (transcriptions.results.length === 0) {
      return {
        success: false,
        error: "No transcriptions found for this session"
      };
    }
    const fullText = transcriptions.results.map((r) => r.content).join(" ");
    return this.addMemory({
      text: fullText,
      metadata: {
        uid,
        sessionId,
        startTime,
        endTime,
        type: "session_summary",
        transcriptionCount: transcriptions.results.length,
        createdAt: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
  }
};

// src/handlers/audioWebhook.ts
var AudioWebhookHandler = class {
  static {
    __name(this, "AudioWebhookHandler");
  }
  env;
  groqClient;
  supermemoryClient;
  constructor(env) {
    this.env = env;
    this.groqClient = new GroqClient(env.GROQ_API_KEY);
    this.supermemoryClient = new SupermemoryClient(
      env.SUPERMEMORY_API_KEY,
      env.SUPERMEMORY_BASE_URL
    );
  }
  /**
   * Handle incoming audio webhook from Omi device
   * @param request - Incoming request with audio data
   * @returns Response indicating success or failure
   */
  async handleRequest(request) {
    try {
      const url = new URL(request.url);
      const uid = url.searchParams.get("uid");
      const sampleRateStr = url.searchParams.get("sample_rate");
      if (!uid) {
        return new Response(
          JSON.stringify({ error: "Missing uid parameter" }),
          { status: 400, headers: { "Content-Type": "application/json" } }
        );
      }
      const sampleRate = sampleRateStr ? parseInt(sampleRateStr) : 16e3;
      const audioBytes = await request.arrayBuffer();
      if (!audioBytes || audioBytes.byteLength === 0) {
        return new Response(
          JSON.stringify({ error: "Empty audio data received" }),
          { status: 400, headers: { "Content-Type": "application/json" } }
        );
      }
      console.log(`Received ${audioBytes.byteLength} bytes of audio from user ${uid}`);
      const timestamp = Date.now();
      const chunkId = `${uid}_${timestamp}`;
      const audioChunk = {
        uid,
        chunkId,
        audioData: audioBytes,
        sampleRate,
        timestamp,
        format: "raw"
      };
      await this.storeAudioChunk(audioChunk);
      const wavAudio = AudioConverter.rawToWAV(audioBytes, sampleRate, 1, 16);
      console.log(`Converted audio to WAV format (${wavAudio.byteLength} bytes)`);
      if (!this.groqClient.isAudioValid(wavAudio)) {
        console.warn("Audio chunk too short for transcription");
        return new Response(
          JSON.stringify({
            success: true,
            message: "Audio received but too short for transcription",
            chunkId
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      let transcription;
      try {
        transcription = await this.groqClient.transcribeWithRetry(wavAudio, 3, 1e3);
      } catch (error) {
        console.error("Groq transcription failed:", error);
        return new Response(
          JSON.stringify({
            success: false,
            error: "Failed to transcribe audio",
            message: error instanceof Error ? error.message : "Unknown error",
            chunkId
          }),
          { status: 500, headers: { "Content-Type": "application/json" } }
        );
      }
      console.log(`Transcription completed: "${transcription.text}"`);
      const storeResult = await this.supermemoryClient.storeTranscription(
        transcription.text,
        {
          uid,
          timestamp,
          source: "groq",
          audioChunkId: chunkId,
          transcriptionId: `transcription_${chunkId}`,
          duration: transcription.duration
        }
      );
      if (!storeResult.success) {
        console.error("Failed to store transcription in Supermemory:", storeResult.error);
      }
      const duration = AudioConverter.getAudioDuration(wavAudio);
      await this.supermemoryClient.storeAudioMetadata({
        uid,
        chunkId,
        sampleRate,
        duration,
        timestamp,
        format: "wav"
      });
      return new Response(
        JSON.stringify({
          success: true,
          chunkId,
          transcription: transcription.text,
          duration: transcription.duration,
          language: transcription.language,
          supermemoryId: storeResult.id
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    } catch (error) {
      console.error("Audio webhook error:", error);
      return new Response(
        JSON.stringify({
          error: "Failed to process audio",
          message: error instanceof Error ? error.message : "Unknown error"
        }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }
  }
  /**
   * Store audio chunk in KV storage
   * @param chunk - Audio chunk to store
   */
  async storeAudioChunk(chunk) {
    try {
      const key = `audio:${chunk.uid}:${chunk.chunkId}`;
      const value = JSON.stringify({
        uid: chunk.uid,
        chunkId: chunk.chunkId,
        sampleRate: chunk.sampleRate,
        timestamp: chunk.timestamp,
        format: chunk.format,
        size: chunk.audioData.byteLength
      });
      await this.env.AUDIO_STORE.put(key, value, {
        expirationTtl: 86400
        // 24 hours
      });
      const audioKey = `audio:raw:${chunk.chunkId}`;
      const base64Audio = AudioConverter.arrayBufferToBase64(chunk.audioData);
      await this.env.AUDIO_STORE.put(audioKey, base64Audio, {
        expirationTtl: 86400
        // 24 hours
      });
      console.log(`Stored audio chunk ${chunk.chunkId} in KV`);
    } catch (error) {
      console.error("Failed to store audio chunk in KV:", error);
    }
  }
  /**
   * Retrieve audio chunk from KV storage
   * @param uid - User ID
   * @param chunkId - Chunk ID
   * @returns Audio chunk or null if not found
   */
  async getAudioChunk(uid, chunkId) {
    try {
      const key = `audio:${uid}:${chunkId}`;
      const metadataStr = await this.env.AUDIO_STORE.get(key);
      if (!metadataStr) {
        return null;
      }
      const metadata = JSON.parse(metadataStr);
      const audioKey = `audio:raw:${chunkId}`;
      const base64Audio = await this.env.AUDIO_STORE.get(audioKey);
      if (!base64Audio) {
        return null;
      }
      const audioData = AudioConverter.base64ToArrayBuffer(base64Audio);
      return {
        uid: metadata.uid,
        chunkId: metadata.chunkId,
        audioData,
        sampleRate: metadata.sampleRate,
        timestamp: metadata.timestamp,
        format: metadata.format
      };
    } catch (error) {
      console.error("Failed to retrieve audio chunk from KV:", error);
      return null;
    }
  }
  /**
   * Get recent audio chunks for a user
   * @param uid - User ID
   * @param limit - Maximum number of chunks to retrieve
   * @returns List of chunk IDs
   */
  async getRecentChunks(uid, limit = 10) {
    try {
      const prefix = `audio:${uid}:`;
      const list = await this.env.AUDIO_STORE.list({ prefix, limit });
      return list.keys.map((k) => k.name.replace(prefix, ""));
    } catch (error) {
      console.error("Failed to list audio chunks:", error);
      return [];
    }
  }
};

// src/handlers/transcriptionWebhook.ts
var TranscriptionWebhookHandler = class {
  static {
    __name(this, "TranscriptionWebhookHandler");
  }
  env;
  supermemoryClient;
  constructor(env) {
    this.env = env;
    this.supermemoryClient = new SupermemoryClient(
      env.SUPERMEMORY_API_KEY,
      env.SUPERMEMORY_BASE_URL
    );
  }
  /**
   * Handle incoming transcription webhook from Omi device
   * @param request - Incoming request with transcription data
   * @returns Response indicating success or failure
   */
  async handleRequest(request) {
    try {
      const url = new URL(request.url);
      const uid = url.searchParams.get("uid");
      if (!uid) {
        return new Response(
          JSON.stringify({ error: "Missing uid parameter" }),
          { status: 400, headers: { "Content-Type": "application/json" } }
        );
      }
      const body = await request.json();
      console.log("Received transcription webhook:", JSON.stringify(body, null, 2));
      const timestamp = Date.now();
      const sessionId = body.session_id || `session_${uid}_${timestamp}`;
      if (body.segments && body.segments.length > 0) {
        const results = await this.processSegments(uid, body.segments, sessionId, timestamp);
        return new Response(
          JSON.stringify({
            success: true,
            message: "Segmented transcription processed",
            segmentCount: body.segments.length,
            storedCount: results.filter((r) => r.success).length,
            sessionId
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      if (body.transcript) {
        const result = await this.processSingleTranscript(uid, body.transcript, sessionId, timestamp);
        return new Response(
          JSON.stringify({
            success: result.success,
            message: "Transcription stored",
            supermemoryId: result.id,
            sessionId
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      return new Response(
        JSON.stringify({ error: "No transcription data found in request" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    } catch (error) {
      console.error("Transcription webhook error:", error);
      return new Response(
        JSON.stringify({
          error: "Failed to process transcription",
          message: error instanceof Error ? error.message : "Unknown error"
        }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }
  }
  /**
   * Process segmented transcriptions
   * @param uid - User ID
   * @param segments - Array of transcription segments
   * @param sessionId - Session identifier
   * @param timestamp - Request timestamp
   * @returns Array of storage results
   */
  async processSegments(uid, segments, sessionId, timestamp) {
    const results = [];
    for (let i = 0; i < segments.length; i++) {
      const segment = segments[i];
      const transcriptionId = `transcription_${sessionId}_${i}`;
      const entry = {
        uid,
        transcriptionId,
        text: segment.text,
        timestamp,
        source: "omi"
      };
      await this.storeTranscriptionEntry(entry);
      const result = await this.supermemoryClient.storeTranscription(
        segment.text,
        {
          uid,
          timestamp,
          source: "omi",
          transcriptionId
        }
      );
      const metadata = {
        sessionId,
        segmentIndex: i,
        totalSegments: segments.length
      };
      if (segment.speaker) metadata.speaker = segment.speaker;
      if (segment.speaker_id !== void 0) metadata.speakerId = segment.speaker_id;
      if (segment.is_user !== void 0) metadata.isUser = segment.is_user;
      if (segment.start !== void 0) metadata.startTime = segment.start;
      if (segment.end !== void 0) metadata.endTime = segment.end;
      const enhancedResult = await this.supermemoryClient.addMemory({
        text: `[Segment ${i + 1}/${segments.length}] ${segment.text}`,
        metadata
      });
      results.push(enhancedResult);
      console.log(`Stored segment ${i + 1}/${segments.length}: "${segment.text}"`);
    }
    const fullTranscript = segments.map((s) => s.text).join(" ");
    await this.supermemoryClient.addMemory({
      text: fullTranscript,
      metadata: {
        uid,
        sessionId,
        timestamp,
        source: "omi",
        type: "full_session_transcript",
        segmentCount: segments.length
      }
    });
    return results;
  }
  /**
   * Process single transcript
   * @param uid - User ID
   * @param transcript - Transcription text
   * @param sessionId - Session identifier
   * @param timestamp - Request timestamp
   * @returns Storage result
   */
  async processSingleTranscript(uid, transcript, sessionId, timestamp) {
    const transcriptionId = `transcription_${sessionId}`;
    const entry = {
      uid,
      transcriptionId,
      text: transcript,
      timestamp,
      source: "omi"
    };
    await this.storeTranscriptionEntry(entry);
    return this.supermemoryClient.storeTranscription(
      transcript,
      {
        uid,
        timestamp,
        source: "omi",
        transcriptionId
      }
    );
  }
  /**
   * Store transcription entry in KV storage
   * @param entry - Transcription entry to store
   */
  async storeTranscriptionEntry(entry) {
    try {
      const key = `transcription:${entry.uid}:${entry.transcriptionId}`;
      const value = JSON.stringify(entry);
      await this.env.TRANSCRIPTION_STORE.put(key, value, {
        expirationTtl: 604800
        // 7 days
      });
      console.log(`Stored transcription ${entry.transcriptionId} in KV`);
    } catch (error) {
      console.error("Failed to store transcription in KV:", error);
    }
  }
  /**
   * Retrieve transcription entry from KV storage
   * @param uid - User ID
   * @param transcriptionId - Transcription ID
   * @returns Transcription entry or null if not found
   */
  async getTranscriptionEntry(uid, transcriptionId) {
    try {
      const key = `transcription:${uid}:${transcriptionId}`;
      const value = await this.env.TRANSCRIPTION_STORE.get(key);
      if (!value) {
        return null;
      }
      return JSON.parse(value);
    } catch (error) {
      console.error("Failed to retrieve transcription from KV:", error);
      return null;
    }
  }
  /**
   * Get recent transcriptions for a user
   * @param uid - User ID
   * @param limit - Maximum number of transcriptions to retrieve
   * @returns List of transcription entries
   */
  async getRecentTranscriptions(uid, limit = 20) {
    try {
      const prefix = `transcription:${uid}:`;
      const list = await this.env.TRANSCRIPTION_STORE.list({ prefix, limit });
      const entries = [];
      for (const key of list.keys) {
        const value = await this.env.TRANSCRIPTION_STORE.get(key.name);
        if (value) {
          entries.push(JSON.parse(value));
        }
      }
      return entries.sort((a, b) => b.timestamp - a.timestamp);
    } catch (error) {
      console.error("Failed to list transcriptions:", error);
      return [];
    }
  }
  /**
   * Delete old transcriptions for a user
   * @param uid - User ID
   * @param olderThan - Delete transcriptions older than this timestamp
   * @returns Number of deleted transcriptions
   */
  async cleanupOldTranscriptions(uid, olderThan) {
    try {
      const prefix = `transcription:${uid}:`;
      const list = await this.env.TRANSCRIPTION_STORE.list({ prefix });
      let deletedCount = 0;
      for (const key of list.keys) {
        const value = await this.env.TRANSCRIPTION_STORE.get(key.name);
        if (value) {
          const entry = JSON.parse(value);
          if (entry.timestamp < olderThan) {
            await this.env.TRANSCRIPTION_STORE.delete(key.name);
            deletedCount++;
          }
        }
      }
      console.log(`Deleted ${deletedCount} old transcriptions for user ${uid}`);
      return deletedCount;
    } catch (error) {
      console.error("Failed to cleanup old transcriptions:", error);
      return 0;
    }
  }
};

// src/index.ts
var src_default = {
  async fetch(request, env) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders
      });
    }
    try {
      const url = new URL(request.url);
      const path = url.pathname;
      switch (path) {
        case "/webhook/audio":
          return await handleAudioWebhook(request, env, corsHeaders);
        case "/webhook/transcription":
          return await handleTranscriptionWebhook(request, env, corsHeaders);
        case "/health":
          return handleHealthCheck(corsHeaders);
        case "/":
          return handleRoot(corsHeaders);
        default:
          return new Response(
            JSON.stringify({
              error: "Not Found",
              message: "The requested endpoint does not exist",
              availableEndpoints: [
                "/webhook/audio",
                "/webhook/transcription",
                "/health"
              ]
            }),
            {
              status: 404,
              headers: {
                ...corsHeaders,
                "Content-Type": "application/json"
              }
            }
          );
      }
    } catch (error) {
      console.error("Worker error:", error);
      return new Response(
        JSON.stringify({
          error: "Internal Server Error",
          message: error instanceof Error ? error.message : "Unknown error"
        }),
        {
          status: 500,
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json"
          }
        }
      );
    }
  }
};
async function handleAudioWebhook(request, env, corsHeaders) {
  if (request.method !== "POST") {
    return new Response(
      JSON.stringify({ error: "Method not allowed. Use POST." }),
      {
        status: 405,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  if (!env.GROQ_API_KEY || !env.SUPERMEMORY_API_KEY) {
    return new Response(
      JSON.stringify({
        error: "Configuration Error",
        message: "Missing required API keys. Please configure GROQ_API_KEY and SUPERMEMORY_API_KEY."
      }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  const handler = new AudioWebhookHandler(env);
  const response = await handler.handleRequest(request);
  const newHeaders = new Headers(response.headers);
  Object.entries(corsHeaders).forEach(([key, value]) => {
    newHeaders.set(key, value);
  });
  return new Response(response.body, {
    status: response.status,
    headers: newHeaders
  });
}
__name(handleAudioWebhook, "handleAudioWebhook");
async function handleTranscriptionWebhook(request, env, corsHeaders) {
  if (request.method !== "POST") {
    return new Response(
      JSON.stringify({ error: "Method not allowed. Use POST." }),
      {
        status: 405,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  if (!env.SUPERMEMORY_API_KEY) {
    return new Response(
      JSON.stringify({
        error: "Configuration Error",
        message: "Missing required API key. Please configure SUPERMEMORY_API_KEY."
      }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json"
        }
      }
    );
  }
  const handler = new TranscriptionWebhookHandler(env);
  const response = await handler.handleRequest(request);
  const newHeaders = new Headers(response.headers);
  Object.entries(corsHeaders).forEach(([key, value]) => {
    newHeaders.set(key, value);
  });
  return new Response(response.body, {
    status: response.status,
    headers: newHeaders
  });
}
__name(handleTranscriptionWebhook, "handleTranscriptionWebhook");
function handleHealthCheck(corsHeaders) {
  return new Response(
    JSON.stringify({
      status: "healthy",
      service: "never-be-alone-webhook-server",
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      endpoints: {
        audio: "/webhook/audio",
        transcription: "/webhook/transcription"
      }
    }),
    {
      status: 200,
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json"
      }
    }
  );
}
__name(handleHealthCheck, "handleHealthCheck");
function handleRoot(corsHeaders) {
  return new Response(
    JSON.stringify({
      name: "Never Be Alone - Webhook Server",
      version: "1.0.0",
      description: "Cloudflare Workers webhook server for Omi wearable audio streaming and transcription",
      endpoints: [
        {
          path: "/webhook/audio",
          method: "POST",
          description: "Receive audio bytes from Omi device, convert to WAV, transcribe with Groq Whisper, and store in Supermemory",
          parameters: {
            query: {
              uid: "User ID (required)",
              sample_rate: "Audio sample rate in Hz (default: 16000)"
            },
            body: "Raw audio bytes (application/octet-stream)"
          }
        },
        {
          path: "/webhook/transcription",
          method: "POST",
          description: "Receive pre-transcribed text from Omi device and store in Supermemory",
          parameters: {
            query: {
              uid: "User ID (required)"
            },
            body: {
              segments: "Array of transcription segments (optional)",
              transcript: "Full transcript text (optional)",
              session_id: "Session identifier (optional)"
            }
          }
        },
        {
          path: "/health",
          method: "GET",
          description: "Health check endpoint"
        }
      ],
      documentation: "https://github.com/Parth0248/never-be-alone"
    }),
    {
      status: 200,
      headers: {
        ...corsHeaders,
        "Content-Type": "application/json"
      }
    }
  );
}
__name(handleRoot, "handleRoot");

// C:/Users/parth/AppData/Roaming/npm/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// C:/Users/parth/AppData/Roaming/npm/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    return Response.json(error, {
      status: 500,
      headers: { "MF-Experimental-Error-Stack": "true" }
    });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-s82w7f/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = src_default;

// C:/Users/parth/AppData/Roaming/npm/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-s82w7f/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
