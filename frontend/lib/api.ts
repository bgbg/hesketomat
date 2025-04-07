import axios from 'axios'

// Log environment variables for debugging
console.log('Environment variables:', {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NODE_ENV: process.env.NODE_ENV
})

// Use a relative URL for API requests in development
const API_BASE_URL = '/api'
console.log('API_BASE_URL:', API_BASE_URL)

export interface Podcast {
  id: number
  title: string
  description: string
  rss_url: string
  image_url: string | null
  homepage_url: string | null
  last_updated: string | null
}

export interface PodcastWithCount extends Podcast {
  episode_count: number
}

export interface Episode {
  id: number
  podcast_id: number
  title: string
  description: string
  url: string
  image_url: string | null
  publish_date: string
}

export interface SearchResult {
  episode: Episode
  matches?: {
    title?: [number, number][]
    description?: [number, number][]
  }
}

export interface ValidateResponse {
  valid: boolean
  podcast?: Podcast
  error?: string
}

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Log the axios instance configuration
console.log('Axios config:', {
  baseURL: api.defaults.baseURL,
  headers: api.defaults.headers
})

// Add response interceptor to extract data and handle errors
api.interceptors.response.use(
  response => {
    console.log('API Response:', {
      url: response.config.url,
      method: response.config.method,
      status: response.status,
      data: response.data
    })
    return response.data
  },
  error => {
    // Create a detailed error object for logging
    const errorDetails = {
      message: error.message,
      code: error.code,
      name: error.name,
      stack: error.stack,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        baseURL: error.config?.baseURL,
        headers: error.config?.headers,
        data: error.config?.data,
      },
      response: error.response ? {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers,
      } : null
    }

    console.error('API Error:', JSON.stringify(errorDetails, null, 2))

    // If we have a response from the server, use its error message
    if (error.response?.data?.detail) {
      return Promise.reject(new Error(error.response.data.detail))
    }

    // If we have a network error, make it more user-friendly
    if (error.message === 'Network Error' || error.code === 'ECONNREFUSED') {
      return Promise.reject(new Error('לא ניתן להתחבר לשרת. אנא בדוק את החיבור לאינטרנט ונסה שוב.'))
    }

    // For any other error, use the error message or a generic one
    return Promise.reject(new Error(error.message || 'שגיאה לא צפויה. אנא נסה שוב.'))
  }
)

export { api }

export type ApiResponse<T> = T

export const podcastsApi = {
  getAll: async (): Promise<ApiResponse<Podcast[]>> => {
    try {
      return await api.get('/podcasts')
    } catch (error) {
      console.error('Error in podcastsApi.getAll:', error)
      throw error
    }
  },
  getAllWithCounts: async (): Promise<ApiResponse<PodcastWithCount[]>> => {
    try {
      return await api.get('/podcasts/with_counts')
    } catch (error) {
      console.error('Error in podcastsApi.getAllWithCounts:', error)
      throw error
    }
  },
  validate: async (rssUrl: string): Promise<ApiResponse<ValidateResponse>> => {
    try {
      return await api.post('/podcasts/validate', { rss_url: rssUrl })
    } catch (error) {
      console.error('Error in podcastsApi.validate:', error)
      throw error
    }
  },
  add: async (podcast: Omit<Podcast, 'id' | 'last_updated'>): Promise<ApiResponse<Podcast>> => {
    try {
      return await api.post('/podcasts', podcast)
    } catch (error) {
      console.error('Error in podcastsApi.add:', error)
      throw error
    }
  },
  refresh: async (id: number): Promise<void> => {
    try {
      return await api.post(`/podcasts/${id}/refresh`)
    } catch (error) {
      console.error('Error in podcastsApi.refresh:', error)
      throw error
    }
  },
  delete: async (id: number): Promise<void> => {
    try {
      return await api.delete(`/podcasts/${id}`)
    } catch (error) {
      console.error('Error in podcastsApi.delete:', error)
      throw error
    }
  }
}

export const episodesApi = {
  search: async (
    query: string,
    podcast_ids: number[],
    weights: { title_weight: number; description_weight: number }
  ): Promise<ApiResponse<SearchResult[]>> => {
    try {
      return await api.post('/episodes/search', {
        query,
        podcast_ids,
        title_weight: weights.title_weight,
        description_weight: weights.description_weight,
        cap_n_matches: 10
      })
    } catch (error) {
      console.error('Error in episodesApi.search:', error)
      throw error
    }
  },
  delete: async (podcast_ids: number[]): Promise<void> => {
    try {
      return await api.post('/episodes/delete', podcast_ids)
    } catch (error) {
      console.error('Error in episodesApi.delete:', error)
      throw error
    }
  }
}