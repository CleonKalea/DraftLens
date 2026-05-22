import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// API interfaces
export interface UploadDocumentResponse {
    id: number;
    filename: string;
    file_path: string;
    vectorized: number;
    status: string;
    created_at: Date
}

export interface ChatRequest {
    document_id: number;
    question: string;
}

export interface ChatResponse {
    answer: string;
}

// API Endpoints
export const documentService = {
    // 1. Upload Document (Multipart/Form-Data)
    upload: async (file: File): Promise<UploadDocumentResponse> => {

    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post<UploadDocumentResponse>("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });

        return response.data;
    },

  // 2. Fetch All Documents
    getAll: async (): Promise<UploadDocumentResponse[]> => {
        const response = await apiClient.get<UploadDocumentResponse[]>("/documents");
    return response.data;
    },
};

export const chatService = {
    sendMessage: async (payload: ChatRequest): Promise<ChatResponse> => {
        const response = await apiClient.post<ChatResponse>("/chat", payload);
        return response.data;
    }
};