// src/hooks/useChatHistory.ts
import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export const useChatHistory = (storageKey: string) => {
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const storedMessages = window.localStorage.getItem(storageKey);
      return storedMessages ? JSON.parse(storedMessages) : [];
    } catch (error) {
      console.error("Error reading from localStorage", error);
      return [];
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(messages));
    } catch (error) {
      console.error("Error writing to localStorage", error);
    }
  }, [messages, storageKey]);

  const addMessage = (message: Omit<Message, 'id'>) => {
    setMessages((prevMessages) => [...prevMessages, { id: uuidv4(), ...message }]);
  };

  return { messages, addMessage };
};