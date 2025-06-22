// src/api/aiApi.ts
import api from '@/lib/axios';

interface QueryResponse {
  summary: string;
  data?: any[];
  sql_query_for_debug?: string;
}

export const postQuery = async (question: string): Promise<QueryResponse> => {
  const response = await api.post<QueryResponse>('/query/', { question });
  return response.data;
};