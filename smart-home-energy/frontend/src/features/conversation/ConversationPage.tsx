// src/features/conversation/ConversationPage.tsx
import { useState } from 'react';
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChatHistory, Message } from '@/hooks/useChatHistory';
import { postQuery } from '@/api/aiApi';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils'; // cn is a utility from shadcn for merging class names

export default function ConversationPage() {
  const { messages, addMessage } = useChatHistory('chatHistory');
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    addMessage({ role: 'user', content: input });
    setInput('');

    try {
      const response = await postQuery(input);
      addMessage({ role: 'assistant', content: response.summary });
    } catch (error) {
      addMessage({ role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <h2 className="text-3xl font-bold tracking-tight mb-4">Conversational AI</h2>
      <ScrollArea className="flex-grow p-4 border rounded-lg">
        <div className="space-y-4">
          {messages.map((message: Message) => (
            <div
              key={message.id}
              className={cn(
                "flex items-start gap-4",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              {message.role === 'assistant' && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback><Bot /></AvatarFallback>
                </Avatar>
              )}
              <div
                className={cn(
                  "rounded-lg p-3 max-w-lg",
                  message.role === 'user'
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <p className="text-sm">{message.content}</p>
              </div>
              {message.role === 'user' && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback><User /></AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex items-start gap-4 justify-start">
               <Avatar className="h-8 w-8"><AvatarFallback><Bot /></AvatarFallback></Avatar>
               <div className="rounded-lg p-3 bg-muted">... thinking</div>
            </div>
          )}
        </div>
      </ScrollArea>
      <form onSubmit={handleSubmit} className="flex items-center gap-4 pt-4">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your energy usage..."
          className="min-h-[40px] flex-grow"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <Button type="submit" disabled={isLoading}>Send</Button>
      </form>
    </div>
  );
}