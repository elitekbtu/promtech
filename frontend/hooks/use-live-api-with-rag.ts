/**
 * useLiveAPIWithRAG Hook
 * 
 * Extends the useLiveAPI hook with RAG (Retrieval-Augmented Generation) capabilities.
 * This hook integrates with the backend RAG system to provide:
 * - Vector search (company knowledge base)
 * - Web search (real-time information)
 * - Multi-agent coordination
 */

import { useCallback, useEffect, useState, useRef } from "react";
import { useLiveAPI, UseLiveAPIResults } from "./use-live-api";
import { LiveClientOptions } from "../lib/types";
import { LiveConnectConfig, LiveServerToolCall } from "@google/genai";
import { config } from "../lib/config";

export interface UseLiveAPIWithRAGResults extends UseLiveAPIResults {
  ragToolsEnabled: boolean;
  ragToolsHealthy: boolean;
  setRAGToolsEnabled: (enabled: boolean) => void;
}

// Types for backend API
interface LiveQueryRequest {
  query: string;
  context: {
    tool_name: string;
    session_id?: string;
  };
}

interface LiveQueryResponse {
  response: string;
}

/**
 * Enhanced useLiveAPI hook with RAG tools integration
 */
export function useLiveAPIWithRAG(options: LiveClientOptions): UseLiveAPIWithRAGResults {
  const liveAPI = useLiveAPI(options);
  const [ragToolsEnabled, setRAGToolsEnabled] = useState(true);
  const [ragToolsHealthy, setRAGToolsHealthy] = useState(false);
  const lastConfigRef = useRef<string | null>(null);
  const sessionIdRef = useRef<string>(Date.now().toString());

  // Check RAG tools health on mount and periodically
  useEffect(() => {
    let healthCheckInterval: ReturnType<typeof setInterval> | null = null;

    const checkRAGHealth = async () => {
      try {
        const response = await fetch(
          `${config.backendURL}${config.endpoints.rag.live.supervisorStatus}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          const isHealthy = data.status === 'operational' && 
                          data.supervisor_agent?.initialized === true;
          setRAGToolsHealthy(isHealthy);
          console.log('[RAG] Health check:', isHealthy ? '✅ Healthy' : '⚠️ Unhealthy');
        } else {
          setRAGToolsHealthy(false);
          console.warn('[RAG] Health check failed:', response.status);
        }
      } catch (error) {
        setRAGToolsHealthy(false);
        console.error('[RAG] Health check error:', error);
      }
    };

    // Initial health check
    checkRAGHealth();

    // Check health every 30 seconds
    healthCheckInterval = setInterval(checkRAGHealth, 30000);

    return () => {
      if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
      }
    };
  }, []);

  // Enhanced setConfig that adds RAG tool declarations
  const setConfigWithRAG = useCallback((newConfig: LiveConnectConfig) => {
    // Create a stable config string to prevent infinite loops
    const configString = JSON.stringify(newConfig);
    
    if (lastConfigRef.current === configString) {
      return;
    }
    
    lastConfigRef.current = configString;

    if (ragToolsEnabled && ragToolsHealthy) {
      // Add RAG function declarations to the config
      const ragConfig: LiveConnectConfig = {
        ...newConfig,
        tools: [
          {
            functionDeclarations: [
              {
                name: "vector_search",
                description: "Search the GidroAtlas knowledge base for water resources, hydrotechnical structures, object passports, and technical specifications. Use this for questions about water resources, objects, passports, or system functionality.",
                parameters: {
                  type: "object" as any,
                  properties: {
                    query: {
                      type: "string" as any,
                      description: "The search query to find relevant information from GidroAtlas knowledge base"
                    }
                  },
                  required: ["query"]
                }
              },
              {
                name: "web_search",
                description: "Search the web for current information, news, and general knowledge. Use this only if the knowledge base doesn't provide sufficient information, or for clearly external topics not in the GidroAtlas knowledge base.",
                parameters: {
                  type: "object" as any,
                  properties: {
                    query: {
                      type: "string" as any,
                      description: "The search query to find information on the web"
                    }
                  },
                  required: ["query"]
                }
              }
            ]
          }
        ]
      };
      liveAPI.setConfig(ragConfig);
      console.log('[RAG] ✅ Config updated with RAG tools');
    } else {
      liveAPI.setConfig(newConfig);
      console.log('[RAG] ⚠️ Config updated without RAG tools');
    }
  }, [liveAPI, ragToolsEnabled, ragToolsHealthy]);

  // Handle tool calls from Gemini
  useEffect(() => {
    const onToolCall = async (toolCall: LiveServerToolCall) => {
      if (!ragToolsEnabled || !ragToolsHealthy) {
        console.warn('[RAG] ⚠️ Tool call received but RAG tools are disabled/unhealthy');
        return;
      }

      const functionCalls = toolCall.functionCalls || [];
      if (functionCalls.length === 0) {
        return;
      }

      console.log('[RAG] 🔧 Processing', functionCalls.length, 'tool call(s)');

      const functionResponses = [];

      for (const fc of functionCalls) {
        const { name, args, id } = fc;
        
        // Validate tool call
        if (!name || !args || typeof args.query !== 'string' || !args.query.trim()) {
          console.warn('[RAG] ⚠️ Invalid tool call:', { name, hasQuery: !!args?.query });
          functionResponses.push({
            id,
            name: name || 'unknown',
            response: {
              error: 'Invalid tool call: missing or empty query parameter'
            }
          });
          continue;
        }

        // Validate tool name
        if (name !== 'vector_search' && name !== 'web_search') {
          console.warn('[RAG] ⚠️ Unknown tool:', name);
          functionResponses.push({
            id,
            name,
            response: {
              error: `Unknown tool: ${name}. Supported tools: vector_search, web_search`
            }
          });
          continue;
        }

        const query = args.query.trim();
        console.log(`[RAG] 🔍 Executing ${name}:`, query);

        try {
          // Call backend RAG API
          const requestBody: LiveQueryRequest = {
            query,
            context: {
              tool_name: name,
              session_id: sessionIdRef.current,
            }
          };

          const response = await fetch(
            `${config.backendURL}${config.endpoints.rag.live.query}`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(requestBody),
            }
          );

          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
          }

          const data: LiveQueryResponse = await response.json();
          console.log(`[RAG] ✅ ${name} completed`);

          // Format response for Gemini - only return the response text
          functionResponses.push({
            id,
            name,
            response: {
              result: data.response
            }
          });
        } catch (error) {
          console.error(`[RAG] ❌ ${name} failed:`, error);
          functionResponses.push({
            id,
            name,
            response: {
              error: error instanceof Error ? error.message : `Failed to execute ${name}`
            }
          });
        }
      }

      // Send all tool responses back to Gemini
      if (functionResponses.length > 0) {
        liveAPI.client.sendToolResponse({ functionResponses });
        console.log('[RAG] 📤 Sent', functionResponses.length, 'tool response(s)');
      }
    };

    // Listen for tool calls
    liveAPI.client.on('toolcall', onToolCall);

    return () => {
      liveAPI.client.off('toolcall', onToolCall);
    };
  }, [liveAPI.client, ragToolsEnabled, ragToolsHealthy]);

  return {
    ...liveAPI,
    setConfig: setConfigWithRAG,
    ragToolsEnabled,
    ragToolsHealthy,
    setRAGToolsEnabled,
  };
}
